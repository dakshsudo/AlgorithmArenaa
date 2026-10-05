"""Custom QPainter canvas rendering an N x N chessboard, queens, attack lines, and candidates."""
from typing import List, Optional, Tuple
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

from app.theme import Colors

class ChessboardCanvas(QWidget):
    """Custom paint canvas displaying the N-Queens chessboard and backtracking events."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChessboardCanvas")
        self.setMinimumSize(360, 360)

        self.n: int = 8
        self.queens: List[int] = [-1] * 8
        self.candidate: Optional[Tuple[int, int]] = None
        self.conflict_queen: Optional[Tuple[int, int]] = None
        self.is_conflict: bool = False

        # Colors
        self._c_light_tile = QColor("#334155")
        self._c_dark_tile = QColor("#1e293b")
        self._c_queen = QColor("#fbbf24")
        self._c_candidate = QColor("#f59e0b")
        self._c_conflict = QColor("#ef4444")
        self._c_border = QColor(Colors.BORDER_DEFAULT)

    def set_board_size(self, n: int):
        self.n = max(4, min(12, n))
        self.queens = [-1] * self.n
        self.candidate = None
        self.conflict_queen = None
        self.is_conflict = False
        self.update()

    def set_state(
        self,
        queens: List[int],
        candidate: Optional[Tuple[int, int]] = None,
        conflict_queen: Optional[Tuple[int, int]] = None,
        is_conflict: bool = False
    ):
        self.queens = list(queens)
        self.candidate = candidate
        self.conflict_queen = conflict_queen
        self.is_conflict = is_conflict
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        n = self.n

        # Board square size
        margin = 28
        board_size = min(w, h) - 2 * margin
        if board_size <= 0:
            return

        tile_size = board_size / n
        start_x = (w - board_size) / 2
        start_y = (h - board_size) / 2

        # Background
        painter.fillRect(0, 0, w, h, QColor(Colors.BG_SURFACE))

        # Coordinate label font
        font_coords = QFont("Segoe UI", 9)
        painter.setFont(font_coords)
        painter.setPen(QColor(Colors.TEXT_MUTED))

        # Draw Column labels (top and bottom)
        for c in range(n):
            cx = start_x + c * tile_size + tile_size / 2
            painter.drawText(QRectF(cx - 15, start_y - 20, 30, 16), Qt.AlignmentFlag.AlignCenter, str(c))
            painter.drawText(QRectF(cx - 15, start_y + board_size + 4, 30, 16), Qt.AlignmentFlag.AlignCenter, str(c))

        # Draw Row labels (left and right)
        for r in range(n):
            ry = start_y + r * tile_size + tile_size / 2
            painter.drawText(QRectF(start_x - 24, ry - 8, 20, 16), Qt.AlignmentFlag.AlignRight, str(r))
            painter.drawText(QRectF(start_x + board_size + 4, ry - 8, 20, 16), Qt.AlignmentFlag.AlignLeft, str(r))

        # Draw Board Tiles
        for r in range(n):
            for c in range(n):
                rect = QRectF(start_x + c * tile_size, start_y + r * tile_size, tile_size, tile_size)
                is_dark = (r + c) % 2 == 1
                tile_color = self._c_dark_tile if is_dark else self._c_light_tile

                painter.fillRect(rect, tile_color)
                painter.setPen(QPen(self._c_border, 0.5))
                painter.drawRect(rect)

        # Highlight Candidate Square
        if self.candidate:
            cr, cc = self.candidate
            if 0 <= cr < n and 0 <= cc < n:
                rect = QRectF(start_x + cc * tile_size, start_y + cr * tile_size, tile_size, tile_size)
                highlight_c = self._c_conflict if self.is_conflict else self._c_candidate
                painter.fillRect(rect, QColor(highlight_c.red(), highlight_c.green(), highlight_c.blue(), 100))
                painter.setPen(QPen(highlight_c, 2.5))
                painter.drawRect(rect)

        # Draw Attack / Conflict Vector Line
        if self.is_conflict and self.candidate and self.conflict_queen:
            cr, cc = self.candidate
            qr, qc = self.conflict_queen
            p1 = QPointF(start_x + cc * tile_size + tile_size / 2, start_y + cr * tile_size + tile_size / 2)
            p2 = QPointF(start_x + qc * tile_size + tile_size / 2, start_y + qr * tile_size + tile_size / 2)

            pen = QPen(self._c_conflict, 2.0, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(p1, p2)

        # Draw Queens
        font_queen = QFont("Segoe UI Symbol", int(tile_size * 0.55), QFont.Weight.Bold)
        painter.setFont(font_queen)

        for r in range(min(n, len(self.queens))):
            c = self.queens[r]
            if 0 <= c < n:
                rect = QRectF(start_x + c * tile_size, start_y + r * tile_size, tile_size, tile_size)

                # Check if this queen is the one causing conflict
                if self.is_conflict and self.conflict_queen == (r, c):
                    painter.fillRect(rect, QColor(239, 68, 68, 120))
                    painter.setPen(QColor("#fca5a5"))
                else:
                    painter.setPen(self._c_queen)

                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "♛")
