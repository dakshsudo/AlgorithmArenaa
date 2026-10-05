"""Sorting Lab page: interactive visualization, controls, statistics, and pseudocode."""
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QLineEdit, QFrame, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt

from app.theme import Colors
from ui.components.header import PageHeader
from visualizers.sorting_canvas import SortingCanvas
from engine.playback_controller import PlaybackController
from engine.run_state import RunState
from engine.events import SortEvent
from engine.benchmark_runner import BenchmarkRunner
from algorithms.sorting.registry import SORTING_ALGORITHMS, get_sorting_algorithm
from algorithms.sorting.base import BaseSortAlgorithm
from services.validation_service import ValidationService

class SortingPage(QWidget):
    """Interactive Sorting Lab page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SortingPage")

        self.current_algorithm: BaseSortAlgorithm = get_sorting_algorithm("bubble_sort")
        self.controller = PlaybackController(self)
        self.array_data: List[int] = []

        self._init_ui()
        self._connect_signals()

        # Initial array generation
        self._generate_preset("random")

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        # 1. Header
        header = PageHeader(
            title="Sorting Algorithm Lab",
            subtitle="Step-by-step bar visualization, exact operation counters, algorithm complexity, and pseudocode."
        )
        root_layout.addWidget(header)

        # 2. Main Scrollable Container or Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        # --- Left/Center Column (Controls + Canvas) ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 12, 0)
        left_layout.setSpacing(12)

        # Config Card (Algorithm select, presets, array size, manual input)
        config_card = self._create_config_card()
        left_layout.addWidget(config_card)

        # Playback Controls Card
        playback_card = self._create_playback_card()
        left_layout.addWidget(playback_card)

        # Sorting Canvas Card
        canvas_card = self._create_canvas_card()
        left_layout.addWidget(canvas_card, 1)

        main_splitter.addWidget(left_container)

        # --- Right Column (Stats, Complexity & Pseudocode) ---
        right_container = self._create_sidebar_info()
        main_splitter.addWidget(right_container)

        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setSizes([680, 340])
        root_layout.addWidget(main_splitter, 1)

    def _create_config_card(self) -> QFrame:
        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Row 1: Algorithm selector + Array presets
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        algo_lbl = QLabel("Algorithm:")
        algo_lbl.setStyleSheet(f"font-weight: 600; color: {Colors.TEXT_PRIMARY};")
        row1.addWidget(algo_lbl)

        self.algo_combo = QComboBox()
        self.algo_combo.setFixedWidth(170)
        for slug, cls in SORTING_ALGORITHMS.items():
            meta = cls().get_metadata()
            self.algo_combo.addItem(meta.name, slug)
        self.algo_combo.currentIndexChanged.connect(self._on_algorithm_changed)
        row1.addWidget(self.algo_combo)

        row1.addSpacing(12)

        # Preset generator buttons
        row1.addWidget(QLabel("Presets:"))
        
        presets = [
            ("Random", "random"),
            ("Nearly Sorted", "nearly_sorted"),
            ("Reverse", "reverse"),
            ("Duplicates", "duplicates")
        ]
        for name, key in presets:
            btn = QPushButton(name)
            btn.setProperty("class", "secondary-btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._generate_preset(k))
            row1.addWidget(btn)

        row1.addStretch()
        layout.addLayout(row1)

        # Row 2: Array Size slider + Manual Input Field
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        row2.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(5, 80)
        self.size_slider.setValue(20)
        self.size_slider.setFixedWidth(130)
        self.size_slider.valueChanged.connect(self._on_size_slider_changed)
        row2.addWidget(self.size_slider)

        self.size_label = QLabel("20 elements")
        self.size_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; min-width: 75px;")
        row2.addWidget(self.size_label)

        row2.addSpacing(16)

        # Manual entry
        row2.addWidget(QLabel("Custom:"))
        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("e.g. 42, 15, -7, 88, 3, 26")
        self.manual_input.returnPressed.connect(self._on_apply_manual_input)
        row2.addWidget(self.manual_input, 1)

        apply_btn = QPushButton("Apply")
        apply_btn.setProperty("class", "secondary-btn")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.clicked.connect(self._on_apply_manual_input)
        row2.addWidget(apply_btn)

        layout.addLayout(row2)

        # Inline validation error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {Colors.DANGER}; font-size: 11px;")
        self.error_label.hide()
        layout.addWidget(self.error_label)

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

        # Play / Pause button
        self.play_btn = QPushButton("▶ Start")
        self.play_btn.setProperty("class", "primary-btn")
        self.play_btn.setFixedWidth(110)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self._on_play_pause_clicked)
        layout.addWidget(self.play_btn)

        # Step Backward
        self.step_back_btn = QPushButton("⏮ Step Back")
        self.step_back_btn.setProperty("class", "secondary-btn")
        self.step_back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.step_back_btn.clicked.connect(self.controller.step_backward)
        layout.addWidget(self.step_back_btn)

        # Step Forward
        self.step_fwd_btn = QPushButton("⏭ Step Forward")
        self.step_fwd_btn.setProperty("class", "secondary-btn")
        self.step_fwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.step_fwd_btn.clicked.connect(self.controller.step_forward)
        layout.addWidget(self.step_fwd_btn)

        # Reset button
        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.setProperty("class", "secondary-btn")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(self.reset_btn)

        layout.addSpacing(16)

        # Speed adjustment slider
        layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 800)
        self.speed_slider.setValue(150)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("150 ms")
        self.speed_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; min-width: 55px;")
        layout.addWidget(self.speed_label)

        layout.addStretch()

        # Pure Benchmark button (measures algorithm execution without animation lag)
        self.bench_btn = QPushButton("⚡ Benchmark")
        self.bench_btn.setProperty("class", "secondary-btn")
        self.bench_btn.setToolTip("Run algorithm in isolation to measure pure execution runtime")
        self.bench_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bench_btn.clicked.connect(self._on_run_benchmark)
        layout.addWidget(self.bench_btn)

        return card

    def _create_canvas_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Canvas
        self.canvas = SortingCanvas()
        layout.addWidget(self.canvas, 1)

        # Legend row
        legend_row = QHBoxLayout()
        legend_row.setSpacing(14)
        legend_row.setContentsMargins(6, 4, 6, 0)

        items = [
            ("#38bdf8", "Default"),
            ("#f59e0b", "Comparing"),
            ("#f43f5e", "Swap / Write"),
            ("#c084fc", "Pivot"),
            ("#10b981", "Sorted"),
            ("#818cf8", "Merge Range"),
        ]

        for color_hex, text in items:
            box = QHBoxLayout()
            box.setSpacing(5)
            badge = QFrame()
            badge.setFixedSize(12, 12)
            badge.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED};")
            box.addWidget(badge)
            box.addWidget(lbl)
            legend_row.addLayout(box)

        legend_row.addStretch()
        layout.addLayout(legend_row)

        return card

    def _create_sidebar_info(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        scroll.setMinimumWidth(320)

        container = QWidget()
        container.setMinimumWidth(300)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        # 1. Real-time Operations Stats Box
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

        s_header = QLabel("Operation Counters")
        s_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        s_layout.addWidget(s_header)

        # Grid of stats
        grid = QHBoxLayout()
        self.stat_compares = self._add_stat_box(grid, "Comparisons", "0")
        self.stat_swaps = self._add_stat_box(grid, "Swaps", "0")
        self.stat_writes = self._add_stat_box(grid, "Writes", "0")
        s_layout.addLayout(grid)

        grid2 = QHBoxLayout()
        self.stat_steps = self._add_stat_box(grid2, "Progress Step", "0 / 0")
        self.stat_time = self._add_stat_box(grid2, "Elapsed Time", "0.0 s")
        s_layout.addLayout(grid2)

        # Verification badge
        self.status_badge = QLabel("Status: Ready")
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

        # Benchmark report row
        self.benchmark_lbl = QLabel("Pure Runtime Benchmark: Not run yet")
        self.benchmark_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        s_layout.addWidget(self.benchmark_lbl)

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

        c_header = QLabel("Theoretical Complexity")
        c_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        c_layout.addWidget(c_header)

        self.lbl_best = QLabel("Best: O(n)")
        self.lbl_avg = QLabel("Average: O(n²)")
        self.lbl_worst = QLabel("Worst: O(n²)")
        self.lbl_space = QLabel("Space: O(1)")
        self.lbl_stable = QLabel("Stable: Yes")

        for lbl in (self.lbl_best, self.lbl_avg, self.lbl_worst, self.lbl_space, self.lbl_stable):
            lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY};")
            c_layout.addWidget(lbl)

        layout.addWidget(complexity_frame)

        # 3. Pseudocode & Explanation Card
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

        p_header = QLabel("Pseudocode & Logic")
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
        t_lbl.setWordWrap(True)
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
        meta = self.current_algorithm.metadata
        self.lbl_best.setText(f"Best: <b>{meta.best_time}</b>")
        self.lbl_avg.setText(f"Average: <b>{meta.avg_time}</b>")
        self.lbl_worst.setText(f"Worst: <b>{meta.worst_time}</b>")
        self.lbl_space.setText(f"Space: <b>{meta.space_complexity}</b>")
        self.lbl_stable.setText(f"Stable: <b>{'Yes' if meta.is_stable else 'No'}</b>")
        self.algo_desc.setText(meta.description)
        self.pseudo_label.setText("\n".join(meta.pseudocode))

    def _on_algorithm_changed(self):
        slug = self.algo_combo.currentData()
        self.current_algorithm = get_sorting_algorithm(slug)
        self._update_metadata_ui()
        self._reload_algorithm_events()

    def _generate_preset(self, preset_type: str):
        self.error_label.hide()
        size = self.size_slider.value()

        if preset_type == "random":
            self.array_data = ValidationService.generate_random(size)
        elif preset_type == "nearly_sorted":
            self.array_data = ValidationService.generate_nearly_sorted(size)
        elif preset_type == "reverse":
            self.array_data = ValidationService.generate_reverse_sorted(size)
        elif preset_type == "duplicates":
            self.array_data = ValidationService.generate_duplicate_heavy(size)

        self._reload_algorithm_events()

    def _on_apply_manual_input(self):
        text = self.manual_input.text()
        is_valid, parsed, err = ValidationService.parse_manual_array(text)
        if not is_valid:
            self.error_label.setText(f"⚠️ {err}")
            self.error_label.show()
            return

        self.error_label.hide()
        self.array_data = parsed
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(len(parsed))
        self.size_label.setText(f"{len(parsed)} elements")
        self.size_slider.blockSignals(False)
        self._reload_algorithm_events()

    def _on_size_slider_changed(self, val: int):
        self.size_label.setText(f"{val} elements")
        self._generate_preset("random")

    def _on_speed_changed(self, val: int):
        self.speed_label.setText(f"{val} ms")
        self.controller.set_speed(val)

    def _reload_algorithm_events(self):
        self.controller.reset()
        self._update_metadata_ui()

        # Generate event trace from algorithm
        events = self.current_algorithm.generate_events(self.array_data)
        self.controller.load_events(self.array_data, events)
        self.canvas.set_array(self.array_data)

        self.stat_compares.setText("0")
        self.stat_swaps.setText("0")
        self.stat_writes.setText("0")
        self.stat_steps.setText(f"0 / {len(events)}")
        self.stat_time.setText("0.0 s")
        self.status_badge.setText("Status: Ready")
        self.status_badge.setStyleSheet(f"background-color: {Colors.BG_BASE}; color: {Colors.TEXT_SECONDARY}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.BORDER_DEFAULT};")
        self.benchmark_lbl.setText("Pure Runtime Benchmark: Ready")

    def _on_play_pause_clicked(self):
        if self.controller.state == RunState.RUNNING:
            self.controller.pause()
        elif self.controller.state == RunState.PAUSED:
            self.controller.resume()
        else:
            self.controller.play()

    def _on_reset_clicked(self):
        self.controller.reset()
        self.canvas.set_array(self.array_data)

    def _on_step_changed(self, curr_step: int, total_steps: int, event: Optional[SortEvent]):
        self.stat_steps.setText(f"{curr_step} / {total_steps}")
        if event is not None:
            self.canvas.set_event(event)
        else:
            self.canvas.set_array(self.array_data)

    def _on_state_changed(self, state_str: str):
        if state_str == RunState.RUNNING.value:
            self.play_btn.setText("⏸ Pause")
            self.status_badge.setText("Status: Sorting in progress...")
            self.status_badge.setStyleSheet(f"background-color: rgba(245, 158, 11, 0.15); color: {Colors.WARNING}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.WARNING};")
        elif state_str == RunState.PAUSED.value:
            self.play_btn.setText("▶ Resume")
            self.status_badge.setText("Status: Paused")
            self.status_badge.setStyleSheet(f"background-color: rgba(129, 140, 248, 0.15); color: {Colors.SECONDARY}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.SECONDARY};")
        elif state_str == RunState.FINISHED.value:
            self.play_btn.setText("↺ Restart")
        else:
            self.play_btn.setText("▶ Start")
            self.status_badge.setText("Status: Ready")
            self.status_badge.setStyleSheet(f"background-color: {Colors.BG_BASE}; color: {Colors.TEXT_SECONDARY}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.BORDER_DEFAULT};")

    def _on_stats_updated(self, comparisons: int, swaps: int, writes: int, elapsed_ms: int):
        self.stat_compares.setText(str(comparisons))
        self.stat_swaps.setText(str(swaps))
        self.stat_writes.setText(str(writes))
        self.stat_time.setText(f"{elapsed_ms / 1000.0:.1f} s")

    def _on_finished(self, is_correct: bool, message: str):
        if is_correct:
            self.status_badge.setText(f"✓ {message}")
            self.status_badge.setStyleSheet(f"background-color: rgba(16, 185, 129, 0.15); color: {Colors.SUCCESS}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.SUCCESS};")
        else:
            self.status_badge.setText(f"✗ Verification Failed: {message}")
            self.status_badge.setStyleSheet(f"background-color: rgba(244, 63, 94, 0.15); color: {Colors.DANGER}; border-radius: 6px; padding: 8px; border: 1px solid {Colors.DANGER};")

    def _on_run_benchmark(self):
        """Execute pure benchmark without UI delay."""
        result = BenchmarkRunner.benchmark_sorting(self.current_algorithm, self.array_data)
        self.benchmark_lbl.setText(
            f"⚡ Benchmark: {result.runtime_ms} ms | {result.comparisons} compares, "
            f"{result.swaps} swaps, {result.writes} writes ({'Verified ✓' if result.is_correct else 'Failed ✗'})"
        )
        self.benchmark_lbl.setStyleSheet(f"color: {Colors.PRIMARY_LIGHT}; font-size: 11px; font-weight: 600;")
