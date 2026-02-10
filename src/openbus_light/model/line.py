from typing import Iterable, Mapping, NamedTuple

from .direction import Direction
from .type import LineFrequency, LineName, LineNr, VehicleCapacity


class BusLine(NamedTuple):
    number: LineNr
    name: LineName
    direction_up: Direction
    direction_down: Direction
    capacity: VehicleCapacity
    frequency: LineFrequency


def update_capacities(
    bus_lines: Iterable[BusLine], new_capacities: Mapping[LineNr, VehicleCapacity]
) -> tuple[BusLine, ...]:
    """
    Create new bus line instances with updated vehicle capacities.

    :param bus_lines: Iterable[BusLine], bus lines to update
    :param new_capacities: Mapping[LineNr, VehicleCapacity], mapping from line number to new capacity
    :return: tuple[BusLine, ...], bus lines with updated capacities (only lines in new_capacities are included)
    """
    updated = []
    for line in bus_lines:
        if line.number in new_capacities:
            updated_line = line._replace(capacity=new_capacities[line.number])
            updated.append(updated_line)

    return tuple(updated)
