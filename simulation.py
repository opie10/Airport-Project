from main import Main
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from tqdm import tqdm


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
        'fingerprint': main_instance.get_graph_fingerprint(),
    }


class Simulation:
    lineUpkeep = 10000
    CostPerMile = 20
    TARGET_UNIQUE_GRAPHS = 26704
    MAX_EMPTY_FILL_BATCHES = 10_000

    def __init__(self, num_runs):
        self.num_runs = num_runs
        self.results = []
        self.execution_time = 0
        self.total_attempts = 0
        self.target_unique_graphs = self.TARGET_UNIQUE_GRAPHS

    def _collect_batch(self, executor, start_index, batch_size, pbar=None):
        futures = [
            executor.submit(_run_single_simulation, i)
            for i in range(start_index, start_index + batch_size)
        ]

        batch_results = []
        for future in as_completed(futures):
            batch_results.append(future.result())
            if pbar is not None:
                pbar.update(1)

        self.total_attempts += batch_size
        return batch_results

    def _append_unique_results(self, candidate_results, seen_fingerprints):
        added = 0
        for result in candidate_results:
            if len(self.results) >= self.target_unique_graphs:
                break

            fingerprint = result.pop('fingerprint')
            if fingerprint in seen_fingerprints:
                continue

            seen_fingerprints.add(fingerprint)
            result['run_index'] = len(self.results)
            self.results.append(result)
            added += 1

        return added

    def run(self):
        start_time = time.time()
        self.results = []
        self.total_attempts = 0
        raw_results = []
        seen_fingerprints = set()
        max_workers = os.cpu_count() or 1
        chunk_size = max_workers * 6

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Phase 1: initial requested pass
            with tqdm(total=self.num_runs, desc='Initial pass', unit='run') as pbar:
                for chunk_start in range(0, self.num_runs, chunk_size):
                    current_batch_size = min(chunk_size, self.num_runs - chunk_start)
                    raw_results.extend(self._collect_batch(executor, chunk_start, current_batch_size, pbar))

            print('Deduplicating initial pass...')
            self._append_unique_results(raw_results, seen_fingerprints)
            initial_duplicates = self.num_runs - len(self.results)
            print(
                f'Initial pass complete: {len(self.results):,} unique graphs '
                f'from {self.num_runs:,} runs ({initial_duplicates:,} duplicates removed).'
            )

            # Phase 2: keep filling until target unique count is reached
            if len(self.results) < self.target_unique_graphs:
                empty_fill_batches = 0
                next_run_index = self.total_attempts
                remaining = self.target_unique_graphs - len(self.results)
                print(f'Filling remaining {remaining:,} unique graphs...')

                with tqdm(
                    total=self.target_unique_graphs,
                    initial=len(self.results),
                    desc='Unique graphs',
                    unit='graph'
                ) as fill_pbar:
                    fill_pbar.set_postfix({'attempts': self.total_attempts})

                    while len(self.results) < self.target_unique_graphs:
                        batch_results = self._collect_batch(executor, next_run_index, chunk_size)
                        next_run_index += chunk_size
                        added = self._append_unique_results(batch_results, seen_fingerprints)

                        if added:
                            fill_pbar.update(added)
                            empty_fill_batches = 0
                        else:
                            empty_fill_batches += 1

                        fill_pbar.set_postfix({
                            'attempts': self.total_attempts,
                            'unique': len(self.results)
                        })

                        if empty_fill_batches >= self.MAX_EMPTY_FILL_BATCHES:
                            print(
                                f'Stopped early after {empty_fill_batches} empty fill batches. '
                                f'Collected {len(self.results):,} / {self.target_unique_graphs:,} unique graphs.'
                            )
                            break

        end_time = time.time()
        self.execution_time = end_time - start_time

    def get_statistics(self):
        if not self.results:
            raise ValueError('No simulation results available. Run the simulation first.')

        edge_counts = [r['edge_count'] for r in self.results]
        distances = [r['total_distance'] for r in self.results]

        stats = {
            'unique_graphs': len(self.results),
            'target_unique_graphs': self.target_unique_graphs,
            'total_attempts': self.total_attempts,
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
        print(f'Simulation Results (initial pass: {self.num_runs:,} runs)')
        print(f'  Execution Time: {self.execution_time:.2f} seconds ({self.execution_time / 60:.2f} minutes)')
        print(f'  Unique Graphs: {stats["unique_graphs"]:,} / {stats["target_unique_graphs"]:,}')
        print(f'  Total Attempts: {stats["total_attempts"]:,}')
        print(f'  Avg Edges: {stats["avg_edges"]:.2f}')
        print(f'  Min Edges: {stats["min_edges"]}')
        print(f'  Max Edges: {stats["max_edges"]}')
        print(f'  Avg Distance: {stats["avg_distance"]:.2f}')
        print(f'  Min Distance: {stats["min_distance"]}')
        print(f'  Max Distance: {stats["max_distance"]}')


if __name__ == "__main__":
    sim = Simulation(num_runs=1000)
    sim.run()
    sim.print_results()
