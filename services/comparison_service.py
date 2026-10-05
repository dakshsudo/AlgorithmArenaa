"""Service for running multi-algorithm benchmarks and comparisons on identical inputs."""
import time
from dataclasses import dataclass
from typing import List, Dict
from algorithms.sorting.registry import get_sorting_algorithm
from algorithms.pathfinding.registry import get_pathfinder
from algorithms.pathfinding.models import GridMap
from engine.benchmark_runner import BenchmarkRunner, SortBenchmarkResult

@dataclass
class PathBenchmarkResult:
    algorithm_name: str
    path_found: bool
    path_length: int
    path_cost: int
    visited_nodes: int
    runtime_ms: float
    guarantees_shortest: bool
    supports_weights: bool

class ComparisonService:
    """Executes side-by-side algorithm comparisons on identical datasets."""

    @classmethod
    def compare_sorting(cls, algorithm_slugs: List[str], array: List[int]) -> List[SortBenchmarkResult]:
        """Run each sorting algorithm on an independent clone of the initial array."""
        results: List[SortBenchmarkResult] = []
        for slug in algorithm_slugs:
            algo = get_sorting_algorithm(slug)
            # BenchmarkRunner clones array and measures pure execution without UI lag
            res = BenchmarkRunner.benchmark_sorting(algo, array)
            results.append(res)
        return results

    @classmethod
    def compare_pathfinding(cls, pathfinder_slugs: List[str], grid: GridMap) -> List[PathBenchmarkResult]:
        """Run each pathfinding algorithm on an independent clone of the grid."""
        results: List[PathBenchmarkResult] = []
        for slug in pathfinder_slugs:
            pf = get_pathfinder(slug)
            cloned_grid = grid.clone()

            start_ns = time.perf_counter_ns()
            events, path, cost = pf.search(cloned_grid)
            end_ns = time.perf_counter_ns()

            runtime_ms = (end_ns - start_ns) / 1_000_000.0
            visited = len(events[-1].visited_nodes) if events else 0

            results.append(PathBenchmarkResult(
                algorithm_name=pf.metadata.name,
                path_found=len(path) > 0,
                path_length=len(path),
                path_cost=cost,
                visited_nodes=visited,
                runtime_ms=round(runtime_ms, 3),
                guarantees_shortest=pf.metadata.guarantees_shortest_path,
                supports_weights=pf.metadata.supports_weights
            ))
        return results
