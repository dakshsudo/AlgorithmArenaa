"""Data models and events for pathfinding algorithms."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Set, Dict

class CellType(int, Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    TARGET = 3
    WEIGHTED = 4

class PathEventType(str, Enum):
    VISIT_FRONTIER = "frontier"
    EXPLORE = "explore"
    FOUND_PATH = "found_path"
    NO_PATH = "no_path"
    FINISH = "finish"

@dataclass
class PathEvent:
    """Represents a single step during pathfinding execution."""
    event_type: PathEventType
    current_node: Optional[Tuple[int, int]] = None
    frontier_nodes: List[Tuple[int, int]] = field(default_factory=list)
    visited_nodes: Set[Tuple[int, int]] = field(default_factory=set)
    path: List[Tuple[int, int]] = field(default_factory=list)
    cost_so_far: float = 0.0
    description: str = ""

@dataclass
class GridMap:
    """Represents an interactive 2D grid."""
    rows: int = 20
    cols: int = 30
    start: Tuple[int, int] = (10, 5)
    target: Tuple[int, int] = (10, 24)
    walls: Set[Tuple[int, int]] = field(default_factory=set)
    weights: Dict[Tuple[int, int], int] = field(default_factory=dict)
    weight_cost: int = 5

    def is_in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, r: int, c: int) -> bool:
        return self.is_in_bounds(r, c) and (r, c) not in self.walls

    def get_cost(self, r: int, c: int) -> int:
        if (r, c) in self.weights:
            return self.weights[(r, c)]
        return 1

    def get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Return 4-directional cardinal neighbors."""
        neighbors = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if self.is_walkable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    getNeighbors = get_neighbors

    def clone(self) -> 'GridMap':
        g = GridMap(
            rows=self.rows,
            cols=self.cols,
            start=self.start,
            target=self.target,
            walls=set(self.walls),
            weights=dict(self.weights),
            weight_cost=self.weight_cost
        )
        return g
