import glob
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from itertools import chain
from pathlib import Path
from statistics import mean
from typing import Any, Sequence

from tqdm import tqdm

from ..model import BusLine, Direction, DirectionName, LineFrequency, LineName, LineNr, VehicleCapacity
from ..model.type import StationName
from .direction import update_trip_times


def _convert_seconds_to_timedelta(seconds: float) -> timedelta:
    """
    Convert seconds to timedelta.
    :param seconds: float, time in second
    :return: timedelta
    """
    return timedelta(seconds=seconds)


@dataclass(frozen=True)
class LineFactory:
    def create_line_from_json(self, json_data: dict[Any, Any]) -> BusLine:
        """
        Parse JSON data and create a BusLine object.

        :param json_data: dict[Any, Any], JSON representation with line number, stations, travel times,
            capacity, and frequency
        :return: BusLine, complete bus line with both directions, capacity, and frequency
        :raises RuntimeError: if station count doesn't match between data and computed values
        """
        line_name = LineName(str(json_data["nummer"]))

        direction_a = Direction(
            station_sequence=tuple(map(str, json_data["linie_a"])),  # type: ignore
            trip_times=tuple(map(_convert_seconds_to_timedelta, json_data["fahrzeiten_a"])),
            name=DirectionName("a"),
        )

        direction_b = Direction(
            station_sequence=tuple(map(str, json_data["linie_b"])),  # type: ignore
            trip_times=tuple(map(_convert_seconds_to_timedelta, json_data["fahrzeiten_b"])),
            name=DirectionName("b"),
        )

        if not direction_a.station_count == json_data["stops_a"]:
            raise RuntimeError("Import failed due to inconsistent number of stops")
        if not direction_b.station_count == json_data["stops_b"]:
            raise RuntimeError("Import failed due to inconsistent number of stops")

        return BusLine(
            LineNr(json_data["nummer"]),
            line_name,
            direction_a,
            direction_b,
            VehicleCapacity(json_data["kapazität"]),
            LineFrequency(json_data["frequenz"]),
        )


def load_lines_from_json(line_factory: LineFactory, path_to_lines: Path) -> tuple[BusLine, ...]:
    """
    Load all bus lines from JSON files and equalize travel times across shared links.

    :param line_factory: LineFactory, factory for creating BusLine objects from JSON
    :param path_to_lines: Path, directory containing JSON files with bus line definitions
    :return: tuple[BusLine, ...], loaded bus lines with equalized travel times on shared links
    """
    loaded_lines: list[BusLine] = []
    all_files_to_load = sorted(glob.glob(os.path.join(path_to_lines, "*.json")))
    for line_to_load in tqdm(all_files_to_load, desc="importing lines", colour="blue"):
        with open(line_to_load, encoding="utf-8") as json_file:
            loaded_lines.append(line_factory.create_line_from_json(json.load(json_file)))

    return _equalise_travel_times_per_link(loaded_lines)


def _equalise_travel_times_per_link(lines: Sequence[BusLine]) -> tuple[BusLine, ...]:
    """
    Equalize the travel times per link across different bus lines with the average travel time.
    :param lines: Sequence[BusLine], sequence of busline objects
    :return: tuple[BusLine, ...], a tuple of BusLine objects with equal travel time
    """
    average_travel_time_per_link = _calculate_average_travel_time_per_link(lines)
    return tuple(
        line._replace(
            direction_up=update_trip_times(average_travel_time_per_link, line.direction_up),
            direction_down=update_trip_times(average_travel_time_per_link, line.direction_down),
        )
        for line in lines
    )


def _calculate_average_travel_time_per_link(
    lines: Sequence[BusLine],
) -> dict[tuple[StationName, StationName], timedelta]:
    """
    Calculate the average travel time per link across all the directions of bus lines.
    :param lines: Sequence[BusLine], sequence of BusLine objects
    :return: dict[tuple[str, str], timedelta], a dict where key is source and target of the link,
        and value is the average travel time of the link
    """
    travel_times_per_link: dict[tuple[StationName, StationName], list[float]] = defaultdict(list)
    for direction in chain.from_iterable((line.direction_up, line.direction_down) for line in lines):
        for (source, target), time_delta in direction.trip_time_by_pair():
            travel_times_per_link[(source, target)].append(time_delta.total_seconds())
    return {k: timedelta(seconds=round(mean(v))) for k, v in travel_times_per_link.items()}
