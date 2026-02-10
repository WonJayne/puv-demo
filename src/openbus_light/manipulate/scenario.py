from __future__ import annotations

from itertools import chain
from typing import Mapping, Sequence

from openbus_light.model.line import update_capacities
from openbus_light.model.scenario import Scenario
from openbus_light.model.type import LineNr, VehicleCapacity
from openbus_light.plan.parameters import DemandParameters

from .demand import load_demand_matrix
from .line import BusLine, LineFactory, load_lines_from_json
from .paths import ScenarioPaths
from .station import Station, load_served_stations


def _drop_stations_that_are_not_served(stations: Sequence[Station], lines: Sequence[BusLine]) -> tuple[Station, ...]:
    """
    Drop stations that are not within the served stations.
    :param stations: Sequence[Station], sequence of Station objects
    :param lines: Sequence[BusLine], sequence of BusLine objects
    :return: tuple[Station, ...], tuple of Stations that are served
    """
    names_of_served_stations = set(
        chain.from_iterable(
            chain.from_iterable((line.direction_up.station_sequence, line.direction_down.station_sequence))
            for line in lines
        )
    )
    return tuple(station for station in stations if station.name in names_of_served_stations)


def load_scenario(parameters: DemandParameters, paths: ScenarioPaths) -> Scenario:
    """
    Load scenario from data files.

    :param parameters: DemandParameters, configuration for demand data processing
    :param paths: ScenarioPaths, file paths to scenario data (lines, stations, demand)
    :return: Scenario, complete scenario with demand matrix, bus lines, and served stations
    """
    line_factory = LineFactory()
    lines = load_lines_from_json(line_factory, paths.to_lines)
    all_stations_in_data = load_served_stations(paths.to_stations, lines)
    served_stations = _drop_stations_that_are_not_served(all_stations_in_data, lines)
    demand_matrix = load_demand_matrix(served_stations, parameters, paths)
    scenario = Scenario(demand_matrix, lines, served_stations)
    scenario.check_consistency()
    return scenario


def update_bus_capacities_in_scenario(scenario: Scenario, capacities: Mapping[LineNr, VehicleCapacity]) -> Scenario:
    """
    Update bus capacities in the scenario's bus lines.

    :param scenario: Scenario, the transit scenario to update
    :param capacities: Mapping[LineNr, VehicleCapacity], mapping from line number to new capacity
    :return: Scenario, updated scenario with new bus capacities applied to bus lines
    """
    updated_bus_lines = update_capacities(scenario.bus_lines, capacities)
    return scenario._replace(bus_lines=updated_bus_lines)
