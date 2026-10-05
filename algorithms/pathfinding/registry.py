"""Pathfinding algorithm registry and presets."""
from typing import Dict, List, Type
from algorithms.pathfinding.base import BasePathfinder
from algorithms.pathfinding.bfs import BFSPathfinder
from algorithms.pathfinding.dfs import DFSPathfinder
from algorithms.pathfinding.dijkstra import DijkstraPathfinder
from algorithms.pathfinding.astar import AStarPathfinder

PATHFINDING_ALGORITHMS: Dict[str, Type[BasePathfinder]] = {
    "bfs": BFSPathfinder,
    "dfs": DFSPathfinder,
    "dijkstra": DijkstraPathfinder,
    "astar": AStarPathfinder,
}

def get_pathfinder(slug: str) -> BasePathfinder:
    if slug not in PATHFINDING_ALGORITHMS:
        raise ValueError(f"Unknown pathfinder slug: {slug}")
    return PATHFINDING_ALGORITHMS[slug]()

def list_pathfinders() -> List[BasePathfinder]:
    return [cls() for cls in PATHFINDING_ALGORITHMS.values()]
