from itertools import chain
from typing import NamedTuple

from openbus_light.model.demand import DemandMatrix
from openbus_light.model.line import BusLine
from openbus_light.model.station import Station


class Scenario(NamedTuple):
    demand_matrix: DemandMatrix
    bus_lines: tuple[BusLine, ...]
    stations: tuple[Station, ...]

    def check_consistency(self) -> None:
        """
        Check consistency of scenario components.

        Verifies that all stations referenced in bus lines and demand matrix
        are present in the scenario's station list.
        Should call the two helper methods below.

        :raises ValueError: if stations in demand or lines are not in the station list
        """
        all_served_station_names = frozenset(
            chain.from_iterable(
                line.direction_up.station_sequence + line.direction_down.station_sequence for line in self.bus_lines
            )
        )
        self._check_station_and_lines_consistency(all_served_station_names)
        self._check_station_and_demand_consistency(all_served_station_names)

    def _check_station_and_lines_consistency(self, all_served_station_names: frozenset[str]) -> None:
        """
        Check the consistency between stations and lines. If any stations in the Scenario are not served
            at least one line, raise error and vice versa.
        """
        all_station_names = frozenset(station.name for station in self.stations)
        if not all_station_names.issuperset(all_served_station_names):
            unknown_stations = all_served_station_names.difference(all_station_names)
            raise ValueError(
                f"Some bus lines stop at stations that are not defined in the scenario: {unknown_stations}"
            )
        if not all_served_station_names.issuperset(all_station_names):
            not_served_stations = all_station_names.difference(all_served_station_names)
            raise ValueError(f"Some Stations are not served by any line: {not_served_stations}")

    def _check_station_and_demand_consistency(self, all_served_station_names: frozenset[str]) -> None:
        """
        Check the consistency between station and demand. If any stations involved in the demand matrix
            are not within the stations or in the ones served by lines, raise error.
        """
        all_station_names = frozenset(station.name for station in self.stations)
        all_stations_in_demand = set(
            chain.from_iterable(flows_to.keys() for flows_to in self.demand_matrix.matrix.values())
        ) | set(self.demand_matrix.all_origins())
        if not all_station_names.issuperset(all_stations_in_demand):
            unknown_stations = all_stations_in_demand.difference(all_station_names)
            raise ValueError(f"Some Origins or Destinations are not defined in the scenario: {unknown_stations}")
        if not all_served_station_names.issuperset(all_stations_in_demand):
            not_served_stations = all_stations_in_demand.difference(all_served_station_names)
            raise ValueError(f"Some Origins or Destinations are not served by any line: {not_served_stations}")
