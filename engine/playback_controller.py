"""Deterministic playback controller with forward, backward, pause, and speed controls."""
import time
from typing import List, Optional
from PySide6.QtCore import QObject, QTimer, Signal

from engine.events import SortEvent, EventType
from engine.run_state import RunState
from services.validation_service import ValidationService

class PlaybackController(QObject):
    """Controls the step-by-step playback of an algorithm's event trace."""

    # Signals
    step_changed = Signal(int, int, object)  # (current_step, total_steps, current_event)
    state_changed = Signal(str)              # (new_state.value)
    stats_updated = Signal(int, int, int, int) # (comparisons, swaps, writes, elapsed_ms)
    finished = Signal(bool, str)             # (is_correct, status_msg)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._events: List[SortEvent] = []
        self._initial_array: List[int] = []
        self._current_index: int = -1
        self._state: RunState = RunState.IDLE
        
        # Cumulative stats cache per step for instant step-backward
        self._cumulative_stats: List[tuple] = [] # (comparisons, swaps, writes)
        
        # Timer for automatic playback
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)
        self._delay_ms: int = 150
        
        # Timing
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
        """Set step interval in milliseconds."""
        self._delay_ms = max(5, delay_ms)
        if self._timer.isActive():
            self._timer.setInterval(self._delay_ms)

    def load_events(self, initial_array: List[int], events: List[SortEvent]):
        """Load an event sequence and precompute cumulative statistics."""
        self.reset()
        self._initial_array = list(initial_array)
        self._events = list(events)
        self._current_index = -1
        self._elapsed_ms = 0

        # Precompute running counts for O(1) forward/backward updates
        self._cumulative_stats.clear()
        c_count = 0
        s_count = 0
        w_count = 0

        for ev in self._events:
            if ev.event_type == EventType.COMPARE:
                c_count += 1
            elif ev.event_type == EventType.SWAP:
                s_count += 1
            elif ev.event_type == EventType.WRITE:
                w_count += 1
            self._cumulative_stats.append((c_count, s_count, w_count))

        self.step_changed.emit(0, len(self._events), None)
        self.stats_updated.emit(0, 0, 0, 0)
        self._set_state(RunState.IDLE)

    def play(self):
        """Start or resume playback."""
        if not self._events:
            return

        if self._state == RunState.FINISHED:
            self.reset()

        self._set_state(RunState.RUNNING)
        self._last_tick_time = time.perf_counter()
        self._timer.start(self._delay_ms)

    def pause(self):
        """Pause running playback."""
        if self._state == RunState.RUNNING:
            self._timer.stop()
            self._update_elapsed()
            self._set_state(RunState.PAUSED)

    def resume(self):
        """Resume paused playback."""
        if self._state == RunState.PAUSED:
            self.play()

    def reset(self):
        """Reset playback to the initial state."""
        self._timer.stop()
        self._current_index = -1
        self._elapsed_ms = 0
        self.step_changed.emit(0, len(self._events), None)
        self.stats_updated.emit(0, 0, 0, 0)
        self._set_state(RunState.IDLE)

    def step_forward(self) -> bool:
        """Advance one step forward."""
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
        """Step one step backward to restore previous state."""
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
            self.stats_updated.emit(0, 0, 0, self._elapsed_ms)
            self._set_state(RunState.IDLE)
            return True
        return False

    def _on_timer_tick(self):
        """Timer callback to step forward."""
        self._update_elapsed()
        if self._current_index < len(self._events) - 1:
            self._current_index += 1
            self._emit_current_step()
            if self._current_index >= len(self._events) - 1:
                self._handle_completion()
        else:
            self._handle_completion()

    def _emit_current_step(self):
        event = self._events[self._current_index]
        c, s, w = self._cumulative_stats[self._current_index]
        self.step_changed.emit(self._current_index + 1, len(self._events), event)
        self.stats_updated.emit(c, s, w, self._elapsed_ms)

    def _update_elapsed(self):
        now = time.perf_counter()
        delta_ms = int((now - self._last_tick_time) * 1000)
        if delta_ms > 0:
            self._elapsed_ms += delta_ms
            self._last_tick_time = now

    def _handle_completion(self):
        self._timer.stop()
        self._set_state(RunState.FINISHED)
        
        # Verify correctness against original input
        if self._events and self._events[-1].array_snapshot:
            final_arr = self._events[-1].array_snapshot
        else:
            final_arr = self._initial_array

        is_valid, msg = ValidationService.verify_sorted_correctness(self._initial_array, final_arr)
        self.finished.emit(is_valid, msg)

    def _set_state(self, new_state: RunState):
        self._state = new_state
        self.state_changed.emit(new_state.value)
