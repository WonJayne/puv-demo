from copy import copy
from datetime import timedelta

import pytest

from openbus_light.model import Direction, PointIn2D, Scenario, Station, StationName, WalkableDistance
from openbus_light.model.walkable_distance import check_station_and_walk_consistency
from openbus_light.plan.parameters import DemandParameters


def test_consistency_ok(baseline_scenario: Scenario) -> None:
    """Check the consistency of the scenario."""
    assert baseline_scenario.check_consistency() is None


def test_non_served_stop_fails(baseline_scenario: Scenario) -> None:
    """Test that a non-served stop in this scenario raises ValueError."""
    scenario_with_only_one_line = baseline_scenario._replace(bus_lines=(baseline_scenario.bus_lines[0],))

    with pytest.raises(ValueError):
        scenario_with_only_one_line.check_consistency()


def test_non_served_demand_fails(baseline_scenario: Scenario) -> None:
    """Test that demand for a non-served stop raises ValueError."""
    invalid_scenario = copy(baseline_scenario)
    invalid_scenario.demand_matrix.matrix[invalid_scenario.demand_matrix.all_origins()[0]][StationName("DUMMY$$")] = 123  # type: ignore

    with pytest.raises(ValueError):
        invalid_scenario.check_consistency()


def test_non_served_walk_fails(baseline_scenario: Scenario) -> None:
    """Test that if a walkable distance starts or ends at a non-served stop, ValueError is raised."""
    dummy_station = Station(StationName("S"), (PointIn2D(1, 1),), tuple(), [], [])
    dummy_distances = WalkableDistance(dummy_station, dummy_station, timedelta(seconds=0))

    with pytest.raises(ValueError):
        check_station_and_walk_consistency(baseline_scenario.stations, (dummy_distances,))


def test_line_with_unknown_station_fails(baseline_scenario: Scenario) -> None:
    """Bus lines referencing stations not defined in the scenario should fail."""
    line = baseline_scenario.bus_lines[0]
    new_station = StationName("UNKNOWN$$")
    new_direction = Direction(
        line.direction_up.name,
        line.direction_up.station_sequence + (new_station,),
        line.direction_up.trip_times + (timedelta(seconds=60),),
        line.direction_up.recorded_trips,
    )
    modified_line = line._replace(direction_up=new_direction)
    invalid_scenario = baseline_scenario._replace(bus_lines=(modified_line,) + baseline_scenario.bus_lines[1:])

    with pytest.raises(ValueError):
        invalid_scenario.check_consistency()


def test_nonexistent_origin_demand_fails(baseline_scenario: Scenario) -> None:
    """Demand matrix containing unknown origins should fail."""
    invalid_scenario = copy(baseline_scenario)
    invalid_scenario.demand_matrix.matrix[StationName("ORIGIN$$")] = {invalid_scenario.stations[0].name: 42.0}  # type: ignore

    with pytest.raises(ValueError):
        invalid_scenario.check_consistency()


def test_walk_distance_with_unknown_start_fails(baseline_scenario: Scenario) -> None:
    """Walkable distances using undefined stations should fail."""
    valid_station = baseline_scenario.stations[0]
    dummy_station = Station(StationName("X"), (PointIn2D(0, 0),), tuple(), [], [])
    walk = WalkableDistance(dummy_station, valid_station, timedelta(seconds=0))

    with pytest.raises(ValueError):
        check_station_and_walk_consistency(baseline_scenario.stations, (walk,))


def test_load_scenario_invokes_check(demand_parameters: DemandParameters, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure load_scenario calls Scenario.check_consistency."""
    from line_planning import get_paths

    from openbus_light.manipulate import load_scenario
    from openbus_light.model.scenario import Scenario

    # Track if check_consistency was called
    call_count = {"count": 0}

    def mock_check_consistency(_self):
        call_count["count"] += 1
        raise RuntimeError("Mocked error")

    monkeypatch.setattr(Scenario, "check_consistency", mock_check_consistency)

    with pytest.raises(RuntimeError, match="Mocked error"):
        load_scenario(demand_parameters, get_paths())

    assert call_count["count"] == 1
