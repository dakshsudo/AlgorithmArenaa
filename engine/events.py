"""Event definitions for algorithm visualizers."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Set

class EventType(str, Enum):
    COMPARE = "compare"
    SWAP = "swap"
    WRITE = "write"
    PIVOT = "pivot"
    MERGE_RANGE = "merge_range"
    MARK_SORTED = "mark_sorted"
    FINISH = "finish"

@dataclass
class SortEvent:
    """Represents a single atomic operation in a sorting algorithm."""
    event_type: EventType
    indices: Tuple[int, ...] = ()
    values: Tuple[int, ...] = ()
    description: str = ""
    # Array state immediately after this event is applied
    array_snapshot: List[int] = field(default_factory=list)
    # Set of indices that are definitively in their final sorted positions
    sorted_indices: Set[int] = field(default_factory=set)
    # Highlighted sub-range (e.g. for Merge Sort [left, right])
    range_bounds: Optional[Tuple[int, int]] = None
    # Pivot index for Quick Sort
    pivot_index: Optional[int] = None
