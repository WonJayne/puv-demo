from datetime import timedelta
from itertools import product
from math import ceil

import pytest

from openbus_light.manipulate.walkable_distance import find_all_walkable_distances
from openbus_light.model import (
    CHF,
    BusLine,
    CHFPerHour,
    DemandMatrix,
    Direction,
    LineFrequency,
    LineName,
    LineNr,
    PointIn2D,
    Scenario,
    Station,
    StationName,
    VehicleCapacity,
    WalkableDistance,
)
from openbus_light.model.type import DirectionName
from openbus_light.plan import (
    LinePlanningParameters,
    LPPData,
    LPPResult,
    PassengerFlowNetwork,
    create_line_planning_problem,
)
from openbus_light.plan.network import Activity
from openbus_light.plan.parameters import WalkParameters, get_permitted_frequencies_by_line


def _create_non_walking_scenario() -> Scenario:
    """
    Generate a simple non-walking scenario with fictional stations, bus lines and demand.
    :return: Scenario
    """
    stations = (
        Station(StationName("A"), (PointIn2D(1, 1),), (LineNr(1), LineNr(2)), [], []),
        Station(StationName("B"), (PointIn2D(1, 1),), (LineNr(1),), [], []),
        Station(StationName("C"), (PointIn2D(1, 1),), (LineNr(1),), [], []),
        Station(StationName("D"), (PointIn2D(1, 1),), (LineNr(1), LineNr(2)), [], []),
    )
    bus_lines = (
        BusLine(
            LineNr(1),
            LineName("1"),
            Direction(
                DirectionName("a"),
                (StationName("A"), StationName("B"), StationName("C"), StationName("D")),
                (timedelta(seconds=300), timedelta(seconds=300), timedelta(seconds=300)),
            ),
            Direction(
                DirectionName("b"),
                (StationName("D"), StationName("C"), StationName("B"), StationName("A")),
                (timedelta(seconds=300), timedelta(seconds=300), timedelta(seconds=300)),
            ),
            capacity=VehicleCapacity(100),
            frequency=LineFrequency(1),
        ),
        BusLine(
            LineNr(2),
            LineName("2"),
            Direction(DirectionName("a"), (StationName("A"), StationName("D")), (timedelta(seconds=300),)),
            Direction(DirectionName("b"), (StationName("D"), StationName("A")), (timedelta(seconds=300),)),
            capacity=VehicleCapacity(100),
            frequency=LineFrequency(1),
        ),
    )
    demand = DemandMatrix(
        {
            StationName("A"): {StationName("B"): 100, StationName("C"): 50, StationName("D"): 100},
            StationName("D"): {StationName("A"): 100, StationName("B"): 50, StationName("C"): 100},
        }
    )

    return Scenario(demand, bus_lines, stations)


def _create_only_walking_scenario() -> tuple[Scenario, tuple[WalkableDistance, ...]]:
    """
    Generate a planning scenario where walking is the only available mode.
    :return: Scenario
    """
    stations = (
        Station(StationName("A"), (PointIn2D(1, 1),), (LineNr(1),), [], []),
        Station(StationName("B"), (PointIn2D(1, 1),), (LineNr(1),), [], []),
        Station(StationName("C"), (PointIn2D(1, 1),), (LineNr(1),), [], []),
        Station(StationName("D"), (PointIn2D(1, 1),), (LineNr(1),), [], []),
    )
    bus_lines = (
        BusLine(
            LineNr(0),
            LineName("1"),
            Direction(
                DirectionName("a"),
                (StationName("A"), StationName("B"), StationName("C"), StationName("D")),
                (timedelta(seconds=300), timedelta(seconds=300), timedelta(seconds=300)),
            ),
            Direction(DirectionName("b"), (StationName("D"), StationName("A")), (timedelta(seconds=300),)),
            capacity=VehicleCapacity(100),
            frequency=LineFrequency(1),
        ),
    )
    demand = DemandMatrix({StationName("A"): {StationName("D"): 100}, StationName("D"): {StationName("A"): 100}})
    walkable_distances = tuple(
        WalkableDistance(first_station, second_station, timedelta(seconds=300))
        for first_station, second_station in product(stations, stations)
        if first_station != second_station
    )
    return Scenario(demand, bus_lines, stations), walkable_distances


def _solve_this_lpp(
    parameters: LinePlanningParameters,
    scenario: Scenario,
    walkable_distances: tuple[WalkableDistance, ...],
    keep_line_frequency: bool = False,
) -> LPPResult:
    """
    Create line planning problem based on LPP Data, and solve the problem.
    :param parameters: LinePlanningParameters
    :param scenario: Scenario
    :return: LPPResult, result of the LP Problem
    """
    network = PassengerFlowNetwork.create_from_scenario(scenario, parameters.period_duration, walkable_distances)
    permitted_frequencies = {}
    if not keep_line_frequency:
        permitted_frequencies = get_permitted_frequencies_by_line(parameters.permitted_frequencies, scenario)
        network.update_board_links_with_frequencies(permitted_frequencies, parameters.period_duration)
    planning_data = LPPData(parameters, scenario, network, permitted_frequencies)
    first_lpp = create_line_planning_problem(planning_data)
    first_lpp.solve()
    return first_lpp.get_result()


def _calculate_number_of_vehicles(scenario_with_frequency_1: Scenario, parameters: LinePlanningParameters) -> int:
    """
    Calculate the number of vehicles needed to serve a planning scenario with frequency of 1.
    :param scenario_with_frequency_1: Scenario, where frequency is 1
    :param parameters: LinePlanningParameters
    :return: int, number of vehicles needed to serve in the scenario
    """
    return sum(
        ceil(
            (
                sum(dt.total_seconds() for dt in line.direction_up.trip_times)
                + sum(dt.total_seconds() for dt in line.direction_down.trip_times)
                + 2 * parameters.dwell_time_at_terminal.total_seconds()
            )
            / parameters.period_duration.total_seconds()
            * line.frequency
        )
        for line in scenario_with_frequency_1.bus_lines
    )


def _calculate_total_passenger_count(non_walking_scenario: Scenario) -> float:
    """
    Calculate the total number of passengers (i.e. demand values) in a non-walking scenario.
    :param non_walking_scenario: Scenario
    :return: float, the total passenger demand
    """
    return sum(sum(from_here.values()) for from_here in non_walking_scenario.demand_matrix.matrix.values())


def test_with_walking(line_planning_parameters: LinePlanningParameters) -> None:
    """
    Compare the results of two different scenarios either favoring vehicles or walking.
    Check in line-favored solution, whether the weighted travel time for walking is 0, and vice versa.
    """
    scenario_with_walking = _create_only_walking_scenario()
    parameters_favoring_vehicle = line_planning_parameters._replace(
        waiting_time_cost=0,
        in_vehicle_time_cost=CHFPerHour(1 / 300),
        walking_time_cost=1,
        vehicle_cost_per_period=CHF(0),
    )
    parameters_favoring_walking = line_planning_parameters._replace(
        waiting_time_cost=0,
        in_vehicle_time_cost=1,
        walking_time_cost=CHFPerHour(1 / 300),
        vehicle_cost_per_period=CHF(0),
    )
    walkable_distances = scenario_with_walking[1]
    scenario_with_walking = scenario_with_walking[0]
    result_using_line = _solve_this_lpp(parameters_favoring_vehicle, scenario_with_walking, walkable_distances)
    result_using_walking = _solve_this_lpp(parameters_favoring_walking, scenario_with_walking, walkable_distances)

    assert result_using_line.solution.generalised_travel_time[Activity.WALK] * 3600 == 0
    assert (
        result_using_line.solution.generalised_travel_time[Activity.RIDE] * 3600
        == _calculate_total_passenger_count(scenario_with_walking) * 2
    )

    assert result_using_walking.solution.generalised_travel_time[Activity.BOARD] * 3600 == 0

    assert result_using_walking.solution.generalised_travel_time[
        Activity.WALK
    ] * 3600 == _calculate_total_passenger_count(scenario_with_walking)


def test_with_walking_and_no_vehicles(line_planning_parameters: LinePlanningParameters) -> None:
    """
    Test scenarios where there are no vehicles or vehicles with zero capacity. Assert that under
    these scenarios, optimization should not succeed.
    """
    scenario = _create_non_walking_scenario()
    zero_capacity_scenario = scenario._replace(
        bus_lines=tuple(line._replace(capacity=VehicleCapacity(0)) for line in scenario.bus_lines)
    )
    parameters_with_no_vehicles = line_planning_parameters._replace(maximal_number_of_vehicles=0)

    zero_capacity_result = _solve_this_lpp(line_planning_parameters, zero_capacity_scenario, tuple())
    zero_vehicles_result = _solve_this_lpp(parameters_with_no_vehicles, scenario, tuple())

    assert not zero_capacity_result.success
    assert not zero_vehicles_result.success


def test_zero_frequency_case(line_planning_parameters: LinePlanningParameters) -> None:
    """
    Test scenario where the permitted frequency is 0, and assert that under such scenario,
    ZeroDivisionError is raised.
    """
    non_walking_scenario = _create_non_walking_scenario()
    zero_frequency_scenario = non_walking_scenario._replace(
        bus_lines=tuple(line._replace(frequency=LineFrequency(0)) for line in non_walking_scenario.bus_lines)
    )

    with pytest.raises(ZeroDivisionError):
        _solve_this_lpp(line_planning_parameters, zero_frequency_scenario, tuple())


def test_no_walking_without_walkable_distances(line_planning_parameters: LinePlanningParameters) -> None:
    """
    Test the parameters favoring walking in a non-walking scenario. Assert that no one walks between
     any stations, i.e. the weighted travel time for walking is 0.
    """
    parameters_favoring_walking = line_planning_parameters._replace(
        waiting_time_cost=CHFPerHour(1 / 900),
        in_vehicle_time_cost=CHFPerHour(1 / 300),
        walking_time_cost=CHFPerHour(1 / 1e6),
        vehicle_cost_per_period=CHF(0),
        egress_time_cost=CHFPerHour(1 / 60),
    )
    non_walking_scenario = _create_non_walking_scenario()
    only_walking_weighted_result = _solve_this_lpp(parameters_favoring_walking, non_walking_scenario, tuple())

    assert only_walking_weighted_result.solution.generalised_travel_time[Activity.WALK] == 0
    assert only_walking_weighted_result.solution.generalised_travel_time[
        Activity.ALIGHT
    ] * 3600 == _calculate_total_passenger_count(non_walking_scenario)
    assert round(only_walking_weighted_result.solution.generalised_travel_time[Activity.RIDE] * 3600) == round(
        _calculate_total_passenger_count(non_walking_scenario) + 100
    )
    assert only_walking_weighted_result.solution.generalised_travel_time[
        Activity.BOARD
    ] * 3600 == _calculate_total_passenger_count(non_walking_scenario)


@pytest.fixture
def reduced_baseline_scenario(baseline_scenario: Scenario) -> Scenario:
    """
    Fixture that provides a baseline scenario with reduced demand matrix.
    Remove the demand matrix for origins starting from the 11th position onward.
    """
    all_origins = sorted(baseline_scenario.demand_matrix.all_origins())
    reduced_matrix = {origin: dict(baseline_scenario.demand_matrix.matrix[origin]) for origin in all_origins[:10]}
    reduced_demand_matrix = DemandMatrix(reduced_matrix)
    return baseline_scenario._replace(demand_matrix=reduced_demand_matrix)


def test_frequency_dependence(
    reduced_baseline_scenario: Scenario,
    line_planning_parameters: LinePlanningParameters,
    walk_parameters: WalkParameters,
) -> None:
    """
    Test the changing of frequency has an impact on waiting time.
    """
    scenario_with_frequency_2 = reduced_baseline_scenario._replace(
        bus_lines=tuple(line._replace(frequency=LineFrequency(20)) for line in reduced_baseline_scenario.bus_lines)
    )

    scenario_with_frequency_1 = reduced_baseline_scenario._replace(
        bus_lines=tuple(line._replace(frequency=LineFrequency(10)) for line in reduced_baseline_scenario.bus_lines)
    )

    parameters_only_transfer_weight = line_planning_parameters._replace(
        waiting_time_cost=1,
        in_vehicle_time_cost=0,
        walking_time_cost=0,
        vehicle_cost_per_period=CHF(0),
        egress_time_cost=0,
    )

    walkable_distances = find_all_walkable_distances(reduced_baseline_scenario.stations, walk_parameters)
    result_with_2 = _solve_this_lpp(
        parameters_only_transfer_weight, scenario_with_frequency_2, walkable_distances, True
    )
    result_with_1 = _solve_this_lpp(
        parameters_only_transfer_weight, scenario_with_frequency_1, walkable_distances, True
    )

    assert result_with_2.success
    assert result_with_1.success
    assert (
        result_with_2.solution.generalised_travel_time[Activity.BOARD]
        != result_with_1.solution.generalised_travel_time[Activity.BOARD]
    )
    assert result_with_1.solution.generalised_travel_time[Activity.RIDE] == 0
    assert result_with_2.solution.generalised_travel_time[Activity.RIDE] == 0

    assert (
        pytest.approx(result_with_2.solution.generalised_travel_time[Activity.BOARD] * 2, abs=1e-4)
        == result_with_1.solution.generalised_travel_time[Activity.BOARD]
    )

    assert result_with_2.solution.used_vehicles != result_with_1.solution.used_vehicles
    assert result_with_1.solution.used_vehicles == _calculate_number_of_vehicles(
        scenario_with_frequency_1, line_planning_parameters
    )
    assert result_with_2.solution.used_vehicles == _calculate_number_of_vehicles(
        scenario_with_frequency_2, line_planning_parameters
    )


def test_frequency_independence(
    reduced_baseline_scenario: Scenario,
    line_planning_parameters: LinePlanningParameters,
    walk_parameters: WalkParameters,
) -> None:
    """
    Test that the changing of frequency does not have an impact on in-vehicle time and walking time.
    """
    scenario_with_frequency_2 = reduced_baseline_scenario._replace(
        bus_lines=tuple(line._replace(frequency=LineFrequency(20)) for line in reduced_baseline_scenario.bus_lines)
    )

    scenario_with_frequency_1 = reduced_baseline_scenario._replace(
        bus_lines=tuple(line._replace(frequency=LineFrequency(10)) for line in reduced_baseline_scenario.bus_lines)
    )

    parameters_only_transfer_weight = line_planning_parameters._replace(
        waiting_time_cost=0, in_vehicle_time_cost=1, walking_time_cost=1, vehicle_cost_per_period=CHF(0)
    )

    walkable_distances = find_all_walkable_distances(reduced_baseline_scenario.stations, walk_parameters)
    result_with_2 = _solve_this_lpp(
        parameters_only_transfer_weight, scenario_with_frequency_2, walkable_distances, True
    )
    result_with_1 = _solve_this_lpp(
        parameters_only_transfer_weight, scenario_with_frequency_1, walkable_distances, True
    )

    assert result_with_2.success
    assert result_with_1.success
    assert (
        result_with_2.solution.generalised_travel_time[Activity.BOARD]
        == result_with_1.solution.generalised_travel_time[Activity.BOARD]
    )
    assert result_with_1.solution.generalised_travel_time[Activity.BOARD] == 0
    assert result_with_2.solution.generalised_travel_time[Activity.BOARD] == 0

    assert (
        pytest.approx(result_with_2.solution.generalised_travel_time[Activity.WALK], abs=100)
        == result_with_1.solution.generalised_travel_time[Activity.WALK]
    )
    assert (
        pytest.approx(result_with_2.solution.generalised_travel_time[Activity.RIDE], abs=100)
        == result_with_1.solution.generalised_travel_time[Activity.RIDE]
    )
