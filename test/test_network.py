"""
Week 2 Tests: Network Construction

These tests verify the correctness of your network construction implementation.
Run with: pytest test/test_network.py -v

Tests are organized by part:
- walkable distances
- walking links
- links for direction
- integration: full network construction
"""

from datetime import timedelta

import pytest

from openbus_light.manipulate.point import calculate_distance_in_m
from openbus_light.manipulate.walkable_distance import find_all_walkable_distances
from openbus_light.model import (
    BusLine,
    DemandMatrix,
    Direction,
    DirectionName,
    LineFrequency,
    LineName,
    LineNr,
    Meter,
    MeterPerSecond,
    PointIn2D,
    Scenario,
    Station,
    StationName,
    VehicleCapacity,
    WalkableDistance,
)
from openbus_light.plan.network import Activity, PassengerFlowNetwork, PFLink, PFNodeType
from openbus_light.plan.parameters import WalkParameters


@pytest.fixture(scope="session")
def simple_scenario() -> Scenario:
    # Stations approximately 100 meters apart
    stations = (
        Station(StationName("A"), (PointIn2D(0, 0),), (LineNr(1), LineNr(2)), [], []),
        Station(StationName("B"), (PointIn2D(0, 1e-3),), (LineNr(1),), [], []),
        Station(StationName("C"), (PointIn2D(0, 2e-3),), (LineNr(1),), [], []),
        Station(StationName("D"), (PointIn2D(0, 4e-3),), (LineNr(1), LineNr(2)), [], []),
    )
    bus_lines = (
        BusLine(
            LineNr(1),
            LineName("1"),
            Direction(
                DirectionName("a"),
                (StationName("A"), StationName("B"), StationName("C"), StationName("D")),
                (timedelta(seconds=100), timedelta(seconds=200), timedelta(seconds=300)),
            ),
            Direction(
                DirectionName("b"),
                (StationName("D"), StationName("C"), StationName("B"), StationName("A")),
                (timedelta(seconds=100), timedelta(seconds=200), timedelta(seconds=300)),
            ),
            capacity=VehicleCapacity(100),
            frequency=LineFrequency(3),
        ),
        BusLine(
            LineNr(2),
            LineName("2"),
            Direction(DirectionName("a"), (StationName("A"), StationName("D")), (timedelta(seconds=200),)),
            Direction(DirectionName("b"), (StationName("D"), StationName("A")), (timedelta(seconds=200),)),
            capacity=VehicleCapacity(100),
            frequency=LineFrequency(2),
        ),
    )

    return Scenario(DemandMatrix({}), bus_lines, stations)


# ===== Test walkable distances =====


def test_walkable_distances_finds_all_distances(simple_scenario: Scenario) -> None:
    """Test that function returns a tuple."""
    stations = simple_scenario.stations
    params = WalkParameters(walking_speed_between_stations=MeterPerSecond(0.6), maximal_walking_distance=Meter(1000))

    result = find_all_walkable_distances(stations, params)
    assert isinstance(result, tuple)
    assert len(result) == 6


def test_walkable_distances_filters_by_max_distance(simple_scenario: Scenario) -> None:
    """Test that only stations within max distance are included."""
    stations = simple_scenario.stations
    params = WalkParameters(walking_speed_between_stations=MeterPerSecond(0.6), maximal_walking_distance=Meter(150))

    result = find_all_walkable_distances(stations, params)

    # Verify all distances respect the threshold
    for wd in result:
        distance = calculate_distance_in_m(wd.station_a.center_position, wd.station_b.center_position)
        assert distance < params.maximal_walking_distance
    assert len(result) == 2


def test_walkable_distances_empty_for_zero_max(simple_scenario: Scenario) -> None:
    """Test that zero max distance results in no connections."""
    stations = simple_scenario.stations
    params = WalkParameters(walking_speed_between_stations=MeterPerSecond(0.6), maximal_walking_distance=Meter(0))

    result = find_all_walkable_distances(stations, params)
    assert len(result) == 0


def test_walkable_distances_calculates_time_correctly() -> None:
    """Test that walking time is calculated correctly from distance and speed."""
    # Create two stations ~300m apart
    stations = (
        Station(StationName("A"), (PointIn2D(0, 0),), (LineNr(1),), [], []),
        Station(StationName("B"), (PointIn2D(0.0027, 0),), (LineNr(1),), [], []),
    )
    params = WalkParameters(walking_speed_between_stations=MeterPerSecond(0.6), maximal_walking_distance=Meter(400))

    result = find_all_walkable_distances(stations, params)

    assert len(result) == 1
    wd = result[0]

    # Distance ≈ 300m, speed = 0.6 m/s → time ≈ 500 seconds
    expected_time_seconds = 500
    actual_time_seconds = wd.walking_time.total_seconds()
    assert actual_time_seconds == pytest.approx(expected_time_seconds, abs=1)  # Allow some tolerance


# ===== Test walking links =====


def test_walking_links_return_type(simple_scenario: Scenario) -> None:
    """Test that function returns a tuple of links."""
    station_a = Station(StationName("A"), (PointIn2D(0, 0),), (LineNr(1),), [], [])
    station_b = Station(StationName("B"), (PointIn2D(100, 100),), (LineNr(1),), [], [])
    walk_dist = WalkableDistance(station_a, station_b, timedelta(minutes=5))

    links = PassengerFlowNetwork._create_links_for_walkable_distance(walk_dist)
    assert isinstance(links, tuple)
    assert len(links) == 2
    for (source, target), link in links:
        assert isinstance(source, str)
        assert isinstance(target, str)
        assert isinstance(link, PFLink)


def test_walking_links_bidirectional() -> None:
    """Test that walking links are created in both directions."""
    station_a = Station(StationName("A"), (PointIn2D(0, 0),), (LineNr(1),), [], [])
    station_b = Station(StationName("B"), (PointIn2D(100, 100),), (LineNr(1),), [], [])
    walk_dist = WalkableDistance(station_a, station_b, timedelta(minutes=5))

    links = PassengerFlowNetwork._create_links_for_walkable_distance(walk_dist)

    (source_1, target_1), _ = links[0]
    (source_2, target_2), _ = links[1]
    assert source_1 == target_2
    assert source_2 == target_1


def test_direct_walking_links_created_for_all_stations() -> None:
    """Test that _create_links_for_direct_walking creates correct links for all stations."""
    stations = [StationName("A"), StationName("B"), StationName("C")]

    links = PassengerFlowNetwork._create_links_for_direct_walking(stations)

    assert len(links) == "YOUR CALCULATION HERE"

    # Verify all links are WALK activity with zero duration
    for (source, target), link in links:
        assert link.activity == Activity.WALK
        assert link.duration == timedelta(seconds=0)
        assert link.line_nr is None
        assert link.frequency is None

    # Verify that each station has correct links created
    expected_links = set()
    for station in stations:
        expected_links.update(["WHICH LINKS SHOULD BE CREATED?"])

    actual_links = {(source, target) for (source, target), _ in links}
    assert actual_links == expected_links


# ===== Test links for direction =====


def test_links_for_direction_return_type(simple_scenario: Scenario) -> None:
    """Test that function returns both nodes and links."""
    line = simple_scenario.bus_lines[0]
    coords = {station.name: station.center_position for station in simple_scenario.stations}

    nodes, links = PassengerFlowNetwork._create_nodes_and_links_for_direction(
        line, line.direction_up, timedelta(hours=1), coords
    )

    assert isinstance(nodes, frozenset)
    assert isinstance(links, tuple)
    for (source, target), link in links:
        assert isinstance(source, str)
        assert isinstance(target, str)
        assert isinstance(link, PFLink)


def test_links_for_direction_node_count(simple_scenario: Scenario) -> None:
    """Test that correct number of nodes are created (4 per station)."""
    line = simple_scenario.bus_lines[0]
    coords = {station.name: station.center_position for station in simple_scenario.stations}

    nodes, _ = PassengerFlowNetwork._create_nodes_and_links_for_direction(
        line, line.direction_up, timedelta(hours=1), coords
    )

    # 4 nodes per station
    assert len(nodes) == len(line.direction_up.station_sequence) * 4


def test_links_for_direction_link_count(simple_scenario: Scenario) -> None:
    """Test that total number of links created is correct.

    Hints:
    - Consider all link types: BOARD, ALIGHT, RIDE
    - How many BOARD links per station? How many ALIGHT links?
    - How many RIDE links connect N stations in sequence?
    """
    line = simple_scenario.bus_lines[0]
    coords = {station.name: station.center_position for station in simple_scenario.stations}

    _, links = PassengerFlowNetwork._create_nodes_and_links_for_direction(
        line, line.direction_up, timedelta(hours=1), coords
    )

    assert len(links) == "YOUR CALCULATION HERE"


def test_links_have_correct_activity_counts(simple_scenario: Scenario) -> None:
    """Test that links are created with correct activity types and counts.

    Hints:
    - Count how many links of each Activity type are created
    - This function creates links for one direction only - no WALK links here
    """
    line = simple_scenario.bus_lines[0]
    coords = {station.name: station.center_position for station in simple_scenario.stations}

    _, links = PassengerFlowNetwork._create_nodes_and_links_for_direction(
        line, line.direction_up, timedelta(hours=1), coords
    )

    activity_counts: dict[Activity, int] = {}
    for _, link in links:
        activity_counts[link.activity] = activity_counts.get(link.activity, 0) + 1

    assert activity_counts[Activity.BOARD] == "YOUR CALCULATION HERE"
    assert activity_counts[Activity.ALIGHT] == "YOUR CALCULATION HERE"
    assert activity_counts[Activity.RIDE] == "YOUR CALCULATION HERE"
    assert activity_counts.get(Activity.WALK, 0) == 0


# ===== Integration tests =====


def test_simple_scenario_network_construction(simple_scenario: Scenario, walk_parameters: WalkParameters) -> None:
    """Integration test: Full network construction with simple scenario.

    This test verifies the complete network by:
    - Checking node counts by type
    - Checking link counts by activity
    - Testing shortest paths through the network
    """
    walk_parameters = walk_parameters._replace(maximal_walking_distance=Meter(150))
    walkable = find_all_walkable_distances(simple_scenario.stations, walk_parameters)
    network = PassengerFlowNetwork.create_from_scenario(simple_scenario, timedelta(hours=1), walkable)

    num_access_nodes = len([n for n in network.all_nodes if n.node_type == PFNodeType.ACCESS])
    num_egress_nodes = len([n for n in network.all_nodes if n.node_type == PFNodeType.EGRESS])
    num_transfer_nodes = len([n for n in network.all_nodes if n.node_type == PFNodeType.TRANSFER])
    num_service_nodes = len([n for n in network.all_nodes if n.node_type == PFNodeType.SERVICE])
    assert network.n_count == num_access_nodes + num_egress_nodes + num_transfer_nodes + num_service_nodes

    assert num_access_nodes == "YOUR CALCULATION HERE"
    assert num_egress_nodes == "YOUR CALCULATION HERE"
    assert num_transfer_nodes == "YOUR CALCULATION HERE"
    assert num_service_nodes == "YOUR CALCULATION HERE"

    board_links = [link for link in network.all_links if link.activity == Activity.BOARD]
    alight_links = [link for link in network.all_links if link.activity == Activity.ALIGHT]
    ride_links = [link for link in network.all_links if link.activity == Activity.RIDE]
    walk_links = [link for link in network.all_links if link.activity == Activity.WALK]
    assert network.l_count == len(board_links) + len(alight_links) + len(ride_links) + len(walk_links)

    assert len(board_links) == "YOUR CALCULATION HERE"
    assert len(alight_links) == "YOUR CALCULATION HERE"
    assert len(ride_links) == "YOUR CALCULATION HERE"
    assert len(walk_links) == 4

    # verify some shortest paths through the network. Shortest paths are based on link durations.
    weights = [link.duration.seconds for link in network.all_links]

    # Example: the shortest path from access station A to egress station D should be direct via line 2
    access_node = PassengerFlowNetwork.access_node_name_from_station_name(simple_scenario.stations[0].name)
    egress_node = PassengerFlowNetwork.egress_node_name_from_station_name(simple_scenario.stations[-1].name)
    path = network.underlying_digraph.get_shortest_paths(access_node, to=egress_node, weights=weights)[0]
    path = [network.node_id_by_index(idx) for idx in path]
    assert path == [
        access_node,
        PassengerFlowNetwork.get_service_node_name(
            StationName("A"), simple_scenario.bus_lines[1], simple_scenario.bus_lines[1].direction_up
        ),
        PassengerFlowNetwork.get_service_node_name(
            StationName("D"), simple_scenario.bus_lines[1], simple_scenario.bus_lines[1].direction_up
        ),
        egress_node,
    ]

    # TODO: create a path that requires a transfer and verify
    raise NotImplementedError("Week 2")

    # TODO: create a path that is only walking and verify
    raise NotImplementedError("Week 2")
