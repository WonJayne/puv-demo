"""
Week 3 Tests: MILP Formulation & Constraint Implementation

These tests verify the correctness of your capacity and flow conservation constraint implementations.
Run with: pytest test/test_problem.py -v

Tests are organized by:
- Capacity constraints (RIDE and BOARD links)
- Flow conservation constraints (origin, destination, intermediate nodes)
- Integration tests (full problem solving)
"""

from itertools import chain

import pulp as pl
import pytest

from openbus_light.model import Scenario
from openbus_light.model.type import LineNr, StationName, VehicleCapacity
from openbus_light.plan import LinePlanningParameters, LPPData, PassengerFlowNetwork, create_line_planning_problem
from openbus_light.plan.parameters import get_permitted_frequencies_by_line
from openbus_light.plan.problem import _add_capacity_constraints, _add_variables


@pytest.fixture
def lpp_data_with_default_frequencies(
    simple_scenario: Scenario, line_planning_parameters: LinePlanningParameters
) -> LPPData:
    """
    Create LPPData structure for the simple scenario with default frequencies defined in lines. No walking.
    :return: LPPData with network without permitted frequencies
    """
    test_parameters = line_planning_parameters._replace(permitted_frequencies=tuple())
    network = PassengerFlowNetwork.create_from_scenario(simple_scenario, test_parameters.period_duration, tuple())
    permitted_freqs = get_permitted_frequencies_by_line(test_parameters.permitted_frequencies, simple_scenario)
    network.update_board_links_with_frequencies(permitted_freqs, test_parameters.period_duration)
    return LPPData(test_parameters, simple_scenario, network, permitted_freqs)


@pytest.fixture
def lpp_data(simple_scenario: Scenario, line_planning_parameters: LinePlanningParameters) -> LPPData:
    """
    Create LPPData structure for the simple scenario. No walking.
    :return: LPPData with network and permitted frequencies
    """
    network = PassengerFlowNetwork.create_from_scenario(
        simple_scenario, line_planning_parameters.period_duration, tuple()
    )
    permitted_freqs = get_permitted_frequencies_by_line(line_planning_parameters.permitted_frequencies, simple_scenario)
    network.update_board_links_with_frequencies(permitted_freqs, line_planning_parameters.period_duration)
    return LPPData(line_planning_parameters, simple_scenario, network, permitted_freqs)


# ===== Capacity Constraint Tests =====


def test_number_of_capacity_constraints_correct(lpp_data: LPPData) -> None:
    """Test that the correct number of capacity constraints are added."""
    model = pl.LpProblem()
    variables = _add_variables(lpp_data)
    _add_capacity_constraints(model, variables, lpp_data)

    assert len(model.constraints) == "YOUR CALCULATION HERE"


def test_capacity_not_violated(lpp_data_with_default_frequencies: LPPData) -> None:
    """Test that solution respects capacity constraints.

    After solving, verify that passenger flow on each link does not exceed capacity.
    """
    lpp = create_line_planning_problem(lpp_data_with_default_frequencies)
    lpp.solve()
    result = lpp.get_result()

    assert result.success, "Problem should solve successfully"

    # Verify capacity is not violated for any active line
    for line in result.solution.active_lines:
        for direction in (line.direction_up, line.direction_down):
            if direction not in result.solution.passengers_per_link[line]:
                continue
            for pax_per_link in result.solution.passengers_per_link[line][direction]:
                # Each link's passenger count should not exceed capacity
                capacity = line.capacity * line.frequency
                assert pax_per_link.pax <= capacity
                if (
                    line.number == LineNr(1)
                    and pax_per_link.start_station == StationName("C")
                    and pax_per_link.end_station == StationName("D")
                ):
                    assert pax_per_link.pax == capacity, "Link C-D on Line 1 should be at full capacity"


def test_capacity_overutilised(lpp_data_with_default_frequencies: LPPData) -> None:
    """Test that capacity constraints are violated when demand exceeds capacity.

    Modify demand to exceed capacity and verify that the problem becomes infeasible.
    """
    lpp_data = lpp_data_with_default_frequencies
    bus_lines = lpp_data.scenario.bus_lines
    bus_lines = tuple(line._replace(capacity=VehicleCapacity(10)) for line in bus_lines)
    lpp_data = lpp_data._replace(scenario=lpp_data.scenario._replace(bus_lines=bus_lines))

    lpp = create_line_planning_problem(lpp_data)
    lpp.solve()
    result = lpp.get_result()

    assert not result.success, "Problem should be infeasible due to overutilised capacity"


# ===== Flow Conservation Tests =====


def test_flow_balance_at_origin(lpp_data_with_default_frequencies: LPPData) -> None:
    """Test flow conservation at origin nodes.
    The sum of all flows entering the network at origin nodes should equal total demand.
    -
    """
    lpp_data = lpp_data_with_default_frequencies
    lpp = create_line_planning_problem(lpp_data)
    lpp.solve()
    result = lpp.get_result()

    assert result.success, "Problem should solve successfully"

    raise NotImplementedError("TODO Week 3")


def test_flow_balance_at_destination(lpp_data_with_default_frequencies: LPPData) -> None:
    """Test flow conservation at destination nodes.
    The sum of all flows exiting the network at destination nodes should equal total demand.
    """
    lpp_data = lpp_data_with_default_frequencies
    lpp = create_line_planning_problem(lpp_data)
    lpp.solve()
    result = lpp.get_result()

    assert result.success, "Problem should solve successfully"

    raise NotImplementedError("TODO Week 3")


def test_flow_balance_at_intermediate(lpp_data_with_default_frequencies: LPPData) -> None:
    """Test flow conservation at intermediate nodes.
    At intermediate nodes flow just passes through: inflow = outflow.
    """
    lpp_data = lpp_data_with_default_frequencies
    lpp = create_line_planning_problem(lpp_data)
    lpp.solve()
    result = lpp.get_result()

    assert result.success, "Problem should solve successfully"

    raise NotImplementedError("Week 3")


# ===== Integration Tests =====


def test_correct_objective_value(lpp_data: LPPData) -> None:
    """Test that the objective value of the optimization problem is correct based on precomputed solution."""
    lpp = create_line_planning_problem(lpp_data)
    lpp.solve()

    result = lpp.get_result()
    assert result.success, "Problem should solve successfully"

    assert sum(result.solution.generalised_travel_time) == pytest.approx(10, abs=1e-1)
