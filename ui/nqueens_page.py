"""N-Queens Backtracking Lab page."""
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QSlider, QFrame, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt

from app.theme import Colors
from ui.components.header import PageHeader
from visualizers.chessboard_canvas import ChessboardCanvas
from algorithms.backtracking.nqueens import NQueensSolver, NQueensEvent, NQueensEventType
from engine.nqueens_controller import NQueensPlaybackController
from engine.run_state import RunState

class NQueensPage(QWidget):
    """Interactive N-Queens Backtracking Lab page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NQueensPage")

        self.solver = NQueensSolver()
        self.controller = NQueensPlaybackController(self)
        self.current_n: int = 8
        self.find_one_mode: bool = False
        self.discovered_solutions: List[List[int]] = []

        self._init_ui()
        self._connect_signals()
        self._reload_solver()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        header = PageHeader(
            title="N-Queens Backtracking Lab",
            subtitle="Explore state-space tree traversal, candidate placement, attack conflicts, and solution enumeration."
        )
        root_layout.addWidget(header)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        # Left Column: Controls + Canvas
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 12, 0)
        left_layout.setSpacing(12)

        # Toolbar Card 1: Board Configuration & Mode
        config_card = self._create_config_card()
        left_layout.addWidget(config_card)

        # Toolbar Card 2: Playback Controls
        playback_card = self._create_playback_card()
        left_layout.addWidget(playback_card)

        # Canvas Card
        canvas_card = self._create_canvas_card()
        left_layout.addWidget(canvas_card, 1)

        main_splitter.addWidget(left_container)

        # Right Column: Stats, Complexity & Pseudocode
        right_container = self._create_sidebar_info()
        main_splitter.addWidget(right_container)

        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setSizes([680, 340])
        root_layout.addWidget(main_splitter, 1)

    def _create_config_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("NQueensConfigCard")
        card.setStyleSheet(f"""
            QFrame#NQueensConfigCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Row 1: Board Size + Mode
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        size_lbl = QLabel("Board Size (N):")
        size_lbl.setStyleSheet(f"font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        row1.addWidget(size_lbl)

        self.size_combo = QComboBox()
        self.size_combo.setFixedWidth(90)
        for n in range(4, 11):
            self.size_combo.addItem(f"{n} × {n}", n)
        self.size_combo.setCurrentIndex(4) # default 8x8 (index 4 is 8)
        self.size_combo.currentIndexChanged.connect(self._on_board_size_changed)
        row1.addWidget(self.size_combo)

        row1.addSpacing(16)

        mode_lbl = QLabel("Mode:")
        mode_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        row1.addWidget(mode_lbl)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Find One Solution", True)
        self.mode_combo.addItem("Enumerate All Solutions", False)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        row1.addWidget(self.mode_combo)

        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Replay Solution
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        sol_lbl = QLabel("Replay Solution:")
        sol_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        row2.addWidget(sol_lbl)

        self.sol_combo = QComboBox()
        self.sol_combo.setMinimumWidth(180)
        self.sol_combo.addItem("None yet", None)
        self.sol_combo.currentIndexChanged.connect(self._on_replay_solution_selected)
        row2.addWidget(self.sol_combo)

        row2.addStretch()
        layout.addLayout(row2)

        return card

    def _create_playback_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("NQueensPlaybackCard")
        card.setStyleSheet(f"""
            QFrame#NQueensPlaybackCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Row 1: Playback Controls
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.play_btn = QPushButton("▶ Start Search")
        self.play_btn.setProperty("class", "primary-btn")
        self.play_btn.setMinimumWidth(110)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self._on_play_pause_clicked)
        row1.addWidget(self.play_btn)

        self.step_back_btn = QPushButton("⏮ Step Back")
        self.step_back_btn.setProperty("class", "secondary-btn")
        self.step_back_btn.clicked.connect(self.controller.step_backward)
        row1.addWidget(self.step_back_btn)

        self.step_fwd_btn = QPushButton("⏭ Step Forward")
        self.step_fwd_btn.setProperty("class", "secondary-btn")
        self.step_fwd_btn.clicked.connect(self.controller.step_forward)
        row1.addWidget(self.step_fwd_btn)

        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.setProperty("class", "secondary-btn")
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        row1.addWidget(self.reset_btn)

        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Speed adjustment
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        speed_lbl = QLabel("Speed:")
        speed_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        row2.addWidget(speed_lbl)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 300)
        self.speed_slider.setValue(50)
        self.speed_slider.setFixedWidth(130)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        row2.addWidget(self.speed_slider)

        self.speed_label = QLabel("50 ms")
        self.speed_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; min-width: 50px; background: transparent; border: none;")
        row2.addWidget(self.speed_label)

        row2.addStretch()
        layout.addLayout(row2)

        return card

    def _create_canvas_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("NQueensCanvasCard")
        card.setStyleSheet(f"""
            QFrame#NQueensCanvasCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(10)

        self.canvas = ChessboardCanvas()
        layout.addWidget(self.canvas, 1)

        # Legend
        legend = QHBoxLayout()
        legend.setSpacing(10)
        legend.setContentsMargins(4, 2, 4, 2)
        legend_items = [
            ("#fbbf24", "Queen (♛)"),
            ("#f59e0b", "Candidate"),
            ("#ef4444", "Conflict"),
            ("#334155", "Square"),
        ]

        for color_hex, text in legend_items:
            box = QHBoxLayout()
            box.setSpacing(6)
            box.setContentsMargins(0, 0, 0, 0)
            badge = QWidget()
            badge.setFixedSize(10, 10)
            badge.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent; border: none; padding: 0px;")
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
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setMinimumWidth(300)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        # 1. Backtracking Counters
        stats_frame = QFrame()
        stats_frame.setObjectName("NQueensStatsCard")
        stats_frame.setStyleSheet(f"""
            QFrame#NQueensStatsCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        s_layout = QVBoxLayout(stats_frame)
        s_layout.setContentsMargins(14, 14, 14, 14)
        s_layout.setSpacing(10)

        s_header = QLabel("Search & Backtracking Metrics")
        s_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        s_layout.addWidget(s_header)

        grid = QGridLayout()
        grid.setSpacing(8)
        self.stat_solutions = self._add_stat_box(grid, 0, 0, "Solutions Found", "0")
        self.stat_depth = self._add_stat_box(grid, 0, 1, "Current Depth", "0")
        self.stat_attempts = self._add_stat_box(grid, 1, 0, "Placements Tested", "0")
        self.stat_conflicts = self._add_stat_box(grid, 1, 1, "Conflicts Pruned", "0")
        self.stat_step = self._add_stat_box(grid, 2, 0, "Step Index", "0 / 0")
        self.stat_time = self._add_stat_box(grid, 2, 1, "Elapsed Time", "0.0 s")
        s_layout.addLayout(grid)

        self.status_badge = QLabel("Status: Ready to Search")
        self.status_badge.setWordWrap(True)
        self.status_badge.setStyleSheet(f"""
            background-color: {Colors.BG_BASE};
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 12px;
            font-weight: 600;
        """)
        s_layout.addWidget(self.status_badge)
        layout.addWidget(stats_frame)

        # 2. Complexity Card
        complexity_frame = QFrame()
        complexity_frame.setObjectName("NQueensComplexityCard")
        complexity_frame.setStyleSheet(f"""
            QFrame#NQueensComplexityCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        c_layout = QVBoxLayout(complexity_frame)
        c_layout.setContentsMargins(14, 14, 14, 14)
        c_layout.setSpacing(8)

        c_header = QLabel("Theoretical Properties")
        c_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        c_layout.addWidget(c_header)

        self.lbl_time = QLabel("Worst-Case Time: O(N!)")
        self.lbl_space = QLabel("Auxiliary Space: O(N) stack & tracking sets")
        self.lbl_strategy = QLabel("Strategy: Depth-First State Space Tree Search")
        self.lbl_known = QLabel("Known Solutions (N=8): 92 total, 12 fundamental")

        for lbl in (self.lbl_time, self.lbl_space, self.lbl_strategy, self.lbl_known):
            lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent; border: none; padding: 0px;")
            c_layout.addWidget(lbl)

        layout.addWidget(complexity_frame)

        # 3. Pseudocode & Explanation
        pseudo_frame = QFrame()
        pseudo_frame.setObjectName("NQueensPseudoCard")
        pseudo_frame.setStyleSheet(f"""
            QFrame#NQueensPseudoCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        p_layout = QVBoxLayout(pseudo_frame)
        p_layout.setContentsMargins(14, 14, 14, 14)
        p_layout.setSpacing(8)

        p_header = QLabel("Backtracking Logic & Pruning")
        p_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        p_layout.addWidget(p_header)

        desc = QLabel(
            "Backtracking places queens row by row. At each row, it tests columns 0 to N-1. "
            "If column, main diagonal (r - c), or anti-diagonal (r + c) collides with an existing queen, "
            "the subtree is pruned immediately without further exploration."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; line-height: 1.4; background: transparent; border: none; padding: 0px;")
        p_layout.addWidget(desc)

        pseudo = [
            "procedure solveNQueens(row, N):",
            "    if row = N then:",
            "        recordSolution()",
            "        return",
            "    for col := 0 to N - 1 do:",
            "        if isSafe(row, col) then:",
            "            placeQueen(row, col)",
            "            solveNQueens(row + 1, N)",
            "            removeQueen(row, col)  // Backtrack"
        ]
        pseudo_lbl = QLabel("\n".join(pseudo))
        pseudo_lbl.setTextFormat(Qt.TextFormat.PlainText)
        pseudo_lbl.setWordWrap(True)
        pseudo_lbl.setStyleSheet(f"""
            background-color: {Colors.BG_BASE};
            color: {Colors.PRIMARY_LIGHT};
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid {Colors.BORDER_DEFAULT};
        """)
        p_layout.addWidget(pseudo_lbl)

        layout.addWidget(pseudo_frame)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _add_stat_box(self, grid: QGridLayout, row: int, col: int, title: str, initial_val: str, colspan: int = 1) -> QLabel:
        frame = QFrame()
        frame_id = f"nqueensStatBox_{row}_{col}"
        frame.setObjectName(frame_id)
        frame.setStyleSheet(f"""
            QFrame#{frame_id} {{
                background-color: {Colors.BG_BASE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
            }}
        """)
        l = QVBoxLayout(frame)
        l.setContentsMargins(10, 8, 10, 8)
        l.setSpacing(2)

        t_lbl = QLabel(title)
        t_lbl.setWordWrap(True)
        t_lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {Colors.TEXT_MUTED}; text-transform: uppercase; background: transparent; border: none; padding: 0px;")
        l.addWidget(t_lbl)

        v_lbl = QLabel(initial_val)
        v_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none; padding: 0px;")
        l.addWidget(v_lbl)

        grid.addWidget(frame, row, col, 1, colspan)
        return v_lbl

    def _connect_signals(self):
        self.controller.step_changed.connect(self._on_step_changed)
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.stats_updated.connect(self._on_stats_updated)
        self.controller.solution_discovered.connect(self._on_solution_discovered)
        self.controller.finished.connect(self._on_finished)

    def _on_board_size_changed(self):
        self.current_n = self.size_combo.currentData()
        self.canvas.set_board_size(self.current_n)
        known = NQueensSolver.KNOWN_SOLUTION_COUNTS.get(self.current_n, "N/A")
        self.lbl_known.setText(f"Known Solutions (N={self.current_n}): <b>{known}</b>")
        self._reload_solver()

    def _on_mode_changed(self):
        self.find_one_mode = self.mode_combo.currentData()
        self._reload_solver()

    def _on_speed_changed(self, val: int):
        self.speed_label.setText(f"{val} ms")
        self.controller.set_speed(val)

    def _reload_solver(self):
        self.controller.reset()
        self.discovered_solutions.clear()
        self.sol_combo.blockSignals(True)
        self.sol_combo.clear()
        self.sol_combo.addItem("None yet", None)
        self.sol_combo.blockSignals(False)

        events, solutions = self.solver.solve(self.current_n, find_one=self.find_one_mode)
        self.controller.load_events(events)
        self.canvas.set_state([-1] * self.current_n)

        self.stat_solutions.setText("0")
        self.stat_attempts.setText("0")
        self.stat_conflicts.setText("0")
        self.stat_depth.setText("0")
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

    def _on_reset_clicked(self):
        self.controller.reset()
        self.canvas.set_state([-1] * self.current_n)

    def _on_step_changed(self, curr_step: int, total_steps: int, event: Optional[NQueensEvent]):
        self.stat_step.setText(f"{curr_step} / {total_steps}")
        if event is None:
            self.canvas.set_state([-1] * self.current_n)
            return

        is_conflict = (event.event_type == NQueensEventType.CONFLICT)
        candidate = (event.row, event.col) if event.event_type in (NQueensEventType.TRY_CANDIDATE, NQueensEventType.CONFLICT) else None
        self.canvas.set_state(
            queens=event.queens,
            candidate=candidate,
            conflict_queen=event.conflicting_queen,
            is_conflict=is_conflict
        )

    def _on_state_changed(self, state_str: str):
        if state_str == RunState.RUNNING.value:
            self.play_btn.setText("⏸ Pause")
            self.status_badge.setText("Status: Backtracking search in progress...")
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

    def _on_stats_updated(self, attempts: int, conflicts: int, solutions: int, depth: int, elapsed_ms: int):
        self.stat_attempts.setText(str(attempts))
        self.stat_conflicts.setText(str(conflicts))
        self.stat_solutions.setText(str(solutions))
        self.stat_depth.setText(f"{depth} / {self.current_n}")
        self.stat_time.setText(f"{elapsed_ms / 1000.0:.1f} s")

    def _on_solution_discovered(self, sol_index: int, queens: list):
        self.discovered_solutions.append(queens)
        self.sol_combo.blockSignals(True)
        if self.sol_combo.count() == 1 and self.sol_combo.itemData(0) is None:
            self.sol_combo.clear()
        self.sol_combo.addItem(f"Solution #{sol_index}", list(queens))
        self.sol_combo.blockSignals(False)

    def _on_replay_solution_selected(self):
        queens = self.sol_combo.currentData()
        if queens:
            self.controller.pause()
            self.canvas.set_state(queens=queens)
            self.status_badge.setText(f"Viewing Replay: {self.sol_combo.currentText()}")
            self.status_badge.setStyleSheet(f"background-color: rgba(16, 185, 129, 0.15); color: {Colors.SUCCESS}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.SUCCESS};")

    def _on_finished(self, total_sols: int, attempts: int, conflicts: int, message: str):
        self.status_badge.setText(f"✓ {message}")
        self.status_badge.setStyleSheet(f"background-color: rgba(16, 185, 129, 0.15); color: {Colors.SUCCESS}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.SUCCESS};")
        self.stat_solutions.setText(str(total_sols))
