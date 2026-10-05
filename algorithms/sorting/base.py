"""Base interface and metadata definitions for sorting algorithms."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Set, Tuple, Optional
from engine.events import SortEvent, EventType

@dataclass
class AlgorithmMetadata:
    """Metadata describing theoretical complexity, properties, and pseudocode."""
    slug: str
    name: str
    best_time: str
    avg_time: str
    worst_time: str
    space_complexity: str
    is_stable: bool
    description: str
    pseudocode: List[str]

class BaseSortAlgorithm(ABC):
    """Abstract base class for all sorting algorithms."""
    
    def __init__(self):
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        """Return the metadata for this algorithm."""
        pass

    @abstractmethod
    def generate_events(self, initial_array: List[int]) -> List[SortEvent]:
        """Execute the sorting algorithm and return an ordered sequence of events."""
        pass

    def sort(self, initial_array: List[int]) -> List[int]:
        """Return a sorted copy using the algorithm's event trace."""
        events = self.generate_events(initial_array)
        if not events:
            return list(initial_array)
        # Final array snapshot is at the last event
        return list(events[-1].array_snapshot)
