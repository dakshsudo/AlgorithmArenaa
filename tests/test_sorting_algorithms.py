"""Automated correctness tests for all six sorting algorithms."""
import pytest
from algorithms.sorting.registry import SORTING_ALGORITHMS, get_sorting_algorithm

# Test cases covering edge cases and normal variations
TEST_CASES = [
    ("empty", []),
    ("single_element", [42]),
    ("two_elements_sorted", [10, 20]),
    ("two_elements_reversed", [20, 10]),
    ("already_sorted", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("reverse_sorted", [9, 8, 7, 6, 5, 4, 3, 2, 1]),
    ("duplicate_values", [5, 2, 8, 2, 5, 5, 1, 9, 2]),
    ("all_identical", [7, 7, 7, 7, 7]),
    ("negatives_and_positives", [-15, 42, 0, -3, 100, -88, 7, 0, -15]),
    ("large_range", [999, -999, 50, -50, 0, 123, -123]),
]

@pytest.mark.parametrize("slug", list(SORTING_ALGORITHMS.keys()))
@pytest.mark.parametrize("name, array", TEST_CASES)
def test_sorting_correctness(slug, name, array):
    """Test that every algorithm correctly sorts every test case to match Python sorted()."""
    algo = get_sorting_algorithm(slug)
    result = algo.sort(array)
    expected = sorted(array)
    assert result == expected, f"{algo.metadata.name} failed on {name}: got {result}, expected {expected}"

@pytest.mark.parametrize("slug", list(SORTING_ALGORITHMS.keys()))
def test_algorithm_metadata_integrity(slug):
    """Verify metadata adheres to accurate DAA complexity facts."""
    algo = get_sorting_algorithm(slug)
    meta = algo.metadata
    assert meta.name
    assert meta.best_time.startswith("O(")
    assert meta.avg_time.startswith("O(")
    assert meta.worst_time.startswith("O(")
    assert meta.space_complexity.startswith("O(")
    assert len(meta.pseudocode) > 0
    assert len(meta.description) > 10

def test_bubble_sort_early_exit():
    """Verify Bubble Sort early-exit optimization on already sorted array."""
    algo = get_sorting_algorithm("bubble_sort")
    arr = [1, 2, 3, 4, 5, 6]
    events = algo.generate_events(arr)
    
    # In an array of size 6, one pass takes 5 comparisons and 0 swaps, then early-exits
    compares = sum(1 for e in events if e.event_type.value == "compare")
    swaps = sum(1 for e in events if e.event_type.value == "swap")
    assert compares == 5, f"Expected 5 compares for already sorted array, got {compares}"
    assert swaps == 0, f"Expected 0 swaps, got {swaps}"
