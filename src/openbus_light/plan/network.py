from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from enum import unique
from itertools import pairwise
from typing import Collection, NamedTuple

import igraph
from ugraph import (
    BaseLinkType,
    BaseNodeType,
    EndNodeIdPair,
    LinkABC,
    LinkIndex,
    MutableNetworkABC,
    NodeABC,
    NodeId,
    ThreeDCoordinates,
)

from openbus_light.model import (
    BusLine,
    Direction,
    DirectionName,
    LineFrequency,
    LineNr,
    PointIn2D,
    Scenario,
    StationName,
    WalkableDistance,
)


@unique
class Activity(BaseLinkType):
    RIDE = 1
    WALK = 2
    BOARD = 3
    ALIGHT = 4


@dataclass(frozen=True, slots=True)
class PFLink(LinkABC):
    activity: Activity
    duration: timedelta
    line_nr: None | LineNr
    frequency: None | LineFrequency
    link_type: Activity = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "link_type", self.activity)


@unique
class PFNodeType(BaseNodeType):
    SERVICE = 1
    TRANSFER = 2
    ACCESS = 3
    EGRESS = 4


@dataclass(frozen=True, slots=True)
class PFNode(NodeABC[PFNodeType]):
    """Node representation used in the passenger flow network."""

    node_id: NodeId
    coordinates: ThreeDCoordinates
    node_type: PFNodeType
    station_name: StationName
    line_nr: LineNr | None
    direction_name: DirectionName | None


class NodesForOneDirection(NamedTuple):
    access_nodes: tuple[PFNode, ...]
    egress_nodes: tuple[PFNode, ...]
    service_nodes: tuple[PFNode, ...]
    transfer_nodes: tuple[PFNode, ...]


class PassengerFlowNetwork(MutableNetworkABC[PFNode, PFLink, PFNodeType, Activity]):

    def __init__(self, graph: igraph.Graph) -> None:
        MutableNetworkABC.__init__(self, graph)

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Equality comparison is not implemented for PassengerFlowNetwork")

    def __repr__(self) -> str:
        return f"PassengerFlowNetwork(graph=(n:{self.n_count}l:{self.l_count}))"

    def __post_init__(self) -> None:
        """
        Check whether the graph is directed. If not, raise an error.
        :return: None
        """
        if not self.graph.is_directed():
            raise RuntimeError(f"graph of {self} must be directed")

    @property
    def shallow_copy(self) -> PassengerFlowNetwork:
        """
        Create a shallow copy of PassengerFlowNetwork.
        :return: PassengerFlowNetwork, a copy of the instance
        """
        return PassengerFlowNetwork(self.graph.copy())

    @property
    def graph(self) -> igraph.Graph:
        return self.underlying_digraph

    @property
    def all_links(self) -> list[PFLink]:
        return super().all_links

    @property
    def all_nodes(self) -> list[PFNode]:
        return super().all_nodes

    @property
    def all_node_names(self) -> tuple[NodeId, ...]:
        """
        Get the names of all the nodes.
        :return: tuple[NodeId, ...]
        """
        return tuple(self.node_ids)

    def get_link_index(self, source: NodeId, target: NodeId) -> int:
        """
        Get the index of an edge between two vertices.
        :param source: NodeId, the ID of the start vertex
        :param target: NodeId, the ID of the end vertex
        :return: int, index of the link
        """
        return int(self.link_index_by_source_target(source, target))

    @classmethod
    def create_from_scenario(
        cls, scenario: Scenario, period_duration: timedelta, walkable_distances: tuple[WalkableDistance, ...]
    ) -> PassengerFlowNetwork:
        """
        Create passenger flow network from scenario data.

        :param scenario: Scenario, complete scenario with bus lines and stations
        :param period_duration: timedelta, duration of the planning period for calculating waiting times
        :param walkable_distances: tuple[WalkableDistance, ...], walkable connections between stations
        :return: PassengerFlowNetwork, directed graph network with nodes and links for optimization
        """
        nodes_to_add: set[PFNode] = set()
        links_to_add: list[tuple[tuple[NodeId, NodeId], PFLink]] = []
        lines_with_directions = (
            (line, direction) for line in scenario.bus_lines for direction in (line.direction_up, line.direction_down)
        )
        station_coordinates = {station.name: station.center_position for station in scenario.stations}
        for line, direction in lines_with_directions:
            new_nodes, new_links = cls._create_nodes_and_links_for_direction(
                line, direction, period_duration, station_coordinates
            )
            links_to_add.extend(new_links)
            nodes_to_add.update(new_nodes)

        for walkable_distance in walkable_distances:
            links_to_add.extend(cls._create_links_for_walkable_distance(walkable_distance))

        links_to_add.extend(cls._create_links_for_direct_walking(station_coordinates.keys()))

        return cls._create_underlying_digraph(nodes_to_add, links_to_add)

    def update_board_links_with_frequencies(
        self, permitted_frequencies: Mapping[LineNr, tuple[LineFrequency, ...]], period_duration: timedelta
    ) -> None:
        """
        Update board links by creating copies for each permitted frequency.

        This method removes all BOARD links for the specified lines and replaces
        them with new links for each line-frequency combination. For each combination, the boarding
        link duration is set to half the headway (average waiting time).

        :param permitted_frequencies: Mapping[LineNr, tuple[LineFrequency, ...]], mapping from line numbers
            to allowed service frequencies. If empty, no changes are made.
        :param period_duration: timedelta, total duration of the planning period used to calculate average waiting time
        :return: None
        """

        links_to_add: list[tuple[EndNodeIdPair, PFLink]] = []
        links_to_delete: list[LinkIndex] = []
        for line_nr, frequencies in permitted_frequencies.items():
            board_links = [
                (LinkIndex(i), end_node_id_pair)
                for i, (end_node_id_pair, link) in enumerate(self.link_by_end_node_iterator())
                if link.activity == Activity.BOARD and link.line_nr == line_nr
            ]
            board_end_node_id_pairs = [end_node_id_pair for _, end_node_id_pair in board_links]
            links_to_delete.extend(i for i, _ in board_links)
            for frequency in frequencies:
                average_waiting_time: timedelta = period_duration / frequency * 0.5
                board_link = PFLink(Activity.BOARD, average_waiting_time, line_nr, frequency)
                links_to_add.extend((end_node_id_pair, board_link) for end_node_id_pair in board_end_node_id_pairs)

        self.delete_links(links_to_delete)
        self.add_links(links_to_add)

    @classmethod
    def _create_links_for_walkable_distance(
        cls, walkable_distance: WalkableDistance
    ) -> tuple[tuple[tuple[NodeId, NodeId], PFLink], tuple[tuple[NodeId, NodeId], PFLink]]:
        """
        Create bidirectional walking links in the passenger flow network between stations.

        :param walkable_distance: WalkableDistance, contains the two stations and the walking time between them
        :return: tuple[tuple[tuple[str, str], PFLink], tuple[tuple[str, str], PFLink]], tuple containing two tuples:
            - First tuple: ((source_node_id, target_node_id), PFLink) for direction A→B
            - Second tuple: ((target_node_id, source_node_id), PFLink) for direction B→A

        Hints:
        - Consider which node type needs to be connected for walking between different stations
        - You can get the node ids from the stations names using the {node_type}_node_name_from_station_name functions
        - Walking links are not associated with any line number or frequency
        """
        # TODO Week 2 Part B
        raise NotImplementedError("TODO Week 2")

    @classmethod
    def _create_links_for_direct_walking(
        cls, stations: Collection[StationName]
    ) -> tuple[tuple[tuple[NodeId, NodeId], PFLink], ...]:
        """
        Create links for direct walking between access/egress and transfer nodes at the same station.
        So passengers can walk directly from one station to another without using bus services.

        :param stations: Collection[StationName], the stations to create walking links for
        :return: tuple[tuple[tuple[str, str], PFLink], ...],
            a tuple of the source and target nodes along with the PFLink object for walking links

        Hints:
        - The links should have zero duration
        - Walking links are not associated with any line number or frequency
        """
        # TODO Week 2 Part B
        raise NotImplementedError("TODO Week 2")

    @classmethod
    def _create_nodes_and_links_for_direction(
        cls,
        line: BusLine,
        direction: Direction,
        period_duration: timedelta,
        station_coordinates: Mapping[StationName, PointIn2D],
    ) -> tuple[frozenset[PFNode], tuple[tuple[tuple[NodeId, NodeId], PFLink], ...]]:
        """
        Create nodes and links for the bus line in a specific direction.

        :param line: BusLine
        :param direction: Direction
        :param period_duration: timedelta, duration of the period for calculating average waiting times
        :param station_coordinates: Mapping[StationName, PointIn2D], mapping from station names to their coordinates
        :return: tuple[set[PFNode], tuple[tuple[tuple[str, str], PFLink], ...]],
            a set of all nodes and a tuple of tuples representing the links to be added to the graph

        Hints:
        - Consider the documentation of the _create_nodes_for_direction function
        - Nodes are connected by activities with types as specified in the Activity enum
        - Each activity has a duration
            - The time needed for vehicles to travel between stations is given in direction.trip_times
            - For boarding a line you should consider the average waiting time of a passenger at a station
            - For alighting from a line you can use a duration of `timedelta(seconds=60)`
        - Consider using zip and pairwise from itertools for iterating over station nodes
        - Every station is a transfer station (in the extreme case you could transfer to the same line again
            or go back in the other direction)
        """
        access_nodes, egress_nodes, service_nodes, transfer_nodes = cls._create_nodes_for_direction(
            direction, line, station_coordinates
        )

        # TODO Week 2 Part C
        links_to_add: list[tuple[tuple[NodeId, NodeId], PFLink]] = []
        raise NotImplementedError("TODO Week 2")

        return frozenset(access_nodes + egress_nodes + service_nodes + transfer_nodes), tuple(links_to_add)

    @classmethod
    def _create_nodes_for_direction(
        cls, direction: Direction, line: BusLine, station_coordinates: Mapping[StationName, PointIn2D]
    ) -> NodesForOneDirection:
        """
        Generates four types of station nodes for a specific direction of a bus line.
        - ACCESS node: where passengers enter the network
        - EGRESS node: where passengers leave the network
        - TRANSFER node: represents passengers that transfer at that station
            (potentially to another station)
        - SERVICE node: represents passengers in a bus service at that station
            (this is the only node associated with the line and direction)
        Note: ACCESS, EGRESS, and TRANSFER nodes are shared among all lines serving the station in both directions

        :param direction: Direction
        :param line: BusLine
        :return: tuple[tuple[PFNode, ...], tuple[PFNode, ...], tuple[PFNode, ...], tuple[PFNode, ...]],
            a tuple which contains tuples of 4 types of nodes
        """
        station_names = direction.station_sequence
        access_nodes = tuple(
            PFNode(
                cls.access_node_name_from_station_name(station_name),
                ThreeDCoordinates(station_coordinates[station_name].lat, station_coordinates[station_name].long, 0),
                PFNodeType.ACCESS,
                station_name,
                line_nr=None,
                direction_name=None,
            )
            for station_name in station_names
        )
        egress_nodes = tuple(
            PFNode(
                cls.egress_node_name_from_station_name(station_name),
                ThreeDCoordinates(station_coordinates[station_name].lat, station_coordinates[station_name].long, 0),
                PFNodeType.EGRESS,
                station_name,
                line_nr=None,
                direction_name=None,
            )
            for station_name in station_names
        )
        transfer_nodes = tuple(
            PFNode(
                cls.transfer_node_name_from_station_name(station_name),
                ThreeDCoordinates(station_coordinates[station_name].lat, station_coordinates[station_name].long, 0),
                PFNodeType.TRANSFER,
                station_name,
                line_nr=None,
                direction_name=None,
            )
            for station_name in station_names
        )
        service_nodes = tuple(
            PFNode(
                cls.get_service_node_name(station_name, line, direction),
                ThreeDCoordinates(station_coordinates[station_name].lat, station_coordinates[station_name].long, 0),
                PFNodeType.SERVICE,
                station_name,
                line_nr=line.number,
                direction_name=direction.name,
            )
            for station_name in station_names
        )

        return NodesForOneDirection(access_nodes, egress_nodes, service_nodes, transfer_nodes)

    @classmethod
    def _create_underlying_digraph(
        cls, nodes: Collection[PFNode], links_with_s_t: Collection[tuple[tuple[NodeId, NodeId], PFLink]]
    ) -> PassengerFlowNetwork:
        """
        Create a directed graph based on the nodes and links.
        :param nodes: Collection[PFNode]
        :param links_with_s_t: Collection[tuple[tuple[str, str], PFLink]]
        :return: PassengerFlowNetwork, the underlying digraph as network
        """
        network = cls.create_empty()
        network.add_nodes(nodes)
        pairs = [(EndNodeIdPair(s_t), link) for s_t, link in links_with_s_t]
        network.add_links(pairs)
        return network

    @staticmethod
    def access_node_name_from_station_name(station_name: StationName) -> NodeId:
        """
        Generate the names of access nodes.
        :param station_name: NodeId, station name
        :return: NodeId, name of the node
        """
        return NodeId(f"{PFNodeType.ACCESS.name}${station_name}")

    @staticmethod
    def egress_node_name_from_station_name(station_name: StationName) -> NodeId:
        """
        Generate the names of egress nodes.
        :param station_name: NodeId, station name
        :return: NodeId, name of the node
        """
        return NodeId(f"{PFNodeType.EGRESS.name}${station_name}")

    @staticmethod
    def transfer_node_name_from_station_name(station_name: StationName) -> NodeId:
        """
        Generate the names of transfer nodes.
        :param station_name: NodeId, station name
        :return: NodeId, name of the node
        """
        return NodeId(f"{PFNodeType.TRANSFER.name}${station_name}")

    @staticmethod
    def get_service_node_name(station_name: StationName, line: BusLine, direction: Direction) -> NodeId:
        """
        Generate the node name associated with the bus line (i.e. this service at this station).
        :param station_name: NodeId, station name
        :param line: BusLine
        :param direction: Direction
        :return: NodeId, name of the node
        """
        return NodeId(f"{line.number}-{direction.name}-{station_name}")
