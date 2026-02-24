"""Week 1 plotting helpers for network and demand exploration."""

from __future__ import annotations

from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from _constants import RESULT_DIRECTORY, get_paths
from openbus_light.manipulate import load_scenario
from openbus_light.model import Scenario
from openbus_light.model.type import Meter
from openbus_light.plan.parameters import DemandParameters


def create_station_demand_bar_plot(scenario: Scenario) -> Figure:
    """Plot outgoing and incoming demand totals per station as side-by-side bars."""
    station_names = [str(station.name) for station in scenario.stations]
    outgoing = [scenario.demand_matrix.starting_from(station.name) for station in scenario.stations]
    incoming = [scenario.demand_matrix.arriving_at(station.name) for station in scenario.stations]

    positions = list(range(len(station_names)))
    bar_width = 0.42

    figure, axis = plt.subplots(figsize=(12, 6))
    axis.bar([position - bar_width / 2 for position in positions], outgoing, width=bar_width, label="Outgoing")
    axis.bar([position + bar_width / 2 for position in positions], incoming, width=bar_width, label="Incoming")

    axis.set_title("Demand load per station")
    axis.set_xlabel("Station")
    axis.set_ylabel("Demand")
    axis.set_xticks(positions)
    axis.set_xticklabels(station_names, rotation=90)
    axis.legend()
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    figure.tight_layout()

    return figure


def create_network_scatter_plot(scenario: Scenario) -> Figure:
    """Plot all station locations and annotate each station with its served line count."""
    x_coords = [station.center_position.long for station in scenario.stations]
    y_coords = [station.center_position.lat for station in scenario.stations]
    demand_sizes = [40 + scenario.demand_matrix.starting_from(station.name) / 3 for station in scenario.stations]

    figure, axis = plt.subplots(figsize=(10, 8))
    scatter = axis.scatter(x_coords, y_coords, s=demand_sizes, c=demand_sizes, cmap="viridis", alpha=0.8)

    for station in scenario.stations:
        axis.annotate(
            f"{station.name} ({len(station.lines)} lines)",
            (station.center_position.long, station.center_position.lat),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
        )

    axis.set_title("Winterthur station layout (size by outgoing demand)")
    axis.set_xlabel("Swiss coordinate X")
    axis.set_ylabel("Swiss coordinate Y")
    axis.grid(linestyle="--", alpha=0.3)
    figure.colorbar(scatter, ax=axis, label="Marker size proxy (outgoing demand)")
    figure.tight_layout()

    return figure


def create_week1_plots(output_dir: Path | None = None) -> tuple[Path, Path]:
    """Generate and save the two week-1 figures, returning their output file paths."""
    scenario = load_scenario(
        DemandParameters(demand_association_radius=Meter(500), demand_scaling=0.1),
        get_paths(),
    )

    destination = output_dir or RESULT_DIRECTORY
    destination.mkdir(parents=True, exist_ok=True)

    station_demand_path = destination / "week1_station_demand.png"
    network_map_path = destination / "week1_network_map.png"

    create_station_demand_bar_plot(scenario).savefig(station_demand_path, dpi=200)
    create_network_scatter_plot(scenario).savefig(network_map_path, dpi=200)

    return station_demand_path, network_map_path


if __name__ == "__main__":
    demand_plot, network_plot = create_week1_plots()
    print(f"Created: {demand_plot}")
    print(f"Created: {network_plot}")
