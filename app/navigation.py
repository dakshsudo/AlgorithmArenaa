"""Navigation definitions and page registry."""
from dataclasses import dataclass
from enum import Enum
from typing import List

class NavDestination(str, Enum):
    DASHBOARD = "dashboard"
    SORTING = "sorting"
    PATHFINDING = "pathfinding"
    NQUEENS = "nqueens"
    COMPARISON = "comparison"
    COMPLEXITY = "complexity"
    LEARNING = "learning"

@dataclass
class NavItem:
    id: NavDestination
    title: str
    icon_char: str
    description: str

NAV_ITEMS: List[NavItem] = [
    NavItem(
        id=NavDestination.DASHBOARD,
        title="Dashboard",
        icon_char="⌂",
        description="Overview, quick launch, and learning progress"
    ),
    NavItem(
        id=NavDestination.SORTING,
        title="Sorting Lab",
        icon_char="📶",
        description="Bar visualization, comparisons, swaps, and step-by-step sorting"
    ),
    NavItem(
        id=NavDestination.PATHFINDING,
        title="Pathfinding Lab",
        icon_char="🗺",
        description="Interactive grid, BFS, DFS, Dijkstra, and A* route exploration"
    ),
    NavItem(
        id=NavDestination.NQUEENS,
        title="N-Queens Lab",
        icon_char="♛",
        description="Backtracking exploration, conflict detection, and solution enumeration"
    ),
    NavItem(
        id=NavDestination.COMPARISON,
        title="Comparison Lab",
        icon_char="⚖",
        description="Multi-algorithm side-by-side benchmark and operations comparison"
    ),
    NavItem(
        id=NavDestination.COMPLEXITY,
        title="Complexity Lab",
        icon_char="📈",
        description="Asymptotic analysis, Big-O curves, worked examples, and math"
    ),
    NavItem(
        id=NavDestination.LEARNING,
        title="Learning & Viva",
        icon_char="🎓",
        description="Comprehensive notes, pseudocode, quizzes, and viva preparation"
    ),
]
