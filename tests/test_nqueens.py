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
