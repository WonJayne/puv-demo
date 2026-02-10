from typing import NamedTuple

from openbus_light.model.demand import DemandMatrix
from openbus_light.model.line import BusLine
from openbus_light.model.station import Station


class Scenario(NamedTuple):
    demand_matrix: DemandMatrix
    bus_lines: tuple[BusLine, ...]
    stations: tuple[Station, ...]

    def check_consistency(self) -> None:
        """
        Check consistency of scenario components.

        Verifies that all stations referenced in bus lines and demand matrix
        are present in the scenario's station list.
        Should call the two helper methods below.

        :raises ValueError: if stations in demand or lines are not in the station list
        """
        # TODO Week 1
        raise NotImplementedError("TODO Week 1")

    def _check_station_and_lines_consistency(self) -> None:
        """
        Check the consistency between stations and lines. If any stations in the Scenario are not served
            at least one line, raise error and vice versa.
        """
        # TODO Week 1
        raise NotImplementedError("TODO Week 1")

    def _check_station_and_demand_consistency(self) -> None:
        """
        Check the consistency between station and demand. If any stations involved in the demand matrix
            are not within the stations or in the ones served by lines, raise error.
        """
        # TODO Week 1
        raise NotImplementedError("TODO Week 1")
