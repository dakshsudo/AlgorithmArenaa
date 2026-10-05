"""UI integration tests for PathfindingPage."""
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from ui.pathfinding_page import PathfindingPage

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

def test_pathfinding_page_initial_state(qapp):
    page = PathfindingPage()
    assert page.algo_combo.count() == 4
    assert page.controller.total_steps > 0
    assert page.status_badge.text() == "Status: Ready to Search"
    assert "Guarantees Shortest Path:" in page.lbl_guarantee.text()
    page.close()

def test_pathfinding_page_algorithm_change(qapp):
    page = PathfindingPage()
    # Change to A*
    idx = page.algo_combo.findData("astar")
    page.algo_combo.setCurrentIndex(idx)
    assert page.current_pathfinder.metadata.slug == "astar"
    assert "Yes" in page.lbl_weights.text()
    page.close()

def test_pathfinding_page_maze_and_clear(qapp):
    page = PathfindingPage()
    page._apply_maze("river")
    assert len(page.grid.weights) > 0

    page._on_clear_all()
    assert len(page.grid.walls) == 0
    assert len(page.grid.weights) == 0

    page.close()

def test_pathfinding_page_step_controls(qapp):
    page = PathfindingPage()
    assert page.controller.step_forward() is True
    assert page.controller.current_step == 1
    assert page.controller.step_backward() is True
    assert page.controller.current_step == 0
    page.close()
