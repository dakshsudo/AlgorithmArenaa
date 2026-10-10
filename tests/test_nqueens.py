"""Automated tests for N-Queens backtracking solver, solution counts, and UI."""
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from algorithms.backtracking.nqueens import NQueensSolver
from ui.nqueens_page import NQueensPage

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

@pytest.mark.parametrize("n, expected_count", [
    (4, 2),
    (5, 10),
    (6, 4),
    (7, 40),
    (8, 92),
])
def test_nqueens_known_solution_counts(n, expected_count):
    """Verify that the solver discovers the exact mathematical count of solutions."""
    solver = NQueensSolver()
    events, solutions = solver.solve(n, find_one=False)
    assert len(solutions) == expected_count, f"N={n}: expected {expected_count} solutions, got {len(solutions)}"

def test_nqueens_all_solutions_validity():
    """Verify that every generated solution for N=4 through 8 has 0 conflicts."""
    solver = NQueensSolver()
    for n in range(4, 9):
        _, solutions = solver.solve(n, find_one=False)
        for sol in solutions:
            assert len(sol) == n
            assert solver.is_valid_solution(sol) is True, f"Invalid solution {sol} for N={n}"

def test_nqueens_find_one_mode():
    """Verify find_one mode stops immediately upon finding the first valid solution."""
    solver = NQueensSolver()
    for n in range(4, 9):
        events, solutions = solver.solve(n, find_one=True)
        assert len(solutions) == 1
        assert solver.is_valid_solution(solutions[0]) is True

from engine.nqueens_controller import NQueensPlaybackController
from engine.run_state import RunState

def test_nqueens_page_ui(qapp):
    page = NQueensPage()
    assert page.current_n == 8
    assert page.controller.total_steps > 0
    assert page.status_badge.text() == "Status: Ready to Search"

    # Step forward and backward
    assert page.controller.step_forward() is True
    assert page.controller.current_step == 1
    assert page.controller.step_backward() is True
    assert page.controller.current_step == 0

    # Change to N=4
    idx = page.size_combo.findData(4)
    page.size_combo.setCurrentIndex(idx)
    assert page.current_n == 4

    page.close()


def test_nqueens_controller_completion_tuple_unpacking():
    """Regression test: verify completion unpacking does not raise ValueError and correctly updates all metrics."""
    solver = NQueensSolver()
    events, _ = solver.solve(4, find_one=False)
    controller = NQueensPlaybackController()

    finished_records = []
    stats_records = []
    step_records = []

    controller.finished.connect(lambda sols, att, cnf, msg: finished_records.append((sols, att, cnf, msg)))
    controller.stats_updated.connect(lambda att, cnf, bck, sols, dep, el: stats_records.append((att, cnf, bck, sols, dep, el)))
    controller.step_changed.connect(lambda curr, total, ev: step_records.append((curr, total, ev)))

    controller.load_events(events)

    # Step to the end
    while controller.step_forward():
        pass

    # Verify controller state
    assert controller.state == RunState.FINISHED
    assert controller.current_step == len(events)
    assert controller.total_steps == len(events)

    # Verify finished signal was emitted
    assert len(finished_records) == 1
    sols, att, cnf, msg = finished_records[0]
    assert sols == 2
    assert att == 60
    assert cnf == 44
    assert "Search complete! Found 2 solution(s) with 60 attempts and 44 conflicts." in msg

    # Verify final stats_updated emission
    assert len(stats_records) > 0
    final_att, final_cnf, final_bck, final_sols, final_depth, _ = stats_records[-1]
    assert final_att == 60
    assert final_cnf == 44
    assert final_bck == 16
    assert final_sols == 2

    # Verify step_changed updated step index to total steps
    curr_step, total_steps, last_ev = step_records[-1]
    assert curr_step == len(events)
    assert total_steps == len(events)
    assert last_ev is not None


def test_nqueens_controller_empty_stats_history_safe():
    """Verify controller handles an empty statistics history safely without crashing."""
    controller = NQueensPlaybackController()

    finished_records = []
    stats_records = []
    step_records = []

    controller.finished.connect(lambda sols, att, cnf, msg: finished_records.append((sols, att, cnf, msg)))
    controller.stats_updated.connect(lambda att, cnf, bck, sols, dep, el: stats_records.append((att, cnf, bck, sols, dep, el)))
    controller.step_changed.connect(lambda curr, total, ev: step_records.append((curr, total, ev)))

    controller.load_events([])
    assert controller.total_steps == 0
    assert controller.current_step == 0

    # Trigger completion on empty history
    controller._handle_completion()

    assert controller.state == RunState.FINISHED
    assert len(finished_records) == 1
    sols, att, cnf, msg = finished_records[0]
    assert sols == 0
    assert att == 0
    assert cnf == 0
    assert "Found 0 solution(s)" in msg

    assert len(stats_records) > 0
    assert stats_records[-1][:5] == (0, 0, 0, 0, 0)

    assert len(step_records) > 0
    assert step_records[-1] == (0, 0, None)


def test_nqueens_controller_completion_executes_only_once_per_run():
    """Verify that the completion handler executes only once per completed run."""
    solver = NQueensSolver()
    events, _ = solver.solve(4, find_one=True)
    controller = NQueensPlaybackController()

    finished_calls = []
    controller.finished.connect(lambda sols, att, cnf, msg: finished_calls.append((sols, att, cnf, msg)))

    controller.load_events(events)

    while controller.step_forward():
        pass

    assert len(finished_calls) == 1
    assert controller.state == RunState.FINISHED

    # Simulate subsequent timer ticks or redundant completion calls
    controller._on_tick()
    controller._handle_completion()
    controller._handle_completion()

    # Must still be called exactly once
    assert len(finished_calls) == 1

    # Reset and run again - should allow completion once more for the new run
    controller.reset()
    assert controller.state == RunState.IDLE

    while controller.step_forward():
        pass

    assert len(finished_calls) == 2


def test_nqueens_playback_controller_boundary_behavior():
    """Verify boundary behavior for NQueensPlaybackController: step_backward at 0 and step_forward at max step."""
    solver = NQueensSolver()
    events, _ = solver.solve(4, find_one=True)
    controller = NQueensPlaybackController()
    controller.load_events(events)

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

    # Step backward from finished state moves to PAUSED
    assert controller.step_backward() is True
    assert controller.state == RunState.PAUSED
    assert controller.current_step == len(events) - 1

    # Reset returns to idle
    controller.reset()
    assert controller.current_step == 0
    assert controller.state == RunState.IDLE


def test_nqueens_page_ui_completion(qapp):
    """Verify NQueensPage UI correctly reflects completion state and message."""
    page = NQueensPage()
    # Switch to N=4 find_one for quick completion
    page.size_combo.setCurrentIndex(page.size_combo.findData(4))
    page.mode_combo.setCurrentIndex(page.mode_combo.findData(True))

    while page.controller.step_forward():
        pass

    assert page.controller.state == RunState.FINISHED
    assert "✓ Search complete!" in page.status_badge.text()
    assert page.step_fwd_btn.isEnabled() is False
    assert page.step_back_btn.isEnabled() is True
    assert page.play_btn.text() == "↺ Restart"
    assert page.stat_solutions.text() == "1"

    page.close()

