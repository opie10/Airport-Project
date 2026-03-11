import argparse
from typing import List

from scipy.spatial import cKDTree
import numpy as np
import matplotlib
import json
import matplotlib.pyplot as plt
matplotlib.use('MacOSX')  #or 'TkAgg' or 'Qt5Agg' depending on your system
from matplotlib.backend_bases import MouseEvent

from simulation import Simulation


def _build_tooltips(costs: List[float], sats: List[float], seeds: List[int]) -> List[str]:
    labels = []
    for i, (cost, sat, seed) in enumerate(zip(costs, sats, seeds)):
        labels.append(
            f"Run: {i}\n"
            f"Cost (x): ${cost:,.2f}\n"
            f"Weighted Satisfaction (y): {sat:.2f}\n"
            f"Seed: {seed}"
        )
    return labels


def plot_simulation_results(num_runs: int, show_plot: bool = True, save_path: str | None = None) -> None:
    sim = Simulation(num_runs=num_runs)
    sim.run()


    costs = [result['graph_total_cost'] for result in sim.results]
    weighted_sats = [result['graph_weighted_satisfaction'] for result in sim.results]
    seeds = [result['seed'] for result in sim.results]

    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(costs, weighted_sats, alpha=0.75, edgecolors='black', linewidths=0.4,
                             s=10)  # smaller points

    ax.set_title('Simulation Results: Cost vs Weighted Satisfaction')
    ax.set_xlabel('Graph Total Cost (x)')
    ax.set_ylabel('Graph Weighted Satisfaction (y)')
    ax.grid(True, linestyle='--', alpha=0.35)

        # Build KD-tree for fast nearest-neighbor lookup
    points = np.column_stack((costs, weighted_sats))
    tree = cKDTree(points)

    labels = _build_tooltips(costs, weighted_sats, seeds)

    annotation = ax.annotate(
            '',
            xy=(0, 0),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='black', alpha=0.9),
        )
    annotation.set_visible(False)

    with open('simulation_results.json', 'w') as f:
        json.dump({
            'execution_time': sim.execution_time,
            'num_runs': sim.num_runs,
            'results': [{k: v for k, v in r.items() if k != 'paths'} for r in sim.results]
        }, f)

    last_idx = None

    def on_move(event: MouseEvent) -> None:
            nonlocal last_idx

            if event.inaxes != ax:
                if annotation.get_visible():
                    annotation.set_visible(False)
                    fig.canvas.draw_idle()
                return

            # Find nearest point using KD-tree (much faster)
            distance, idx = tree.query([event.xdata, event.ydata])

            # Only update if we're close enough and changed point
            if distance < 50000 and idx != last_idx:  # adjust threshold as needed
                last_idx = idx
                annotation.xy = (costs[idx], weighted_sats[idx])
                annotation.set_text(labels[idx])
                annotation.set_visible(True)
                fig.canvas.draw_idle()
            elif distance >= 50000 and annotation.get_visible():
                last_idx = None
                annotation.set_visible(False)
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', on_move)
        # ... rest of code

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    if show_plot:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot simulation graph cost vs weighted satisfaction.')
    parser.add_argument('--runs', type=int, default=500, help='Number of simulation runs to generate.')
    parser.add_argument('--save', type=str, default=None, help='Optional file path to save the plot image.')
    parser.add_argument('--no-show', action='store_true', help='Do not open interactive window.')
    args = parser.parse_args()

    plot_simulation_results(num_runs=10000, show_plot=True, save_path="my_plot.png")

   # plot_simulation_results(num_runs=args.runs, show_plot=not args.no_show, save_path=args.save)
