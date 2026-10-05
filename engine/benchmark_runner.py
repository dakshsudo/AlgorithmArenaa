"""Isolated benchmark runner for algorithms separate from visualizer playback."""
import time
from dataclasses import dataclass
from typing import List
from algorithms.sorting.base import BaseSortAlgorithm
from services.validation_service import ValidationService

@dataclass
class SortBenchmarkResult:
    algorithm_name: str
    array_size: int
    runtime_ms: float
    comparisons: int
    swaps: int
    writes: int
    is_correct: bool
    status_message: str

class BenchmarkRunner:
    """Runs sorting algorithms on isolated cloned inputs to measure pure algorithmic performance."""

    @staticmethod
    def benchmark_sorting(algorithm: BaseSortAlgorithm, array: List[int]) -> SortBenchmarkResult:
        cloned_arr = list(array)
        
        # Measure algorithmic execution time
        start_ns = time.perf_counter_ns()
        events = algorithm.generate_events(cloned_arr)
        end_ns = time.perf_counter_ns()
        
        runtime_ms = (end_ns - start_ns) / 1_000_000.0

        # Count operations from generated event stream
        c_count = 0
        s_count = 0
        w_count = 0
        for ev in events:
            if ev.event_type.value == "compare":
                c_count += 1
            elif ev.event_type.value == "swap":
                s_count += 1
            elif ev.event_type.value == "write":
                w_count += 1

        final_arr = events[-1].array_snapshot if events else cloned_arr
        is_valid, msg = ValidationService.verify_sorted_correctness(array, final_arr)

        return SortBenchmarkResult(
            algorithm_name=algorithm.metadata.name,
            array_size=len(array),
            runtime_ms=round(runtime_ms, 3),
            comparisons=c_count,
            swaps=s_count,
            writes=w_count,
            is_correct=is_valid,
            status_message=msg
        )
