"""Sorting algorithm registry and factory."""
from typing import Dict, List, Type
from algorithms.sorting.base import BaseSortAlgorithm
from algorithms.sorting.bubble_sort import BubbleSort
from algorithms.sorting.selection_sort import SelectionSort
from algorithms.sorting.insertion_sort import InsertionSort
from algorithms.sorting.merge_sort import MergeSort
from algorithms.sorting.quick_sort import QuickSort
from algorithms.sorting.heap_sort import HeapSort

SORTING_ALGORITHMS: Dict[str, Type[BaseSortAlgorithm]] = {
    "bubble_sort": BubbleSort,
    "selection_sort": SelectionSort,
    "insertion_sort": InsertionSort,
    "merge_sort": MergeSort,
    "quick_sort": QuickSort,
    "heap_sort": HeapSort,
}

def get_sorting_algorithm(slug: str) -> BaseSortAlgorithm:
    """Return an instantiated algorithm by its slug."""
    if slug not in SORTING_ALGORITHMS:
        raise ValueError(f"Unknown sorting algorithm slug: {slug}")
    return SORTING_ALGORITHMS[slug]()

def list_sorting_algorithms() -> List[BaseSortAlgorithm]:
    """Return an instantiated list of all available sorting algorithms."""
    return [cls() for cls in SORTING_ALGORITHMS.values()]
