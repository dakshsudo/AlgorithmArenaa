"""Automated tests for pathfinding algorithms (BFS, DFS, Dijkstra, A*)."""
import pytest
from algorithms.pathfinding.models import GridMap
from algorithms.pathfinding.registry import PATHFINDING_ALGORITHMS, get_pathfinder
from algorithms.pathfinding.astar import AStarPathfinder

def is_path_continuous(path):
    """Verify that every consecutive pair of coordinates in the path is adjacent."""
    for i in range(len(path) - 1):
        r1, c1 = path[i]
        r2, c2 = path[i + 1]
        dist = abs(r1 - r2) + abs(c1 - c2)
        if dist != 1:
            return False
    return True

@pytest.mark.parametrize("slug", list(PATHFINDING_ALGORITHMS.keys()))
def test_simple_reachable_path(slug):
    """Test that all algorithms successfully find a continuous path in an open grid."""
    grid = GridMap(rows=10, cols=10, start=(1, 1), target=(8, 8))
    pathfinder = get_pathfinder(slug)
    events, path, cost = pathfinder.search(grid)

    assert len(path) > 0, f"{slug} failed to find path in open grid"
    assert path[0] == (1, 1)
    assert path[-1] == (8, 8)
    assert is_path_continuous(path)
    assert cost > 0

def test_bfs_shortest_path():
    """Verify BFS finds the exact minimum Manhattan path length in an unweighted grid."""
    grid = GridMap(rows=10, cols=10, start=(2, 2), target=(7, 7))
    bfs = get_pathfinder("bfs")
    _, path, cost = bfs.search(grid)

    # In open grid, shortest path length is Manhattan distance: |7-2| + |7-2| = 10 steps (11 nodes)
    expected_steps = 10
    assert cost == expected_steps
    assert len(path) == expected_steps + 1

@pytest.mark.parametrize("slug", list(PATHFINDING_ALGORITHMS.keys()))
def test_blocked_path_no_solution(slug):
    """Test that all algorithms gracefully report failure when destination is surrounded by walls."""
    grid = GridMap(rows=10, cols=10, start=(1, 1), target=(5, 5))
    # Wall off target (5, 5) completely
    grid.walls.add((4, 5))
    grid.walls.add((6, 5))
    grid.walls.add((5, 4))
    grid.walls.add((5, 6))

    pathfinder = get_pathfinder(slug)
    events, path, cost = pathfinder.search(grid)

    assert len(path) == 0
    assert cost == 0

def test_start_equals_target():
    """Test edge case where start is identical to destination."""
    for slug in PATHFINDING_ALGORITHMS.keys():
        grid = GridMap(rows=10, cols=10, start=(3, 3), target=(3, 3))
        pathfinder = get_pathfinder(slug)
        _, path, cost = pathfinder.search(grid)
        assert path == [(3, 3)]
        assert cost == 0

def test_dijkstra_and_astar_weighted_terrain():
    """Verify Dijkstra and A* correctly navigate around high-cost weighted cells."""
    # 5x5 grid with start at (2, 0) and target at (2, 4)
    grid = GridMap(rows=5, cols=5, start=(2, 0), target=(2, 4))
    # Place a heavy weight wall in column 2 except at top (0, 2)
    grid.weights[(1, 2)] = 10
    grid.weights[(2, 2)] = 10
    grid.weights[(3, 2)] = 10
    grid.weights[(4, 2)] = 10

    dijkstra = get_pathfinder("dijkstra")
    astar = get_pathfinder("astar")

    _, d_path, d_cost = dijkstra.search(grid)
    _, a_path, a_cost = astar.search(grid)

    assert d_cost == a_cost, f"Dijkstra cost {d_cost} != A* cost {a_cost}"
    # The optimal path must route through row 0 where weight is 1
    assert (0, 2) in d_path
    assert (0, 2) in a_path

def test_astar_heuristic_admissibility():
    """Confirm Manhattan heuristic never overestimates distance."""
    for r1 in range(5):
        for c1 in range(5):
            for r2 in range(5):
                for c2 in range(5):
                    h = AStarPathfinder.heuristic((r1, c1), (r2, c2))
                    true_manhattan = abs(r1 - r2) + abs(c1 - c2)
                    assert h == true_manhattan
                    assert h >= 0
