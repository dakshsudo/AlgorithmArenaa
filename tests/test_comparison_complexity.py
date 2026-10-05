"""Automated tests for Comparison and Complexity labs."""
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from services.comparison_service import ComparisonService
from services.complexity_service import ComplexityService, COMPLEXITY_CLASSES
from algorithms.pathfinding.models import GridMap
from ui.comparison_page import ComparisonPage
from ui.complexity_page import ComplexityPage

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

def test_comparison_service_sorting():
    slugs = ["bubble_sort", "merge_sort", "quick_sort"]
    arr = [45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 45, 8]
    original_copy = list(arr)

    results = ComparisonService.compare_sorting(slugs, arr)
    assert len(results) == 3
    # Verify input was untouched (independent clone)
    assert arr == original_copy

    for res in results:
        assert res.is_correct is True
        assert res.runtime_ms >= 0.0
        assert res.comparisons > 0

def test_comparison_service_pathfinding():
    slugs = ["bfs", "dijkstra", "astar"]
    grid = GridMap(rows=10, cols=10, start=(1, 1), target=(8, 8))
    results = ComparisonService.compare_pathfinding(slugs, grid)

    assert len(results) == 3
    for res in results:
        assert res.path_found is True
        assert res.path_length > 0
        assert res.runtime_ms >= 0.0

def test_complexity_service_math():
    n = 16
    assert ComplexityService.compute_value("O(1)", n) == 1.0
    assert ComplexityService.compute_value("O(log n)", n) == 4.0
    assert ComplexityService.compute_value("O(n)", n) == 16.0
    assert ComplexityService.compute_value("O(n log n)", n) == 64.0
    assert ComplexityService.compute_value("O(n²)", n) == 256.0
    assert ComplexityService.compute_value("O(2ⁿ)", n) == 65536.0

def test_comparison_page_ui(qapp):
    page = ComparisonPage()
    assert page.table.rowCount() == 6
    # Switch to pathfinding
    idx = page.cat_combo.findData("pathfinding")
    page.cat_combo.setCurrentIndex(idx)
    assert page.table.rowCount() == 4
    page.close()

def test_complexity_page_ui(qapp):
    page = ComplexityPage()
    assert page.values_table.rowCount() == len(COMPLEXITY_CLASSES)
    page.n_slider.setValue(10)
    assert page.n_label.text() == "N = 10"
    page.close()
