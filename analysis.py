import argparse
from typing import List

from scipy.spatial import cKDTree
import numpy as np
import matplotlib
import json
matplotlib.use('TkAgg')  # or 'TkAgg' or 'Qt5Agg' depending on your system
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent

from simulation import Simulation

RAW_SAVE_PATH_DEFAULT = 'my_plot.png'
NORMALIZED_SAVE_PATH = 'normalized.png'
MAX_COST = 500_000
MAX_SATISFACTION = 100
HOVER_DISTANCE_RAW = 50_000
HOVER_DISTANCE_NORMALIZED = 0.05


def _normalize_values(costs: List[float], sats: List[float]) -> tuple[list[float], list[float]]:
    normalized_costs = [min(max(cost / MAX_COST, 0), 1) for cost in costs]
    normalized_sats = [min(max(sat / MAX_SATISFACTION, 0), 1) for sat in sats]
    return normalized_costs, normalized_sats


def _build_tooltips(costs: List[float], sats: List[float], seeds: List[int], normalized: bool = False) -> List[str]:
    labels = []
    for i, (cost, sat, seed) in enumerate(zip(costs, sats, seeds)):
        if normalized:
            labels.append(
                f"Run: {i}\n"
                f"Normalized Cost (x): {cost:.4f}\n"
                f"Normalized Satisfaction (y): {sat:.4f}\n"
                f"Seed: {seed}"
            )
        else:
            labels.append(
                f"Run: {i}\n"
                f"Cost (x): ${cost:,.2f}\n"
                f"Weighted Satisfaction (y): {sat:.2f}\n"
                f"Seed: {seed}"
            )
    return labels


def _add_hover(ax, fig, scatter, x_values, y_values, labels, hover_distance: float) -> None:
    points = np.column_stack((x_values, y_values))
    tree = cKDTree(points)

    annotation = ax.annotate(
        '',
        xy=(0, 0),
        xytext=(10, 10),
        textcoords='offset points',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='black', alpha=0.9),
    )
    annotation.set_visible(False)

    last_idx = None

    def on_move(event: MouseEvent) -> None:
        nonlocal last_idx

        if event.inaxes != ax or event.xdata is None or event.ydata is None:
            if annotation.get_visible():
                annotation.set_visible(False)
                fig.canvas.draw_idle()
            return

        _, contains = scatter.get_visible(), True
        distance, idx = tree.query([event.xdata, event.ydata])

        if distance < hover_distance and idx != last_idx:
            last_idx = idx
            annotation.xy = (x_values[idx], y_values[idx])
            annotation.set_text(labels[idx])
            annotation.set_visible(True)
            fig.canvas.draw_idle()
        elif distance >= hover_distance and annotation.get_visible():
            last_idx = None
            annotation.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', lambda event: on_move(event))


def _build_scatter_figure(
    costs: List[float],
    sats: List[float],
    seeds: List[int],
    normalized_costs: List[float],
    normalized_sats: List[float],
) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    raw_ax, norm_ax = axes
    raw_scatter = raw_ax.scatter(costs, sats, alpha=0.75, edgecolors='black', linewidths=0.4, s=10)
    raw_ax.set_title('Simulation Results: Cost vs Weighted Satisfaction')
    raw_ax.set_xlabel('Graph Total Cost (x)')
    raw_ax.set_ylabel('Graph Weighted Satisfaction (y)')
    raw_ax.grid(True, linestyle='--', alpha=0.35)
    _add_hover(raw_ax, fig, raw_scatter, costs, sats, _build_tooltips(costs, sats, seeds), HOVER_DISTANCE_RAW)

    norm_scatter = norm_ax.scatter(
        normalized_costs,
        normalized_sats,
        alpha=0.75,
        edgecolors='black',
        linewidths=0.4,
        s=10,
        color='darkorange'
    )
    norm_ax.set_title('Normalized Results: Cost vs Weighted Satisfaction')
    norm_ax.set_xlabel('Normalized Cost (0 to 1)')
    norm_ax.set_ylabel('Normalized Weighted Satisfaction (0 to 1)')
    norm_ax.set_xlim(0, 1)
    norm_ax.set_ylim(0, 1)
    norm_ax.grid(True, linestyle='--', alpha=0.35)
    _add_hover(
        norm_ax,
        fig,
        norm_scatter,
        normalized_costs,
        normalized_sats,
        _build_tooltips(normalized_costs, normalized_sats, seeds, normalized=True),
        HOVER_DISTANCE_NORMALIZED,
    )

    fig.tight_layout()
    return fig


def _save_individual_plots(
    costs: List[float],
    sats: List[float],
    normalized_costs: List[float],
    normalized_sats: List[float],
    raw_save_path: str,
) -> None:
    raw_fig, raw_ax = plt.subplots(figsize=(11, 7))
    raw_ax.scatter(costs, sats, alpha=0.75, edgecolors='black', linewidths=0.4, s=10)
    raw_ax.set_title('Simulation Results: Cost vs Weighted Satisfaction')
    raw_ax.set_xlabel('Graph Total Cost (x)')
    raw_ax.set_ylabel('Graph Weighted Satisfaction (y)')
    raw_ax.grid(True, linestyle='--', alpha=0.35)
    raw_fig.tight_layout()
    raw_fig.savefig(raw_save_path, dpi=150, bbox_inches='tight')
    plt.close(raw_fig)

    normalized_fig, normalized_ax = plt.subplots(figsize=(11, 7))
    normalized_ax.scatter(normalized_costs, normalized_sats, alpha=0.75, edgecolors='black', linewidths=0.4, s=10, color='darkorange')
    normalized_ax.set_title('Normalized Results: Cost vs Weighted Satisfaction')
    normalized_ax.set_xlabel('Normalized Cost (0 to 1)')
    normalized_ax.set_ylabel('Normalized Weighted Satisfaction (0 to 1)')
    normalized_ax.set_xlim(0, 1)
    normalized_ax.set_ylim(0, 1)
    normalized_ax.grid(True, linestyle='--', alpha=0.35)
    normalized_fig.tight_layout()
    normalized_fig.savefig(NORMALIZED_SAVE_PATH, dpi=150, bbox_inches='tight')
    plt.close(normalized_fig)


def plot_simulation_results(num_runs: int, show_plot: bool = True, save_path: str | None = None) -> None:
    sim = Simulation(num_runs=num_runs)
    sim.run()

    costs = [result['graph_total_cost'] for result in sim.results]
    weighted_sats = [result['graph_weighted_satisfaction'] for result in sim.results]
    seeds = [result['seed'] for result in sim.results]
    normalized_costs, normalized_sats = _normalize_values(costs, weighted_sats)

    with open('simulation_results.json', 'w') as f:
        json.dump({
            'execution_time': sim.execution_time,
            'num_runs': sim.num_runs,
            'results': [{k: v for k, v in r.items() if k != 'paths'} for r in sim.results]
        }, f)

    raw_save_path = save_path or RAW_SAVE_PATH_DEFAULT
    _save_individual_plots(costs, weighted_sats, normalized_costs, normalized_sats, raw_save_path)

    fig = _build_scatter_figure(costs, weighted_sats, seeds, normalized_costs, normalized_sats)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot simulation graph cost vs weighted satisfaction.')
    parser.add_argument('--runs', type=int, default=500, help='Number of simulation runs to generate.')
    parser.add_argument('--save', type=str, default=RAW_SAVE_PATH_DEFAULT, help='Optional file path to save the main plot image.')
    parser.add_argument('--no-show', action='store_true', help='Do not open interactive window.')
    args = parser.parse_args()

    plot_simulation_results(num_runs=2_000_000, show_plot=True, save_path="my_plot.png")
