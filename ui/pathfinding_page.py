"""Pathfinding Lab page: interactive grid editor, pathfinding algorithms, and visualization."""
from typing import Optional, Tuple, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QFrame, QScrollArea, QSplitter, QButtonGroup
)
from PySide6.QtCore import Qt

from app.theme import Colors
from ui.components.header import PageHeader
from visualizers.grid_canvas import GridCanvas, EditMode
from algorithms.pathfinding.models import GridMap, PathEvent
from algorithms.pathfinding.registry import PATHFINDING_ALGORITHMS, get_pathfinder
from algorithms.pathfinding.base import BasePathfinder
from algorithms.pathfinding.mazes import MazeGenerator
from engine.pathfinding_controller import PathfindingPlaybackController
from engine.run_state import RunState

class PathfindingPage(QWidget):
    """Interactive Pathfinding & Graph Lab page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PathfindingPage")

        self.grid = GridMap(rows=20, cols=30, start=(10, 4), target=(10, 25))
        self.current_pathfinder: BasePathfinder = get_pathfinder("bfs")
        self.controller = PathfindingPlaybackController(self)

        self._init_ui()
        self._connect_signals()
        self._reload_search()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        header = PageHeader(
            title="Pathfinding & Graph Lab",
            subtitle="Draw obstacles and weights, test BFS, DFS, Dijkstra, and A*, and inspect frontier explorations."
        )
        root_layout.addWidget(header)

        # Splitter between visualizer and properties
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        # --- Left Column: Controls + Grid Canvas ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 12, 0)
        left_layout.setSpacing(12)

        # Toolbar Card 1: Algorithm & Maze Tools
        tools_card = self._create_tools_card()
        left_layout.addWidget(tools_card)

        # Toolbar Card 2: Playback Controls
        playback_card = self._create_playback_card()
        left_layout.addWidget(playback_card)

        # Canvas Card
        canvas_card = self._create_canvas_card()
        left_layout.addWidget(canvas_card, 1)

        main_splitter.addWidget(left_container)

        # --- Right Column: Stats, Complexity & Pseudocode ---
        right_container = self._create_sidebar_info()
        main_splitter.addWidget(right_container)

        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 2)
        root_layout.addWidget(main_splitter, 1)

    def _create_tools_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 10px 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Row 1: Algorithm selector + Grid Dimensions + Maze Presets
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        row1.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.setFixedWidth(190)
        for slug, cls in PATHFINDING_ALGORITHMS.items():
            meta = cls().get_metadata()
            self.algo_combo.addItem(meta.name, slug)
        self.algo_combo.currentIndexChanged.connect(self._on_algo_changed)
        row1.addWidget(self.algo_combo)

        row1.addSpacing(10)
        row1.addWidget(QLabel("Mazes:"))

        btn_rnd = QPushButton("Random")
        btn_rnd.setProperty("class", "secondary-btn")
        btn_rnd.clicked.connect(lambda: self._apply_maze("random"))
        row1.addWidget(btn_rnd)

        btn_div = QPushButton("Recursive Division")
        btn_div.setProperty("class", "secondary-btn")
        btn_div.clicked.connect(lambda: self._apply_maze("division"))
        row1.addWidget(btn_div)

        btn_river = QPushButton("Weighted Terrain")
        btn_river.setProperty("class", "secondary-btn")
        btn_river.clicked.connect(lambda: self._apply_maze("river"))
        row1.addWidget(btn_river)

        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Drawing Tools & Clearing Options
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        row2.addWidget(QLabel("Drawing Tool:"))
        self.tool_group = QButtonGroup(self)

        tools = [
            ("Wall", EditMode.WALL),
            ("Weight (5x)", EditMode.WEIGHT),
            ("Erase", EditMode.ERASE),
            ("Move Start", EditMode.START),
            ("Move Target", EditMode.TARGET),
        ]

        for text, mode in tools:
            btn = QPushButton(text)
            btn.setProperty("class", "secondary-btn")
            btn.setCheckable(True)
            if mode == EditMode.WALL:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, m=mode: self.canvas.set_edit_mode(m))
            self.tool_group.addButton(btn)
            row2.addWidget(btn)

        row2.addSpacing(16)

        btn_clear_path = QPushButton("Clear Path")
        btn_clear_path.setProperty("class", "secondary-btn")
        btn_clear_path.setToolTip("Keep walls and reset search traversal")
        btn_clear_path.clicked.connect(self._on_clear_path)
        row2.addWidget(btn_clear_path)

        btn_clear_all = QPushButton("Clear All")
        btn_clear_all.setProperty("class", "secondary-btn")
        btn_clear_all.clicked.connect(self._on_clear_all)
        row2.addWidget(btn_clear_all)

        row2.addStretch()
        layout.addLayout(row2)

        return card

    def _create_playback_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 10px 14px;
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setSpacing(10)

        self.play_btn = QPushButton("▶ Start Search")
        self.play_btn.setProperty("class", "primary-btn")
        self.play_btn.setFixedWidth(130)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self._on_play_pause_clicked)
        layout.addWidget(self.play_btn)

        self.step_back_btn = QPushButton("⏮ Step Back")
        self.step_back_btn.setProperty("class", "secondary-btn")
        self.step_back_btn.clicked.connect(self.controller.step_backward)
        layout.addWidget(self.step_back_btn)

        self.step_fwd_btn = QPushButton("⏭ Step Forward")
        self.step_fwd_btn.setProperty("class", "secondary-btn")
        self.step_fwd_btn.clicked.connect(self.controller.step_forward)
        layout.addWidget(self.step_fwd_btn)

        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.setProperty("class", "secondary-btn")
        self.reset_btn.clicked.connect(self._on_clear_path)
        layout.addWidget(self.reset_btn)

        layout.addSpacing(16)
        layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 250)
        self.speed_slider.setValue(40)
        self.speed_slider.setFixedWidth(110)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("40 ms")
        self.speed_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; min-width: 50px;")
        layout.addWidget(self.speed_label)

        layout.addStretch()
        return card

    def _create_canvas_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.canvas = GridCanvas(self.grid)
        self.canvas.grid_modified.connect(self._on_grid_modified)
        layout.addWidget(self.canvas, 1)

        # Legend row
        legend = QHBoxLayout()
        legend.setSpacing(14)
        legend_items = [
            ("#22c55e", "Start (S)"),
            ("#ef4444", "Target (T)"),
            ("#334155", "Wall"),
            ("#854d0e", "5x Weight"),
            ("#f59e0b", "Frontier"),
            ("#3b82f6", "Visited"),
            ("#ec4899", "Current"),
            ("#10b981", "Final Path"),
        ]

        for color_hex, text in legend_items:
            box = QHBoxLayout()
            box.setSpacing(5)
            badge = QFrame()
            badge.setFixedSize(12, 12)
            badge.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED};")
            box.addWidget(badge)
            box.addWidget(lbl)
            legend.addLayout(box)

        legend.addStretch()
        layout.addLayout(legend)

        return card

    def _create_sidebar_info(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 1. Operation Counters Box
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        s_layout = QVBoxLayout(stats_frame)
        s_layout.setSpacing(10)

        s_header = QLabel("Search Metrics")
        s_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        s_layout.addWidget(s_header)

        grid1 = QHBoxLayout()
        self.stat_visited = self._add_stat_box(grid1, "Nodes Visited", "0")
        self.stat_frontier = self._add_stat_box(grid1, "Frontier Nodes", "0")
        s_layout.addLayout(grid1)

        grid2 = QHBoxLayout()
        self.stat_length = self._add_stat_box(grid2, "Path Length", "0")
        self.stat_cost = self._add_stat_box(grid2, "Total Cost", "0")
        s_layout.addLayout(grid2)

        grid3 = QHBoxLayout()
        self.stat_step = self._add_stat_box(grid3, "Step Index", "0 / 0")
        self.stat_time = self._add_stat_box(grid3, "Elapsed Time", "0.0 s")
        s_layout.addLayout(grid3)

        self.status_badge = QLabel("Status: Ready to Search")
        self.status_badge.setStyleSheet(f"""
            background-color: {Colors.BG_BASE};
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            font-weight: 600;
        """)
        s_layout.addWidget(self.status_badge)
        layout.addWidget(stats_frame)

        # 2. Complexity Card
        complexity_frame = QFrame()
        complexity_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        c_layout = QVBoxLayout(complexity_frame)
        c_layout.setSpacing(8)

        c_header = QLabel("Theoretical Properties")
        c_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        c_layout.addWidget(c_header)

        self.lbl_guarantee = QLabel("Guarantees Shortest Path: Yes")
        self.lbl_weights = QLabel("Supports Edge Weights: No")
        self.lbl_time = QLabel("Time Complexity: O(V + E)")
        self.lbl_space = QLabel("Space Complexity: O(V)")

        for lbl in (self.lbl_guarantee, self.lbl_weights, self.lbl_time, self.lbl_space):
            lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY};")
            c_layout.addWidget(lbl)

        layout.addWidget(complexity_frame)

        # 3. Pseudocode & Explanation
        pseudo_frame = QFrame()
        pseudo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        p_layout = QVBoxLayout(pseudo_frame)
        p_layout.setSpacing(8)

        p_header = QLabel("Algorithm Explanation & Logic")
        p_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        p_layout.addWidget(p_header)

        self.algo_desc = QLabel("")
        self.algo_desc.setWordWrap(True)
        self.algo_desc.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; line-height: 1.4;")
        p_layout.addWidget(self.algo_desc)

        self.pseudo_label = QLabel("")
        self.pseudo_label.setTextFormat(Qt.TextFormat.PlainText)
        self.pseudo_label.setStyleSheet(f"""
            background-color: {Colors.BG_BASE};
            color: {Colors.PRIMARY_LIGHT};
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid {Colors.BORDER_DEFAULT};
        """)
        p_layout.addWidget(self.pseudo_label)

        layout.addWidget(pseudo_frame)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _add_stat_box(self, parent_layout: QHBoxLayout, title: str, initial_val: str) -> QLabel:
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {Colors.BG_BASE};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 6px;
            padding: 6px 10px;
        """)
        l = QVBoxLayout(frame)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {Colors.TEXT_MUTED}; text-transform: uppercase;")
        l.addWidget(t_lbl)

        v_lbl = QLabel(initial_val)
        v_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        l.addWidget(v_lbl)

        parent_layout.addWidget(frame)
        return v_lbl

    def _connect_signals(self):
        self.controller.step_changed.connect(self._on_step_changed)
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.stats_updated.connect(self._on_stats_updated)
        self.controller.finished.connect(self._on_finished)

    def _update_metadata_ui(self):
        meta = self.current_pathfinder.metadata
        self.lbl_guarantee.setText(f"Guarantees Shortest Path: <b>{'Yes' if meta.guarantees_shortest_path else 'No'}</b>")
        self.lbl_weights.setText(f"Supports Weights: <b>{'Yes' if meta.supports_weights else 'No'}</b>")
        self.lbl_time.setText(f"Time Complexity: <b>{meta.time_complexity}</b>")
        self.lbl_space.setText(f"Space Complexity: <b>{meta.space_complexity}</b>")
        self.algo_desc.setText(meta.description)
        self.pseudo_label.setText("\n".join(meta.pseudocode))

    def _on_algo_changed(self):
        slug = self.algo_combo.currentData()
        self.current_pathfinder = get_pathfinder(slug)
        self._update_metadata_ui()
        self._reload_search()

    def _apply_maze(self, maze_type: str):
        if maze_type == "random":
            MazeGenerator.random_walls(self.grid)
        elif maze_type == "division":
            MazeGenerator.recursive_division(self.grid)
        elif maze_type == "river":
            MazeGenerator.weighted_river(self.grid)
        self.canvas.update()
        self._reload_search()

    def _on_clear_path(self):
        self.controller.reset()
        self.canvas.reset_search_state()
        self._reload_search()

    def _on_clear_all(self):
        self.grid.walls.clear()
        self.grid.weights.clear()
        self.canvas.update()
        self._on_clear_path()

    def _on_grid_modified(self):
        self._reload_search()

    def _on_speed_changed(self, val: int):
        self.speed_label.setText(f"{val} ms")
        self.controller.set_speed(val)

    def _reload_search(self):
        self.controller.reset()
        self._update_metadata_ui()

        # Run pathfinding search to obtain events and final path
        events, path, cost = self.current_pathfinder.search(self.grid)
        self.controller.load_events(events)

        self.stat_visited.setText("0")
        self.stat_frontier.setText("0")
        self.stat_length.setText(f"{len(path)} steps" if path else "0")
        self.stat_cost.setText(str(cost))
        self.stat_step.setText(f"0 / {len(events)}")
        self.stat_time.setText("0.0 s")
        self.status_badge.setText("Status: Ready to Search")
        self.status_badge.setStyleSheet(f"background-color: {Colors.BG_BASE}; color: {Colors.TEXT_SECONDARY}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.BORDER_DEFAULT};")

    def _on_play_pause_clicked(self):
        if self.controller.state == RunState.RUNNING:
            self.controller.pause()
        elif self.controller.state == RunState.PAUSED:
            self.controller.resume()
        else:
            self.controller.play()

    def _on_step_changed(self, curr_step: int, total_steps: int, event: Optional[PathEvent]):
        self.stat_step.setText(f"{curr_step} / {total_steps}")
        self.canvas.set_event(event)

    def _on_state_changed(self, state_str: str):
        if state_str == RunState.RUNNING.value:
            self.play_btn.setText("⏸ Pause")
            self.status_badge.setText("Status: Traversing grid...")
            self.status_badge.setStyleSheet(f"background-color: rgba(245, 158, 11, 0.15); color: {Colors.WARNING}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.WARNING};")
        elif state_str == RunState.PAUSED.value:
            self.play_btn.setText("▶ Resume")
            self.status_badge.setText("Status: Paused")
            self.status_badge.setStyleSheet(f"background-color: rgba(129, 140, 248, 0.15); color: {Colors.SECONDARY}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.SECONDARY};")
        elif state_str == RunState.FINISHED.value:
            self.play_btn.setText("↺ Restart")
        else:
            self.play_btn.setText("▶ Start Search")
            self.status_badge.setText("Status: Ready to Search")
            self.status_badge.setStyleSheet(f"background-color: {Colors.BG_BASE}; color: {Colors.TEXT_SECONDARY}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.BORDER_DEFAULT};")

    def _on_stats_updated(self, visited_count: int, frontier_count: int, current_cost: float, elapsed_ms: int):
        self.stat_visited.setText(str(visited_count))
        self.stat_frontier.setText(str(frontier_count))
        self.stat_time.setText(f"{elapsed_ms / 1000.0:.1f} s")

    def _on_finished(self, found: bool, path_len: int, path_cost: int, message: str):
        if found:
            self.status_badge.setText(f"✓ {message}")
            self.status_badge.setStyleSheet(f"background-color: rgba(16, 185, 129, 0.15); color: {Colors.SUCCESS}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.SUCCESS};")
            self.stat_length.setText(f"{path_len} steps")
            self.stat_cost.setText(str(path_cost))
        else:
            self.status_badge.setText(f"✗ {message}")
            self.status_badge.setStyleSheet(f"background-color: rgba(244, 63, 94, 0.15); color: {Colors.DANGER}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.DANGER};")
            self.stat_length.setText("0")
            self.stat_cost.setText("0")
