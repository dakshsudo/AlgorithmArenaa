"""Phase 1 smoke tests: verify app creation, window initialization, and navigation."""
import sys
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from ui.main_window import MainWindow
from app.navigation import NavDestination, NAV_ITEMS

@pytest.fixture(scope="session")
def qapp():
    """Ensure QApplication instance is initialized for tests."""
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

def test_main_window_initialization(qapp):
    """Test MainWindow instantiates with correct titles, sizes, and layout."""
    window = MainWindow()
    assert window is not None
    assert "Algorithm Arena" in window.windowTitle()
    assert window.minimumWidth() >= 1000
    assert window.minimumHeight() >= 650
    assert window.stack.count() == 7
    window.close()

def test_all_destinations_registered(qapp):
    """Verify that all expected navigation items are registered in the page map."""
    window = MainWindow()
    expected_keys = [
        NavDestination.DASHBOARD.value,
        NavDestination.SORTING.value,
        NavDestination.PATHFINDING.value,
        NavDestination.NQUEENS.value,
        NavDestination.COMPARISON.value,
        NavDestination.COMPLEXITY.value,
        NavDestination.LEARNING.value,
    ]
    for key in expected_keys:
        assert key in window.page_map, f"Missing page for {key}"
        assert window.page_map[key] is not None
        assert key in window.nav_buttons, f"Missing button for {key}"
    window.close()

def test_navigation_switching(qapp):
    """Verify that navigate_to actually switches the active widget and updates buttons."""
    window = MainWindow()
    
    # Switch to Sorting
    window.navigate_to(NavDestination.SORTING.value)
    assert window.stack.currentWidget() == window.page_map[NavDestination.SORTING.value]
    assert window.nav_buttons[NavDestination.SORTING.value].isChecked()
    
    # Switch to Pathfinding
    window.navigate_to(NavDestination.PATHFINDING.value)
    assert window.stack.currentWidget() == window.page_map[NavDestination.PATHFINDING.value]
    assert window.nav_buttons[NavDestination.PATHFINDING.value].isChecked()
    
    # Switch to N-Queens
    window.navigate_to(NavDestination.NQUEENS.value)
    assert window.stack.currentWidget() == window.page_map[NavDestination.NQUEENS.value]
    assert window.nav_buttons[NavDestination.NQUEENS.value].isChecked()
    
    # Switch to Dashboard
    window.navigate_to(NavDestination.DASHBOARD.value)
    assert window.stack.currentWidget() == window.page_map[NavDestination.DASHBOARD.value]
    assert window.nav_buttons[NavDestination.DASHBOARD.value].isChecked()
    
    window.close()

def test_dashboard_card_navigation_signal(qapp):
    """Verify dashboard emits navigate_requested signal when card is triggered."""
    window = MainWindow()
    dashboard = window.page_map[NavDestination.DASHBOARD.value]
    
    # Trigger signal
    dashboard.navigate_requested.emit(NavDestination.COMPLEXITY.value)
    assert window.stack.currentWidget() == window.page_map[NavDestination.COMPLEXITY.value]
    assert window.nav_buttons[NavDestination.COMPLEXITY.value].isChecked()
    
    window.close()
