"""Base class and metadata for pathfinding algorithms."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional
from algorithms.pathfinding.models import GridMap, PathEvent

@dataclass
class PathfindingMetadata:
    slug: str
    name: str
    guarantees_shortest_path: bool
    supports_weights: bool
    time_complexity: str
    space_complexity: str
    description: str
    pseudocode: List[str]

class BasePathfinder(ABC):
    """Abstract base class for pathfinding search algorithms."""

    def __init__(self):
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> PathfindingMetadata:
        pass

    @abstractmethod
    def search(self, grid: GridMap) -> Tuple[List[PathEvent], List[Tuple[int, int]], int]:
        """Execute the search.
        
        Returns:
            (events, final_path, total_path_cost)
        """
        pass
