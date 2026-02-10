from datetime import timedelta
from itertools import chain
from typing import Iterable, NamedTuple

from .station import Station


class WalkableDistance(NamedTuple):
    station_a: Station
    station_b: Station
    walking_time: timedelta

    def __repr__(self) -> str:
        return f"WalkableDistance(station_a={self.station_a.name}, station_b={self.station_b.name}, walking_time={self.walking_time})"


def check_station_and_walk_consistency(
    stations: Iterable[Station], walkable_distances: Iterable[WalkableDistance]
) -> None:
    """
    Verify that all stations referenced in walkable distances exist in the station list.

    :param stations: Iterable[Station], collection of all stations in the scenario
    :param walkable_distances: Iterable[WalkableDistance], walkable connections to validate
    :raises ValueError: if any walkable distance references a station not in the station list
    """
    all_station_names = frozenset(station.name for station in stations)
    walkable_stations = set(
        chain.from_iterable((link.station_a.name, link.station_b.name) for link in walkable_distances)
    )
    if not all_station_names.issuperset(walkable_stations):
        unknown_stations = walkable_stations.difference(all_station_names)
        raise ValueError(f"Some Walking Distances involve stations not defined in the scenario: {unknown_stations}")
