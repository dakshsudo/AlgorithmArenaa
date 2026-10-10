"""Playback controller for pathfinding algorithms."""
import time
from typing import List, Optional
from PySide6.QtCore import QObject, QTimer, Signal

from algorithms.pathfinding.models import PathEvent, PathEventType
from engine.run_state import RunState

class PathfindingPlaybackController(QObject):
    """Controls step-by-step playback of pathfinding events."""

    step_changed = Signal(int, int, object)       # (curr_step, total_steps, PathEvent)
    state_changed = Signal(str)                   # (RunState)
    stats_updated = Signal(int, int, float, int)  # (visited_count, frontier_count, current_cost, elapsed_ms)
    finished = Signal(bool, int, int, str)        # (found_path, path_len, path_cost, message)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: List[PathEvent] = []
        self._current_index: int = -1
        self._state: RunState = RunState.IDLE

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._delay_ms: int = 40
        self._elapsed_ms: int = 0
        self._last_tick_time: float = 0.0

    @property
    def state(self) -> RunState:
        return self._state

    @property
    def current_step(self) -> int:
        return self._current_index + 1

    @property
    def total_steps(self) -> int:
        return len(self._events)

    def set_speed(self, delay_ms: int):
        self._delay_ms = max(5, delay_ms)
        if self._timer.isActive():
            self._timer.setInterval(self._delay_ms)

    def load_events(self, events: List[PathEvent]):
        self.reset()
        self._events = list(events)
        self._current_index = -1
        self._elapsed_ms = 0
        self.step_changed.emit(0, len(self._events), None)
        self.stats_updated.emit(0, 0, 0.0, 0)
        self._set_state(RunState.IDLE)

    def play(self):
        if not self._events:
            return
        if self._state == RunState.FINISHED:
            self.reset()

        self._set_state(RunState.RUNNING)
        self._last_tick_time = time.perf_counter()
        self._timer.start(self._delay_ms)

    def pause(self):
        if self._state == RunState.RUNNING:
            self._timer.stop()
            self._update_elapsed()
            self._set_state(RunState.PAUSED)

    def resume(self):
        if self._state == RunState.PAUSED:
            self.play()

    def reset(self):
        self._timer.stop()
        self._current_index = -1
        self._elapsed_ms = 0
        self.step_changed.emit(0, len(self._events), None)
        self.stats_updated.emit(0, 0, 0.0, 0)
        self._set_state(RunState.IDLE)

    def step_forward(self) -> bool:
        if self._state == RunState.RUNNING:
            self.pause()

        if self._current_index < len(self._events) - 1:
            self._current_index += 1
            self._emit_current_step()
            if self._current_index == len(self._events) - 1:
                self._handle_completion()
            return True
        return False

    def step_backward(self) -> bool:
        if self._state == RunState.RUNNING:
            self.pause()

        if self._current_index > 0:
            self._current_index -= 1
            self._emit_current_step()
            self._set_state(RunState.PAUSED)
            return True
        elif self._current_index == 0:
            self._current_index = -1
            self.step_changed.emit(0, len(self._events), None)
            self.stats_updated.emit(0, 0, 0.0, self._elapsed_ms)
            self._set_state(RunState.IDLE)
            return True
        return False

    def _on_tick(self):
        self._update_elapsed()
        if self._current_index < len(self._events) - 1:
            self._current_index += 1
            self._emit_current_step()
            if self._current_index >= len(self._events) - 1:
                self._handle_completion()
        else:
            self._handle_completion()

    def _emit_current_step(self):
        ev = self._events[self._current_index]
        visited_count = len(ev.visited_nodes)
        frontier_count = len(ev.frontier_nodes)
        self.step_changed.emit(self._current_index + 1, len(self._events), ev)
        self.stats_updated.emit(visited_count, frontier_count, ev.cost_so_far, self._elapsed_ms)

    def _update_elapsed(self):
        now = time.perf_counter()
        delta_ms = int((now - self._last_tick_time) * 1000)
        if delta_ms > 0:
            self._elapsed_ms += delta_ms
            self._last_tick_time = now

    def _handle_completion(self):
        self._timer.stop()
        self._set_state(RunState.FINISHED)
        if not self._events:
            return

        last_ev = self._events[-1]
        if last_ev.event_type == PathEventType.FOUND_PATH:
            path_steps = max(0, len(last_ev.path) - 1) if last_ev.path else 0
            path_cost = int(last_ev.cost_so_far)
            self.finished.emit(True, path_steps, path_cost, f"Target Reached! Path Length: {path_steps} steps, Cost: {path_cost}")
        else:
            self.finished.emit(False, 0, 0, "No path possible: Target is completely walled off.")

    def _set_state(self, state: RunState):
        self._state = state
        self.state_changed.emit(state.value)
