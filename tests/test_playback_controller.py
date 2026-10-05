"""Tests for PlaybackController forward/backward steps, speed, and state transitions."""
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from engine.playback_controller import PlaybackController
from engine.run_state import RunState
from algorithms.sorting.registry import get_sorting_algorithm

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

def test_playback_controller_forward_and_backward(qapp):
    controller = PlaybackController()
    algo = get_sorting_algorithm("insertion_sort")
    arr = [5, 2, 8, 1, 9]
    events = algo.generate_events(arr)

    controller.load_events(arr, events)
    assert controller.total_steps == len(events)
    assert controller.current_step == 0
    assert controller.state == RunState.IDLE

    # Step forward 3 times
    assert controller.step_forward() is True
    assert controller.current_step == 1

    assert controller.step_forward() is True
    assert controller.current_step == 2

    assert controller.step_forward() is True
    assert controller.current_step == 3

    # Step backward 2 times
    assert controller.step_backward() is True
    assert controller.current_step == 2

    assert controller.step_backward() is True
    assert controller.current_step == 1

    # Step backward back to 0
    assert controller.step_backward() is True
    assert controller.current_step == 0

    # Stepping backward when already at 0 should return False safely
    assert controller.step_backward() is False
    assert controller.current_step == 0

def test_playback_controller_reset_and_boundaries(qapp):
    controller = PlaybackController()
    algo = get_sorting_algorithm("selection_sort")
    arr = [3, 1, 2]
    events = algo.generate_events(arr)
    controller.load_events(arr, events)

    # Step to completion
    while controller.current_step < controller.total_steps:
        controller.step_forward()

    assert controller.state == RunState.FINISHED
    # Stepping forward past finished returns False
    assert controller.step_forward() is False

    # Reset
    controller.reset()
    assert controller.state == RunState.IDLE
    assert controller.current_step == 0
