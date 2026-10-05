"""UI integration tests for SortingPage controls and interactions."""
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from ui.sorting_page import SortingPage

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

def test_sorting_page_initial_state(qapp):
    page = SortingPage()
    assert page.algo_combo.count() == 6
    assert len(page.array_data) == 20
    assert page.controller.total_steps > 0
    assert page.status_badge.text() == "Status: Ready"
    assert "O(" in page.lbl_worst.text()
    page.close()

def test_sorting_page_preset_buttons(qapp):
    page = SortingPage()
    
    # Nearly sorted
    page._generate_preset("nearly_sorted")
    assert len(page.array_data) == 20
    assert page.controller.current_step == 0
    
    # Reverse
    page._generate_preset("reverse")
    assert len(page.array_data) == 20
    assert page.array_data[0] >= page.array_data[-1]

    # Duplicates
    page._generate_preset("duplicates")
    assert len(page.array_data) == 20

    page.close()

def test_sorting_page_manual_input_validation(qapp):
    page = SortingPage()
    page.show()
    
    # Invalid input
    page.manual_input.setText("invalid, text, here")
    page._on_apply_manual_input()
    assert not page.error_label.isHidden()
    assert "Invalid integer token" in page.error_label.text()

    # Valid input
    page.manual_input.setText("45, 12, -8, 0, 99, 14")
    page._on_apply_manual_input()
    assert page.error_label.isHidden()
    assert page.array_data == [45, 12, -8, 0, 99, 14]
    assert len(page.array_data) == 6

    page.close()

def test_sorting_page_step_and_benchmark(qapp):
    page = SortingPage()
    
    # Step forward
    page.controller.step_forward()
    assert page.controller.current_step == 1
    assert "1 /" in page.stat_steps.text()

    # Step backward
    page.controller.step_backward()
    assert page.controller.current_step == 0
    assert "0 /" in page.stat_steps.text()

    # Run pure benchmark
    page._on_run_benchmark()
    assert "⚡ Benchmark:" in page.benchmark_lbl.text()
    assert "Verified ✓" in page.benchmark_lbl.text()

    page.close()
