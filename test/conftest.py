"""
Pytest configuration and shared fixtures for test package.
This file is automatically discovered by pytest and makes fixtures available to all test modules.
"""

from datetime import timedelta

import pytest
from line_planning import get_paths

from openbus_light.manipulate import load_scenario
from openbus_light.model import (
    BusLine,
    DemandMatrix,
    Direction,
    DirectionName,
    LineFrequency,
    LineName,
    LineNr,
    MeterPerSecond,
    PointIn2D,
    Scenario,
    Station,
    StationName,
    VehicleCapacity,
)
from openbus_light.model.type import CHF, CHFPerHour, Meter
from openbus_light.plan import LinePlanningParameters
from openbus_light.plan.parameters import DemandParameters, WalkParameters


@pytest.fixture(scope="session")
def demand_parameters() -> DemandParameters:
    """Fixture providing demand parameters for tests."""
    return DemandParameters(demand_association_radius=Meter(500), demand_scaling=0.1)


@pytest.fixture(scope="session")
def walk_parameters() -> WalkParameters:
    """Fixture providing walk parameters for tests."""
    return WalkParameters(walking_speed_between_stations=MeterPerSecond(0.6), maximal_walking_distance=Meter(300))


@pytest.fixture(scope="session")
def line_planning_parameters() -> LinePlanningParameters:
    """Fixture providing line planning parameters for tests."""
    return LinePlanningParameters(
        egress_time_cost=CHFPerHour(0),
        period_duration=timedelta(hours=1),
        waiting_time_cost=CHFPerHour(2),
        in_vehicle_time_cost=CHFPerHour(1),
        walking_time_cost=CHFPerHour(2),
        dwell_time_at_terminal=timedelta(seconds=5 * 60),
        vehicle_cost_per_period=CHF(1000),
        permitted_frequencies=(LineFrequency(1), LineFrequency(2)),
        maximal_number_of_vehicles=None,
        solver="cbc",
    )


@pytest.fixture(scope="session")
def simple_scenario() -> Scenario:
    """Fixture providing a simple 4-station, 2-line scenario for testing."""
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
    demand = DemandMatrix(
        {
            StationName("A"): {StationName("A"): 0, StationName("B"): 20, StationName("C"): 10, StationName("D"): 50},
            StationName("B"): {StationName("A"): 0, StationName("B"): 0, StationName("C"): 15, StationName("D"): 25},
            StationName("C"): {StationName("A"): 0, StationName("B"): 0, StationName("C"): 0, StationName("D"): 275},
            StationName("D"): {StationName("A"): 0, StationName("B"): 0, StationName("C"): 0, StationName("D"): 0},
        }
    )

    return Scenario(demand, bus_lines, stations)


@pytest.fixture(scope="session")
def baseline_scenario(demand_parameters: DemandParameters) -> Scenario:
    """Fixture providing a baseline scenario for tests. Cached at session scope for performance."""
    return load_scenario(demand_parameters, get_paths())
