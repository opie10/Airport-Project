import pathData
from main import Main
import time
from concurrent.futures import ProcessPoolExecutor
import os

def _run_single_simulation(run_index):
    """Helper function to run one simulation (must be top-level for pickling)"""
    main_instance = Main()
    graph_total_cost = (main_instance.TotalEdgeNumber * Simulation.lineUpkeep +
                        Simulation.CostPerMile * main_instance.TotalEdgeDistance)
    graph_weighted_satisfaction = main_instance.returnWeightedSat()

    return {
        'run_index': run_index,
        'seed': main_instance.seed,
        'edge_count': main_instance.TotalEdgeNumber,
        'total_distance': main_instance.TotalEdgeDistance,
        'graph_total_cost': graph_total_cost,
        'graph_weighted_satisfaction': graph_weighted_satisfaction,
        'paths': main_instance.pathDataArray,
    }

class Simulation:
    lineUpkeep = 10000
    CostPerMile = 20
    def __init__(self, num_runs):
        self.num_runs = num_runs
        self.results = []
        self.execution_time = 0

    def run(self):
        start_time = time.time()
        self.results = []

        # Use all available CPU cores
        max_workers = os.cpu_count()

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            self.results = list(executor.map(_run_single_simulation, range(self.num_runs)))

        end_time = time.time()
        self.execution_time = end_time - start_time

        end_time = time.time()
        self.execution_time = end_time - start_time

    def get_statistics(self):
        if not self.results:
            raise ValueError('No simulation results available. Run the simulation first.')

        edge_counts = [r['edge_count'] for r in self.results]
        distances = [r['total_distance'] for r in self.results]

        stats = {
            'avg_edges': sum(edge_counts) / len(edge_counts),
            'min_edges': min(edge_counts),
            'max_edges': max(edge_counts),
            'avg_distance': sum(distances) / len(distances),
            'min_distance': min(distances),
            'max_distance': max(distances),
        }

        return stats

    def print_results(self):
        stats = self.get_statistics()
        print(f"Simulation Results ({self.num_runs} runs):")
        print(f"  Execution Time: {self.execution_time:.2f} seconds ({self.execution_time/60:.2f} minutes)")
        print(f"  Avg Edges: {stats['avg_edges']:.2f}")
        print(f"  Min Edges: {stats['min_edges']}")
        print(f"  Max Edges: {stats['max_edges']}")
        print(f"  Avg Distance: {stats['avg_distance']:.2f}")
        print(f"  Min Distance: {stats['min_distance']}")
        print(f"  Max Distance: {stats['max_distance']}")



if __name__ == "__main__":
    sim = Simulation(num_runs=1000)
    sim.run()
    sim.print_results()
