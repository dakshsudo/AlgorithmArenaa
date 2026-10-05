"""Custom QPainter canvas for sorting bar visualization with color highlights and baseline."""
from typing import List, Optional, Set
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

from app.theme import Colors
from engine.events import SortEvent, EventType

class SortingCanvas(QWidget):
    """Custom paint canvas rendering array values as dynamic bars with state highlights."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SortingCanvas")
        self.setMinimumHeight(340)
        
        # Current data state
        self._array: List[int] = []
        self._current_event: Optional[SortEvent] = None
        self._comparing_indices: Set[int] = set()
        self._modifying_indices: Set[int] = set()
        self._sorted_indices: Set[int] = set()
        self._pivot_index: Optional[int] = None
        self._range_bounds: Optional[tuple] = None
        
        # Color definitions
        self._c_bg = QColor(Colors.BG_SURFACE)
        self._c_default = QColor("#38bdf8")       # Sky
        self._c_compare = QColor("#f59e0b")       # Amber
        self._c_swap = QColor("#f43f5e")          # Rose
        self._c_sorted = QColor("#10b981")        # Emerald
        self._c_pivot = QColor("#c084fc")         # Purple
        self._c_merge_bg = QColor(56, 189, 248, 25) # Transparent sky
        self._c_text = QColor(Colors.TEXT_PRIMARY)
        self._c_muted = QColor(Colors.TEXT_MUTED)
        self._c_border = QColor(Colors.BORDER_DEFAULT)

    def set_array(self, arr: List[int]):
        """Set or update the base array to visualize."""
        self._array = list(arr)
        self._current_event = None
        self._comparing_indices.clear()
        self._modifying_indices.clear()
        self._sorted_indices.clear()
        self._pivot_index = None
        self._range_bounds = None
        self.update()

    def set_event(self, event: Optional[SortEvent]):
        """Update canvas based on the active event."""
        self._current_event = event
        self._comparing_indices.clear()
        self._modifying_indices.clear()
        self._pivot_index = None
        self._range_bounds = None

        if event is not None:
            # Sync array state if snapshot is present
            if event.array_snapshot:
                self._array = list(event.array_snapshot)
                
            self._sorted_indices = set(event.sorted_indices)
            self._range_bounds = event.range_bounds
            self._pivot_index = event.pivot_index

            if event.event_type == EventType.COMPARE:
                self._comparing_indices = set(event.indices)
            elif event.event_type in (EventType.SWAP, EventType.WRITE):
                self._modifying_indices = set(event.indices)
            elif event.event_type == EventType.PIVOT:
                if event.indices:
                    self._pivot_index = event.indices[0]

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # 1. Background fill
        painter.fillRect(0, 0, width, height, self._c_bg)

        # Draw subtle border
        painter.setPen(QPen(self._c_border, 1))
        painter.drawRect(0, 0, width - 1, height - 1)

        if not self._array:
            # Empty state message
            painter.setPen(self._c_muted)
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(
                QRectF(0, 0, width, height),
                Qt.AlignmentFlag.AlignCenter,
                "No array data. Generate an array or enter custom values."
            )
            return

        n = len(self._array)
        padding_x = 24
        padding_top = 28
        padding_bottom = 44
        chart_width = width - 2 * padding_x
        chart_height = height - padding_top - padding_bottom

        # Compute range of values
        min_val = min(self._array)
        max_val = max(self._array)

        # Ensure we avoid division by zero
        if min_val == max_val:
            if min_val >= 0:
                min_val = 0
                max_val = max(1, max_val)
            else:
                max_val = 0
                min_val = min(-1, min_val)
        else:
            if min_val > 0:
                min_val = 0
            if max_val < 0:
                max_val = 0

        val_span = max_val - min_val
        if val_span == 0:
            val_span = 1

        # Baseline Y position (where value == 0)
        # If min_val >= 0, baseline is at bottom of chart
        # If min_val < 0, baseline is proportional
        zero_ratio = (max_val - 0) / val_span
        baseline_y = padding_top + zero_ratio * chart_height

        # Highlight merge range if active
        if self._range_bounds and len(self._range_bounds) == 2:
            r_left, r_right = self._range_bounds
            if 0 <= r_left <= r_right < n:
                slot_w = chart_width / n
                rx = padding_x + r_left * slot_w
                rw = (r_right - r_left + 1) * slot_w
                painter.fillRect(
                    QRectF(rx, padding_top - 6, rw, chart_height + 12),
                    self._c_merge_bg
                )
                painter.setPen(QPen(QColor(Colors.SECONDARY), 1, Qt.PenStyle.DashLine))
                painter.drawRect(QRectF(rx, padding_top - 6, rw, chart_height + 12))

        # Draw baseline line
        painter.setPen(QPen(QColor(Colors.BORDER_ACTIVE), 1, Qt.PenStyle.DashLine))
        painter.drawLine(padding_x, int(baseline_y), width - padding_x, int(baseline_y))

        # Bar sizing
        slot_width = chart_width / n
        gap = max(1.0, slot_width * 0.15) if n < 60 else (0.5 if n < 85 else 0.0)
        bar_width = max(1.5, slot_width - gap)

        # Draw individual bars
        font_bars = QFont("Segoe UI", 9, QFont.Weight.Bold)
        font_indices = QFont("Segoe UI", 8)

        for i, val in enumerate(self._array):
            x = padding_x + i * slot_width + (slot_width - bar_width) / 2

            # Compute height from baseline
            bar_h = (abs(val) / val_span) * chart_height
            if bar_h < 3:
                bar_h = 3  # Ensure bar is visible

            if val >= 0:
                y = baseline_y - bar_h
            else:
                y = baseline_y

            # Determine color state
            if i in self._sorted_indices:
                bar_color = self._c_sorted
            elif i == self._pivot_index:
                bar_color = self._c_pivot
            elif i in self._modifying_indices:
                bar_color = self._c_swap
            elif i in self._comparing_indices:
                bar_color = self._c_compare
            else:
                bar_color = self._c_default

            # Draw bar
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bar_color))
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_h), 2, 2)

            # Draw value text if array is small enough
            if n <= 32:
                painter.setFont(font_bars)
                painter.setPen(self._c_text)
                text_rect = QRectF(x - 10, y - 18 if val >= 0 else y + bar_h + 2, bar_width + 20, 16)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(val))

            # Draw index below chart
            if n <= 28:
                painter.setFont(font_indices)
                painter.setPen(self._c_muted)
                idx_rect = QRectF(x - 5, height - padding_bottom + 4, bar_width + 10, 14)
                painter.drawText(idx_rect, Qt.AlignmentFlag.AlignCenter, str(i))
