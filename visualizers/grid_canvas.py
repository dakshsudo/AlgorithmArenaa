"""Interactive QPainter grid canvas for maze editing and pathfinding visualization."""
from enum import Enum
from typing import Optional, Set, Tuple, List
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from app.theme import Colors
from algorithms.pathfinding.models import GridMap, PathEvent, PathEventType

class EditMode(str, Enum):
    WALL = "wall"
    WEIGHT = "weight"
    START = "start"
    TARGET = "target"
    ERASE = "erase"

class GridCanvas(QWidget):
    """Custom interactive paint canvas for grid maps and search animations."""

    grid_modified = Signal()

    def __init__(self, grid_map: GridMap, parent=None):
        super().__init__(parent)
        self.setObjectName("GridCanvas")
        self.setMinimumSize(280, 200)
        self.setMouseTracking(True)

        self.grid = grid_map
        self.edit_mode = EditMode.WALL

        # Visualization state
        self._current_node: Optional[Tuple[int, int]] = None
        self._frontier_nodes: Set[Tuple[int, int]] = set()
        self._visited_nodes: Set[Tuple[int, int]] = set()
        self._path_nodes: List[Tuple[int, int]] = []
        self._is_dragging = False
        self._drag_action: Optional[str] = None # "add_wall", "remove_wall", "move_start", "move_target", etc.

        # Palette
        self._c_bg = QColor(Colors.BG_SURFACE)
        self._c_grid_line = QColor(Colors.BORDER_DEFAULT)
        self._c_wall = QColor("#334155")
        self._c_start = QColor("#22c55e")
        self._c_target = QColor("#ef4444")
        self._c_weight = QColor("#854d0e")
        self._c_frontier = QColor(245, 158, 11, 180)
        self._c_visited = QColor(59, 130, 246, 170)
        self._c_current = QColor("#ec4899")
        self._c_path = QColor("#10b981")

    def set_grid(self, grid: GridMap):
        self.grid = grid
        self.reset_search_state()
        self.update()

    def set_edit_mode(self, mode: EditMode):
        self.edit_mode = mode

    def reset_search_state(self):
        self._current_node = None
        self._frontier_nodes.clear()
        self._visited_nodes.clear()
        self._path_nodes.clear()
        self.update()

    def set_event(self, event: Optional[PathEvent]):
        if event is None:
            self.reset_search_state()
            return

        self._current_node = event.current_node
        self._frontier_nodes = set(event.frontier_nodes)
        self._visited_nodes = set(event.visited_nodes)
        self._path_nodes = list(event.path)
        self.update()

    def _get_cell_at_pos(self, pos: QPointF) -> Optional[Tuple[int, int]]:
        w = self.width()
        h = self.height()
        cell_w = w / self.grid.cols
        cell_h = h / self.grid.rows

        c = int(pos.x() // cell_w)
        r = int(pos.y() // cell_h)

        if self.grid.is_in_bounds(r, c):
            return (r, c)
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cell = self._get_cell_at_pos(event.position())
            if not cell:
                return

            self._is_dragging = True
            r, c = cell

            if cell == self.grid.start:
                self._drag_action = "move_start"
            elif cell == self.grid.target:
                self._drag_action = "move_target"
            elif self.edit_mode == EditMode.START:
                if cell != self.grid.target and cell not in self.grid.walls:
                    self.grid.start = cell
                    self.grid_modified.emit()
            elif self.edit_mode == EditMode.TARGET:
                if cell != self.grid.start and cell not in self.grid.walls:
                    self.grid.target = cell
                    self.grid_modified.emit()
            elif self.edit_mode == EditMode.WEIGHT:
                if cell != self.grid.start and cell != self.grid.target:
                    if cell in self.grid.weights:
                        del self.grid.weights[cell]
                    else:
                        self.grid.weights[cell] = self.grid.weight_cost
                        self.grid.walls.discard(cell)
                    self.grid_modified.emit()
            elif self.edit_mode == EditMode.ERASE:
                self._drag_action = "erase"
                self.grid.walls.discard(cell)
                self.grid.weights.pop(cell, None)
                self.grid_modified.emit()
            else: # WALL
                if cell != self.grid.start and cell != self.grid.target:
                    if cell in self.grid.walls:
                        self._drag_action = "remove_wall"
                        self.grid.walls.remove(cell)
                    else:
                        self._drag_action = "add_wall"
                        self.grid.walls.add(cell)
                        self.grid.weights.pop(cell, None)
                    self.grid_modified.emit()

            self.update()

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            cell = self._get_cell_at_pos(event.position())
            if not cell:
                return

            if self._drag_action == "move_start":
                if cell != self.grid.target and cell not in self.grid.walls:
                    self.grid.start = cell
                    self.grid_modified.emit()
            elif self._drag_action == "move_target":
                if cell != self.grid.start and cell not in self.grid.walls:
                    self.grid.target = cell
                    self.grid_modified.emit()
            elif self._drag_action == "add_wall":
                if cell != self.grid.start and cell != self.grid.target:
                    self.grid.walls.add(cell)
                    self.grid.weights.pop(cell, None)
                    self.grid_modified.emit()
            elif self._drag_action == "remove_wall":
                if cell in self.grid.walls:
                    self.grid.walls.remove(cell)
                    self.grid_modified.emit()
            elif self._drag_action == "erase":
                self.grid.walls.discard(cell)
                self.grid.weights.pop(cell, None)
                self.grid_modified.emit()

            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._drag_action = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        rows = self.grid.rows
        cols = self.grid.cols

        if w <= 0 or h <= 0 or rows <= 0 or cols <= 0:
            return

        cell_w = w / cols
        cell_h = h / rows
        if cell_w <= 0 or cell_h <= 0:
            return

        # Background
        painter.fillRect(0, 0, w, h, self._c_bg)

        # Draw Cells
        path_set = set(self._path_nodes)
        badge_size = max(1, int(min(cell_w, cell_h) * 0.45))
        font_badge = QFont("Segoe UI", badge_size, QFont.Weight.Bold)

        for r in range(rows):
            for c in range(cols):
                node = (r, c)
                x = c * cell_w
                y = r * cell_h
                rect = QRectF(x, y, cell_w, cell_h)

                # Determine fill color
                if node == self.grid.start:
                    fill = self._c_start
                elif node == self.grid.target:
                    fill = self._c_target
                elif node in self.grid.walls:
                    fill = self._c_wall
                elif node in path_set:
                    fill = self._c_path
                elif node == self._current_node:
                    fill = self._c_current
                elif node in self._frontier_nodes:
                    fill = self._c_frontier
                elif node in self._visited_nodes:
                    fill = self._c_visited
                elif node in self.grid.weights:
                    fill = self._c_weight
                else:
                    fill = None

                if fill:
                    painter.fillRect(rect, fill)

                # Grid borders
                painter.setPen(QPen(self._c_grid_line, 0.5))
                painter.drawRect(rect)

                # Start / Target / Weight markers
                if node == self.grid.start:
                    painter.setFont(font_badge)
                    painter.setPen(Qt.GlobalColor.white)
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "S")
                elif node == self.grid.target:
                    painter.setFont(font_badge)
                    painter.setPen(Qt.GlobalColor.white)
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "T")
                elif node in self.grid.weights and node not in path_set and node != self._current_node:
                    painter.setFont(font_badge)
                    painter.setPen(QColor("#fbbf24"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "5x")
