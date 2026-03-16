import json
import os
from typing import List

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from scipy.spatial import cKDTree

MAX_COST = 471_220
MAX_SATISFACTION = 100
HOVER_DISTANCE_RAW = 50_000
HOVER_DISTANCE_NORMALIZED = 0.05
DATA_PATH = 'simulation_results.json'


if not os.path.exists(DATA_PATH):
    print(f"File not found: {DATA_PATH}. Run analysis.py first.")
    raise SystemExit(1)

with open(DATA_PATH, 'r') as f:
    results_data = json.load(f)

results = results_data['results']
costs = [r['graph_total_cost'] for r in results]
weighted_sats = [r['graph_weighted_satisfaction'] for r in results]
seeds = [r['seed'] for r in results]
normalized_costs = [min(max(cost / MAX_COST, 0), 1) for cost in costs]
normalized_sats = [min(max(sat / MAX_SATISFACTION, 0), 1) for sat in weighted_sats]
max_x_idx = int(np.argmax(costs))
min_x_idx = int(np.argmin(costs))
xmin_point = (normalized_costs[min_x_idx], normalized_sats[min_x_idx])
xmax_point = (normalized_costs[max_x_idx], normalized_sats[max_x_idx])
furthestDist =0
furthestIndex = 0

for i in range(len(normalized_costs)):
    cost = normalized_costs[i]
    sat = normalized_sats[i]
    distance = abs(((xmax_point[1] - xmin_point[1] )*cost)-((xmax_point[0] - xmin_point[0])*sat)+(xmax_point[0]*xmin_point[1])-(xmax_point[1]*xmin_point[0]))/np.sqrt((xmax_point[1] - xmin_point[1])**2 + (xmax_point[0] - xmin_point[0])**2)
    lineY= ((xmax_point[1] - xmin_point[1])/(xmax_point[0] - xmin_point[0]))*cost + (xmin_point[1] - ((xmax_point[1] - xmin_point[1])/(xmax_point[0] - xmin_point[0]))*xmin_point[0])
    if distance > furthestDist and sat>lineY:
        furthestDist = distance
        furthestIndex = i

def _build_tooltips(cost_values: List[float], sat_values: List[float], seed_values: List[int], normalized: bool = False) -> List[str]:
    labels = []
    for i, (cost, sat, seed) in enumerate(zip(cost_values, sat_values, seed_values)):
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


def _add_hover(ax, fig, x_values, y_values, labels, hover_distance: float) -> None:
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


fig, (raw_ax, norm_ax) = plt.subplots(1, 2, figsize=(16, 7))

raw_ax.scatter(costs, weighted_sats, alpha=0.75, edgecolors='black', linewidths=0.4, s=10)

raw_ax.set_title('Simulation Results: Cost vs Weighted Satisfaction')
raw_ax.set_xlabel('Graph Total Cost (x)')
raw_ax.set_ylabel('Graph Weighted Satisfaction (y)')
raw_ax.grid(True, linestyle='--', alpha=0.35)
_add_hover(raw_ax, fig, costs, weighted_sats, _build_tooltips(costs, weighted_sats, seeds), HOVER_DISTANCE_RAW)
norm_ax.scatter(normalized_costs, normalized_sats, alpha=0.75, edgecolors='black', linewidths=0.4, s=10, color='darkorange')
norm_ax.set_title('Normalized Results: Cost vs Weighted Satisfaction')
norm_ax.set_xlabel('Normalized Cost (0 to 1)')
norm_ax.set_ylabel('Normalized Weighted Satisfaction (0 to 1)')
norm_ax.set_xlim(0, 1)
norm_ax.set_ylim(0, 1)
norm_ax.grid(True, linestyle='--', alpha=0.35)
_add_hover(
    norm_ax,
    fig,
    normalized_costs,
    normalized_sats,
    _build_tooltips(normalized_costs, normalized_sats, seeds, normalized=True),
    HOVER_DISTANCE_NORMALIZED,
)

norm_ax.plot(
    [xmin_point[0], xmax_point[0]],  # X coordinates
    [xmin_point[1], xmax_point[1]],  # Y coordinates
    color='blue',
    linestyle='--',
    linewidth=2,
    label='Line between min/max X'
)


plt.tight_layout()
norm_ax.scatter(normalized_costs[furthestIndex], normalized_sats[furthestIndex], c='green', s=30, zorder=2)
#raw_ax.scatter(costs[furthestIndex], weighted_sats[furthestIndex], c='blue', s=30, zorder=2)

plt.show()
