"""Tests for sorting event stream generation, snapshots, and accuracy."""
import pytest
from algorithms.sorting.registry import SORTING_ALGORITHMS, get_sorting_algorithm
from engine.events import EventType

@pytest.mark.parametrize("slug", list(SORTING_ALGORITHMS.keys()))
def test_event_trace_snapshots(slug):
    """Verify all events have valid snapshots and finish with a completely sorted array."""
    algo = get_sorting_algorithm(slug)
    arr = [34, -5, 12, 99, 0, 18, -22]
    events = algo.generate_events(arr)

    assert len(events) > 0
    # Last event must be FINISH
    last_event = events[-1]
    assert last_event.event_type == EventType.FINISH
    assert last_event.array_snapshot == sorted(arr)
    # Final sorted indices must cover the entire array
    assert last_event.sorted_indices == set(range(len(arr)))

    # Every event snapshot must preserve array length
    for idx, ev in enumerate(events):
        assert len(ev.array_snapshot) == len(arr), f"Snapshot at event {idx} has invalid length"

    # For pure swap-based in-place algorithms, intermediate snapshots preserve the exact multiset
    if slug in ("bubble_sort", "selection_sort", "quick_sort", "heap_sort"):
        original_multiset = sorted(arr)
        for idx, ev in enumerate(events):
            assert sorted(ev.array_snapshot) == original_multiset, (
                f"{slug}: snapshot at event {idx} corrupted multiset"
            )

def test_quick_sort_pivot_events():
    """Verify Quick Sort emits pivot events with valid pivot indices."""
    algo = get_sorting_algorithm("quick_sort")
    arr = [25, 10, 8, 40, 15]
    events = algo.generate_events(arr)

    pivot_events = [e for e in events if e.event_type == EventType.PIVOT]
    assert len(pivot_events) > 0
    for p_ev in pivot_events:
        assert p_ev.pivot_index is not None
        assert 0 <= p_ev.pivot_index < len(arr)

def test_merge_sort_range_events():
    """Verify Merge Sort emits merge range events with valid sub-array bounds."""
    algo = get_sorting_algorithm("merge_sort")
    arr = [14, 3, 22, 1, 9]
    events = algo.generate_events(arr)

    merge_events = [e for e in events if e.event_type == EventType.MERGE_RANGE]
    assert len(merge_events) > 0
    for m_ev in merge_events:
        assert m_ev.range_bounds is not None
        left, right = m_ev.range_bounds
        assert 0 <= left <= right < len(arr)
