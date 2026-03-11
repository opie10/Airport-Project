import json
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('MacOSX')
from matplotlib.backend_bases import MouseEvent
from scipy.spatial import cKDTree
from typing import List

data_path = 'simulation_results.json'

if not os.path.exists(data_path):
    print(f"File not found: {data_path}. Run analysis.py first.")
    exit()

with open(data_path, 'r') as f:
    results_data = json.load(f)

results = results_data['results']
costs = [r['graph_total_cost'] for r in results]
weighted_sats = [r['graph_weighted_satisfaction'] for r in results]
seeds = [r['seed'] for r in results]


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


fig, ax = plt.subplots(figsize=(11, 7))
ax.scatter(costs, weighted_sats, alpha=0.75, edgecolors='black', linewidths=0.4, s=10)

ax.set_title('Simulation Results: Cost vs Weighted Satisfaction')
ax.set_xlabel('Graph Total Cost (x)')
ax.set_ylabel('Graph Weighted Satisfaction (y)')
ax.grid(True, linestyle='--', alpha=0.35)

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

last_idx = None

def on_move(event: MouseEvent) -> None:
    global last_idx

    if event.inaxes != ax:
        if annotation.get_visible():
            annotation.set_visible(False)
            fig.canvas.draw_idle()
        return

    distance, idx = tree.query([event.xdata, event.ydata])

    if distance < 50000 and idx != last_idx:
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
plt.tight_layout()
plt.show()
