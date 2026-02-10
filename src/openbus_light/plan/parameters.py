from datetime import timedelta
from typing import Collection, NamedTuple

from openbus_light.model.scenario import Scenario

from ..model import LineFrequency
from ..model.type import CHF, CHFPerHour, LineNr, Meter, MeterPerSecond


class DemandParameters(NamedTuple):
    """
    Parameters for loading demand data and associating it to stations.

    :param demand_scaling: float, scaling factor applied to demand values.
        0.0 means no demand, 1.0 means entire daily demand
    :param demand_association_radius: Meter, maximum distance for associating demand to stations
    """

    demand_scaling: float
    demand_association_radius: Meter


class WalkParameters(NamedTuple):
    """
    Parameters for construction of the passenger flow network.

    :param walking_speed_between_stations: MeterPerSecond, assumed walking speed for transfers
    :param maximal_walking_distance: Meter, maximum distance passengers will walk between stations
    """

    walking_speed_between_stations: MeterPerSecond
    maximal_walking_distance: Meter


class LinePlanningParameters(NamedTuple):
    """
    Parameters for the line planning optimization problem.

    :param egress_time_cost: CHFPerHour, value of time spent exiting/alighting
    :param waiting_time_cost: CHFPerHour, value of time spent waiting for service
    :param in_vehicle_time_cost: CHFPerHour, value of time spent traveling on vehicle
    :param walking_time_cost: CHFPerHour, value of time spent walking between stations
    :param period_duration: timedelta, duration of the period
    :param dwell_time_at_terminal: timedelta, time vehicles spend at terminal stations
    :param vehicle_cost_per_period: CHF, cost of operating one vehicle for the period
    :param permitted_frequencies: tuple[LineFrequency, ...],
        the number of vehicles per line in each period. If empty, uses the default
        frequency specified in the bus line definition
    :param maximal_number_of_vehicles: None | int, fleet size constraint (None for unlimited)
    :param solver: str, optimization solver to use ("cbc" or "highspy"), defaults to "cbc"
    """

    egress_time_cost: CHFPerHour
    waiting_time_cost: CHFPerHour
    in_vehicle_time_cost: CHFPerHour
    walking_time_cost: CHFPerHour
    period_duration: timedelta
    dwell_time_at_terminal: timedelta
    vehicle_cost_per_period: CHF
    permitted_frequencies: tuple[LineFrequency, ...]
    maximal_number_of_vehicles: None | int
    solver: str = "cbc"


def get_permitted_frequencies_by_line(
    frequencies: Collection[LineFrequency], scenario: Scenario
) -> dict[LineNr, tuple[LineFrequency, ...]]:
    """
    Create mapping of allowed frequencies for all bus lines in the scenario.

    :param frequencies: Collection[LineFrequency], service frequencies to apply to all lines
    :param scenario: Scenario, transit scenario containing bus lines
    :return: dict[LineNr, tuple[LineFrequency, ...]], mapping from line number to allowed frequencies
        (empty dict if frequencies is empty)
    """
    updated: dict[LineNr, tuple[LineFrequency, ...]] = {}
    if not frequencies:
        return updated
    for line in scenario.bus_lines:
        updated[line.number] = tuple(frequencies)
    return updated
