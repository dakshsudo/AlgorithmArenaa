"""Custom QPainter chart components for benchmarks and complexity curves."""
from typing import List, Dict, Tuple, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from app.theme import Colors
from services.complexity_service import COMPLEXITY_CLASSES, ComplexityService

class ComparisonBarChartView(QWidget):
    """Bar chart rendering algorithm execution benchmarks and operation counts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComparisonBarChartView")
        self.setMinimumHeight(240)

        # List of (algo_name, runtime_ms, total_ops)
        self._data: List[Tuple[str, float, int]] = []
        self._mode: str = "runtime" # "runtime" or "operations"

        self._c_bar = QColor("#38bdf8")
        self._c_text = QColor(Colors.TEXT_PRIMARY)
        self._c_muted = QColor(Colors.TEXT_MUTED)
        self._c_border = QColor(Colors.BORDER_DEFAULT)

    def set_data(self, data: List[Tuple[str, float, int]], mode: str = "runtime"):
        self._data = list(data)
        self._mode = mode
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor(Colors.BG_SURFACE))
        painter.setPen(QPen(self._c_border, 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        if not self._data:
            painter.setPen(self._c_muted)
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "Run a benchmark to view comparison charts.")
            return

        pad_left = 60
        pad_bottom = 50
        pad_top = 30
        pad_right = 30

        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # Extract values
        if self._mode == "runtime":
            values = [d[1] for d in self._data]
            unit = "ms"
        else:
            values = [float(d[2]) for d in self._data]
            unit = "ops"

        max_val = max(values) if values else 1.0
        if max_val == 0:
            max_val = 1.0

        # Draw grid lines
        painter.setPen(QPen(self._c_border, 0.5, Qt.PenStyle.DashLine))
        for level in (0.25, 0.5, 0.75, 1.0):
            gy = pad_top + (1.0 - level) * chart_h
            painter.drawLine(pad_left, int(gy), w - pad_right, int(gy))
            painter.setPen(self._c_muted)
            painter.setFont(QFont("Segoe UI", 9))
            lbl_val = f"{max_val * level:.1f}" if self._mode == "runtime" else f"{int(max_val * level)}"
            painter.drawText(QRectF(pad_left - 55, gy - 8, 50, 16), Qt.AlignmentFlag.AlignRight, lbl_val)
            painter.setPen(QPen(self._c_border, 0.5, Qt.PenStyle.DashLine))

        # Draw baseline
        painter.setPen(QPen(QColor(Colors.BORDER_ACTIVE), 1))
        painter.drawLine(pad_left, pad_top + chart_h, w - pad_right, pad_top + chart_h)

        # Draw Bars
        num_bars = len(self._data)
        slot_w = chart_w / num_bars
        bar_w = min(50.0, slot_w * 0.6)

        font_label = QFont("Segoe UI", 9, QFont.Weight.Bold)
        font_name = QFont("Segoe UI", 9)

        for i, (name, runtime, ops) in enumerate(self._data):
            val = runtime if self._mode == "runtime" else ops
            bar_h = (val / max_val) * chart_h if max_val > 0 else 2
            bar_h = max(3.0, bar_h)

            bx = pad_left + i * slot_w + (slot_w - bar_w) / 2
            by = pad_top + chart_h - bar_h

            # Draw bar
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self._c_bar))
            painter.drawRoundedRect(QRectF(bx, by, bar_w, bar_h), 4, 4)

            # Draw value text above bar
            painter.setFont(font_label)
            painter.setPen(self._c_text)
            val_str = f"{val:.2f} {unit}" if self._mode == "runtime" else f"{val:,}"
            painter.drawText(QRectF(bx - 20, by - 18, bar_w + 40, 16), Qt.AlignmentFlag.AlignCenter, val_str)

            # Draw algorithm name below baseline
            painter.setFont(font_name)
            painter.setPen(self._c_muted)
            short_name = name.replace("Algorithm", "").replace("Sort", "").strip()
            painter.drawText(QRectF(bx - 15, pad_top + chart_h + 8, bar_w + 30, 36), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, short_name)


class ComplexityCurvesChartView(QWidget):
    """Line chart displaying mathematical asymptotic growth curves."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComplexityCurvesChartView")
        self.setMinimumHeight(320)

        self.current_n: int = 25
        self.max_n: int = 50
        self._points = ComplexityService.get_growth_points(max_n=50)

    def set_n(self, n: int):
        self.current_n = max(1, min(self.max_n, n))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor(Colors.BG_SURFACE))
        painter.setPen(QPen(QColor(Colors.BORDER_DEFAULT), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        pad_left = 65
        pad_bottom = 45
        pad_top = 25
        pad_right = 35

        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # Max Y value clamped for readability (e.g. at N=50, O(n^2) = 2500)
        y_max = 2600.0

        # Draw gridlines
        painter.setPen(QPen(QColor(Colors.BORDER_SUBTLE), 0.5, Qt.PenStyle.DashLine))
        painter.setFont(QFont("Segoe UI", 9))
        for level in (0.25, 0.5, 0.75, 1.0):
            gy = pad_top + (1.0 - level) * chart_h
            painter.drawLine(pad_left, int(gy), w - pad_right, int(gy))
            painter.setPen(QColor(Colors.TEXT_MUTED))
            painter.drawText(QRectF(pad_left - 60, gy - 8, 55, 16), Qt.AlignmentFlag.AlignRight, f"{int(y_max * level)}")
            painter.setPen(QPen(QColor(Colors.BORDER_SUBTLE), 0.5, Qt.PenStyle.DashLine))

        # Draw Axes
        painter.setPen(QPen(QColor(Colors.BORDER_ACTIVE), 1.5))
        painter.drawLine(pad_left, pad_top + chart_h, w - pad_right, pad_top + chart_h) # X axis
        painter.drawLine(pad_left, pad_top, pad_left, pad_top + chart_h)                 # Y axis

        # X-axis labels
        painter.setPen(QColor(Colors.TEXT_MUTED))
        for tick_n in (10, 20, 30, 40, 50):
            tx = pad_left + (tick_n / self.max_n) * chart_w
            painter.drawText(QRectF(tx - 15, pad_top + chart_h + 6, 30, 16), Qt.AlignmentFlag.AlignCenter, str(tick_n))

        # Draw Growth Curves
        for cls_info in COMPLEXITY_CLASSES:
            series = self._points.get(cls_info.notation, [])
            if not series:
                continue

            pen = QPen(QColor(cls_info.color_hex), 2.5)
            painter.setPen(pen)

            prev_pt = None
            for n_val, f_val in series:
                cx = pad_left + (n_val / self.max_n) * chart_w
                # Clamp Y to chart height
                clamped_val = min(y_max, f_val)
                cy = pad_top + chart_h - (clamped_val / y_max) * chart_h
                curr_pt = QPointF(cx, cy)

                if prev_pt is not None:
                    painter.drawLine(prev_pt, curr_pt)
                prev_pt = curr_pt

        # Vertical line for Current N
        cur_x = pad_left + (self.current_n / self.max_n) * chart_w
        n_pen = QPen(QColor("#fbbf24"), 1.5, Qt.PenStyle.DashLine)
        painter.setPen(n_pen)
        painter.drawLine(int(cur_x), pad_top, int(cur_x), pad_top + chart_h)

        # Label for Current N
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#fbbf24"))
        painter.drawText(QRectF(cur_x - 30, pad_top - 20, 60, 16), Qt.AlignmentFlag.AlignCenter, f"N = {self.current_n}")
