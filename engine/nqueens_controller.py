"""Playback controller for N-Queens backtracking visualizer."""
import time
from typing import List, Optional
from PySide6.QtCore import QObject, QTimer, Signal

from algorithms.backtracking.nqueens import NQueensEvent, NQueensEventType
from engine.run_state import RunState

class NQueensPlaybackController(QObject):
    """Controls step-by-step playback of N-Queens backtracking events."""

    step_changed = Signal(int, int, object)       # (curr_step, total_steps, NQueensEvent)
    state_changed = Signal(str)                   # (RunState)
    stats_updated = Signal(int, int, int, int, int) # (attempts, conflicts, solutions, depth, elapsed_ms)
    solution_discovered = Signal(int, list)       # (sol_index, queens_list)
    finished = Signal(int, int, int, str)         # (total_sols, attempts, conflicts, message)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: List[NQueensEvent] = []
        self._current_index: int = -1
        self._state: RunState = RunState.IDLE

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._delay_ms: int = 50
        self._elapsed_ms: int = 0
        self._last_tick_time: float = 0.0

        # Cumulative metrics cache for instant stepping
        self._cumulative_stats: List[tuple] = [] # (attempts, conflicts, solutions, depth)

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

    def load_events(self, events: List[NQueensEvent]):
        self.reset()
        self._events = list(events)
        self._current_index = -1
        self._elapsed_ms = 0

        # Precompute cumulative stats
        self._cumulative_stats.clear()
        att = 0
        cnf = 0
        sols = 0

        for ev in self._events:
            if ev.event_type == NQueensEventType.TRY_CANDIDATE:
                att += 1
            elif ev.event_type == NQueensEventType.CONFLICT:
                cnf += 1
            elif ev.event_type == NQueensEventType.SOLUTION_FOUND:
                sols += 1
            
            # depth is number of queens currently placed
            depth = sum(1 for q in ev.queens if q >= 0)
            self._cumulative_stats.append((att, cnf, sols, depth))

        self.step_changed.emit(0, len(self._events), None)
        self.stats_updated.emit(0, 0, 0, 0, 0)
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
        self.stats_updated.emit(0, 0, 0, 0, 0)
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
            self.stats_updated.emit(0, 0, 0, 0, self._elapsed_ms)
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
        att, cnf, sols, depth = self._cumulative_stats[self._current_index]
        self.step_changed.emit(self._current_index + 1, len(self._events), ev)
        self.stats_updated.emit(att, cnf, sols, depth, self._elapsed_ms)

        if ev.event_type == NQueensEventType.SOLUTION_FOUND and ev.solution_index is not None:
            self.solution_discovered.emit(ev.solution_index, list(ev.queens))

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

        att, cnf, sols, depth = self._cumulative_stats[-1] if self._cumulative_stats else (0, 0, 0, 0)
        msg = f"Search complete! Found {sols} solution(s) with {att} attempts and {cnf} conflicts."
        self.finished.emit(sols, att, cnf, msg)

    def _set_state(self, state: RunState):
        self._state = state
        self.state_changed.emit(state.value)
