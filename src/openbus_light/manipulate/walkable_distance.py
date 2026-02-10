from __future__ import annotations

from datetime import timedelta
from itertools import combinations
from typing import Collection

from openbus_light.manipulate.point import calculate_distance_in_m
from openbus_light.model import Station, WalkableDistance
from openbus_light.model.walkable_distance import check_station_and_walk_consistency
from openbus_light.plan.parameters import WalkParameters


def find_all_walkable_distances(
    stations: Collection[Station], parameters: WalkParameters
) -> tuple[WalkableDistance, ...]:
    """
    Get all walkable distances between pairs of stations.

    For each pair of stations, check if they are within walking distance.
    If yes, create a WalkableDistance object with the walking time.

    :param stations: Collection[Station], collection of bus stations
    :param parameters: WalkParameters, parameters for walking distance calculation
        - walking_speed_between_stations: MeterPerSecond
        - maximal_walking_distance: Meter
    :return: tuple[WalkableDistance, ...], WalkableDistance between pairs of stations

    Hints:
    - Use calculate_distance_in_m() to compute the distance between two stations.
    - Use itertools.combinations to generate all unique pairs
    - check_station_and_walk_consistency() verifies that all stations in walkable distances exist in the station list.
    """
    # TODO Week 2 Part A
    raise NotImplementedError("TODO Week 2")

    walkable_distances = tuple()
    check_station_and_walk_consistency(stations, walkable_distances)
    return walkable_distances
