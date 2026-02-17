import pytest

from _constants import get_paths
from openbus_light.manipulate.scenario import load_scenario
from openbus_light.model.scenario import Scenario
from openbus_light.model.type import Meter
from openbus_light.plan.parameters import DemandParameters


def test_incoming_equals_outgoing_demand(baseline_scenario: Scenario) -> None:
    """Test that the sum of all incoming demands equals the sum of all outgoing demands.
    Hint:
    - You can use pytest.approx for floating point comparisons"""
    demand_matrix = baseline_scenario.demand_matrix

    # Calculate total outgoing and incoming demand
    total_outgoing = sum(demand_matrix.starting_from(origin) for origin in demand_matrix.all_origins())
    total_incoming = sum(demand_matrix.arriving_at(origin) for origin in demand_matrix.all_origins())

    # Verify conservation of flow
    assert total_outgoing == pytest.approx(total_incoming)


def test_zero_association_radius_no_demand() -> None:
    """Test that with zero demand association radius"""
    params = DemandParameters(demand_association_radius=Meter(0), demand_scaling=1.0)
    scenario = load_scenario(params, get_paths())

    # Calculate total demand
    demand_matrix = scenario.demand_matrix
    total_demand = sum(demand_matrix.starting_from(origin) for origin in demand_matrix.all_origins())

    # Verify that no demand is captured
    assert total_demand == 0.0
