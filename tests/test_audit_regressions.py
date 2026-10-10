"""Regression tests covering all issues identified during the Algorithm Arena project audit."""
import pytest
from PySide6.QtWidgets import QApplication

from app.application import create_application
from app.settings import MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
from algorithms.pathfinding.models import GridMap, PathEventType
from algorithms.pathfinding.bfs import BFSPathfinder
from algorithms.pathfinding.dfs import DFSPathfinder
from algorithms.pathfinding.dijkstra import DijkstraPathfinder
from algorithms.pathfinding.astar import AStarPathfinder
from algorithms.pathfinding.registry import PATHFINDING_ALGORITHMS, get_pathfinder
from algorithms.backtracking.nqueens import NQueensSolver, NQueensEventType
from engine.nqueens_controller import NQueensPlaybackController
from engine.playback_controller import PlaybackController
from engine.pathfinding_controller import PathfindingPlaybackController
from engine.run_state import RunState
from ui.sorting_page import SortingPage
from ui.pathfinding_page import PathfindingPage
from ui.nqueens_page import NQueensPage


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app


# ============================================================================
# 1. Pathfinding Weighted Cost and Path Length Regressions
# ============================================================================

def test_bfs_and_dfs_weighted_grid_cost_calculation():
    """Verify BFS and DFS compute accurate path costs when traversing weighted cells."""
    grid = GridMap(rows=6, cols=6, start=(0, 0), target=(2, 2))
    # Place weights along path
    grid.weights[(1, 0)] = 5
    grid.weights[(0, 1)] = 5

    bfs = BFSPathfinder()
    _, bfs_path, bfs_cost = bfs.search(grid)
    assert len(bfs_path) > 0
    actual_bfs_cost = sum(grid.get_cost(*p) for p in bfs_path[1:])
    assert bfs_cost == actual_bfs_cost, f"BFS returned cost {bfs_cost} != actual {actual_bfs_cost}"

    dfs = DFSPathfinder()
    _, dfs_path, dfs_cost = dfs.search(grid)
    assert len(dfs_path) > 0
    actual_dfs_cost = sum(grid.get_cost(*p) for p in dfs_path[1:])
    assert dfs_cost == actual_dfs_cost, f"DFS returned cost {dfs_cost} != actual {actual_dfs_cost}"


@pytest.mark.parametrize("slug", list(PATHFINDING_ALGORITHMS.keys()))
def test_all_pathfinders_unreachable_grid(slug):
    """Verify BFS, DFS, Dijkstra, and A* on completely walled-off targets."""
    grid = GridMap(rows=5, cols=5, start=(0, 0), target=(4, 4))
    # Wall off target completely
    grid.walls.update({(3, 4), (4, 3)})

    pathfinder = get_pathfinder(slug)
    events, path, cost = pathfinder.search(grid)

    assert path == []
    assert cost == 0
    assert events[-1].event_type == PathEventType.NO_PATH


@pytest.mark.parametrize("slug", list(PATHFINDING_ALGORITHMS.keys()))
def test_path_length_steps_vs_nodes_definition(slug):
    """Verify that path length in steps is strictly len(path) - 1, matching graph edge count."""
    grid = GridMap(rows=8, cols=8, start=(1, 1), target=(4, 4))
    pathfinder = get_pathfinder(slug)
    events, path, cost = pathfinder.search(grid)

    assert len(path) > 1
    expected_steps = len(path) - 1
    last_ev = events[-1]
    assert last_ev.event_type == PathEventType.FOUND_PATH
    assert f"Length: {expected_steps} steps ({len(path)} nodes)" in last_ev.description


# ============================================================================
# 2. N-Queens Solution Counts, Counting Definitions & Invariants (N=4..10)
# ============================================================================

@pytest.mark.parametrize("n, expected_solutions", [
    (4, 2),
    (5, 10),
    (6, 4),
    (7, 40),
    (8, 92),
    (9, 352),
    (10, 724),
])
def test_nqueens_solution_counts_n4_to_n10(n, expected_solutions):
    """Verify N-Queens solution counts for all supported sizes (N=4 through 10) against OEIS A000170."""
    solver = NQueensSolver()
    events, solutions = solver.solve(n, find_one=False)

    assert len(solutions) == expected_solutions
    for sol in solutions:
        assert solver.is_valid_solution(sol) is True


def test_nqueens_counting_definitions_and_invariants():
    """Verify counting definitions: attempts = conflicts + placements, placements = backtracks."""
    solver = NQueensSolver()
    # Check on N=4 and N=5 for fast invariant verification
    for n in (4, 5):
        events, solutions = solver.solve(n, find_one=False)
        attempts = sum(1 for e in events if e.event_type == NQueensEventType.TRY_CANDIDATE)
        conflicts = sum(1 for e in events if e.event_type == NQueensEventType.CONFLICT)
        placements = sum(1 for e in events if e.event_type == NQueensEventType.PLACE_QUEEN)
        backtracks = sum(1 for e in events if e.event_type == NQueensEventType.BACKTRACK)
        solutions_count = sum(1 for e in events if e.event_type == NQueensEventType.SOLUTION_FOUND)

        assert attempts == conflicts + placements, f"N={n}: attempts ({attempts}) != conflicts ({conflicts}) + placements ({placements})"
        assert placements == backtracks, f"N={n}: placements ({placements}) != backtracks ({backtracks})"
        assert len(solutions) == solutions_count
        # Total events = attempts + conflicts + placements + backtracks + solutions + 1 (SEARCH_COMPLETE)
        assert len(events) == attempts + conflicts + placements + backtracks + solutions_count + 1


def test_nqueens_controller_cumulative_stats_with_backtracks():
    """Verify NQueensPlaybackController accurately counts and emits backtrack events."""
    solver = NQueensSolver()
    events, _ = solver.solve(4, find_one=False)
    controller = NQueensPlaybackController()

    emitted_stats = []
    controller.stats_updated.connect(lambda att, cnf, bck, sols, dep, el: emitted_stats.append((att, cnf, bck, sols, dep)))

    controller.load_events(events)
    assert controller.total_steps == len(events)
    assert emitted_stats[-1] == (0, 0, 0, 0, 0)

    # Step through all events
    while controller.step_forward():
        pass

    final_att, final_cnf, final_bck, final_sols, _ = emitted_stats[-1]
    assert final_sols == 2
    assert final_att == 60
    assert final_cnf == 44
    assert final_bck == 16


# ============================================================================
# 3. Playback Controls Boundary Behavior and State Machine
# ============================================================================

def test_sorting_playback_controller_boundary_behavior():
    """Verify step_backward at step 0 and step_forward at max step."""
    controller = PlaybackController()
    from algorithms.sorting.bubble_sort import BubbleSort
    arr = [5, 3, 1]
    events = BubbleSort().generate_events(arr)
    controller.load_events(arr, events)

    assert controller.current_step == 0
    # At step 0, step_backward returns False
    assert controller.step_backward() is False
    assert controller.current_step == 0

    # Step to the end
    while controller.step_forward():
        pass

    assert controller.current_step == len(events)
    # At end, step_forward returns False
    assert controller.step_forward() is False
    assert controller.state == RunState.FINISHED

    # Reset returns to idle
    controller.reset()
    assert controller.current_step == 0
    assert controller.state == RunState.IDLE


def test_pathfinding_playback_controller_boundary_behavior():
    """Verify boundary behavior for PathfindingPlaybackController."""
    grid = GridMap(rows=4, cols=4, start=(0, 0), target=(2, 2))
    events, _, _ = BFSPathfinder().search(grid)
    controller = PathfindingPlaybackController()
    controller.load_events(events)

    assert controller.current_step == 0
    assert controller.step_backward() is False

    while controller.step_forward():
        pass

    assert controller.current_step == len(events)
    assert controller.step_forward() is False
    assert controller.state == RunState.FINISHED


# ============================================================================
# 4. UI Layout, Minimum Sizes, and Dynamic Button States
# ============================================================================

def test_settings_min_window_width():
    """Verify minimum window width is at least 1100px to ensure columns never cramp."""
    assert MIN_WINDOW_WIDTH >= 1100
    assert MIN_WINDOW_HEIGHT >= 650


def test_sorting_page_ui_button_states_and_minimum_width(qapp):
    """Verify SortingPage step buttons enabled states at step 0 and after stepping."""
    page = SortingPage()
    page.show()

    # Initially at step 0
    assert page.step_back_btn.isEnabled() is False
    assert page.step_fwd_btn.isEnabled() is True
    assert page.play_btn.isEnabled() is True

    # Step forward once
    page.step_fwd_btn.click()
    assert page.controller.current_step == 1
    assert page.step_back_btn.isEnabled() is True

    # Reset
    page.reset_btn.click()
    assert page.controller.current_step == 0
    assert page.step_back_btn.isEnabled() is False
    assert page.step_fwd_btn.isEnabled() is True

    page.close()


def test_pathfinding_page_ui_button_states(qapp):
    """Verify PathfindingPage step buttons enabled states."""
    page = PathfindingPage()
    page.show()

    assert page.step_back_btn.isEnabled() is False
    assert page.step_fwd_btn.isEnabled() is True

    page.step_fwd_btn.click()
    assert page.controller.current_step == 1
    assert page.step_back_btn.isEnabled() is True

    page.reset_btn.click()
    assert page.controller.current_step == 0
    assert page.step_back_btn.isEnabled() is False

    page.close()


def test_nqueens_page_ui_button_states_and_backtrack_card(qapp):
    """Verify NQueensPage step buttons and backtracks stat box."""
    page = NQueensPage()
    page.show()

    assert hasattr(page, "stat_backtracks")
    assert page.stat_backtracks.text() == "0"
    assert page.step_back_btn.isEnabled() is False
    assert page.step_fwd_btn.isEnabled() is True

    page.step_fwd_btn.click()
    assert page.controller.current_step == 1
    assert page.step_back_btn.isEnabled() is True

    page.reset_btn.click()
    assert page.controller.current_step == 0
    assert page.step_back_btn.isEnabled() is False

    page.close()
