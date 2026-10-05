"""Comparison Lab page: multi-algorithm side-by-side benchmarking and analysis."""
from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QFrame, QScrollArea, QTableWidget,
    QTableWidgetItem, QCheckBox, QHeaderView, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt

from app.theme import Colors
from ui.components.header import PageHeader
from visualizers.chart_view import ComparisonBarChartView
from services.comparison_service import ComparisonService
from services.validation_service import ValidationService
from algorithms.sorting.registry import SORTING_ALGORITHMS
from algorithms.pathfinding.registry import PATHFINDING_ALGORITHMS
from algorithms.pathfinding.models import GridMap
from algorithms.pathfinding.mazes import MazeGenerator

class ComparisonPage(QWidget):
    """Comparison Lab page comparing algorithms on identical inputs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComparisonPage")

        self.category: str = "sorting" # "sorting" or "pathfinding"
        self.sorting_checkboxes: Dict[str, QCheckBox] = {}
        self.pathfinding_checkboxes: Dict[str, QCheckBox] = {}

        self._init_ui()
        self._run_sorting_comparison()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        header = PageHeader(
            title="Algorithm Comparison Lab",
            subtitle="Multi-algorithm side-by-side benchmarking, operation counts, and performance metrics on identical inputs."
        )
        root_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # 1. Config Toolbar Card
        config_card = self._create_config_card()
        layout.addWidget(config_card)

        # 2. Results Table Card
        table_card = self._create_table_card()
        layout.addWidget(table_card)

        # 3. Chart Card
        chart_card = self._create_chart_card()
        layout.addWidget(chart_card)

        # 4. Methodology Note Card
        note_card = QFrame()
        note_card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        n_layout = QVBoxLayout(note_card)
        n_lbl = QLabel(
            "<b>🔬 Benchmarking Methodology:</b> Algorithms are executed in complete isolation on independent cloned "
            "copies of the exact same test input. Pure wall-clock execution time is recorded with sub-millisecond precision "
            "via <code>time.perf_counter_ns()</code>, completely separated from UI rendering and animation frames."
        )
        n_lbl.setWordWrap(True)
        n_lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; line-height: 1.4;")
        n_layout.addWidget(n_lbl)
        layout.addWidget(note_card)

        scroll.setWidget(container)
        root_layout.addWidget(scroll, 1)

    def _create_config_card(self) -> QFrame:
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
        layout.setSpacing(10)

        # Row 1: Category Selection
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Category:"))

        self.cat_combo = QComboBox()
        self.cat_combo.addItem("Sorting Algorithms", "sorting")
        self.cat_combo.addItem("Pathfinding & Graph Algorithms", "pathfinding")
        self.cat_combo.currentIndexChanged.connect(self._on_category_changed)
        row1.addWidget(self.cat_combo)

        row1.addSpacing(16)

        # Test Input Preset
        row1.addWidget(QLabel("Input Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Random Array", "random")
        self.preset_combo.addItem("Nearly Sorted", "nearly_sorted")
        self.preset_combo.addItem("Reverse Sorted", "reverse")
        self.preset_combo.addItem("Duplicate-Heavy", "duplicates")
        row1.addWidget(self.preset_combo)

        row1.addSpacing(16)

        # Size slider
        self.size_lbl = QLabel("Size: 100 elements")
        row1.addWidget(self.size_lbl)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(20, 500)
        self.size_slider.setValue(100)
        self.size_slider.setFixedWidth(130)
        self.size_slider.valueChanged.connect(lambda v: self.size_lbl.setText(f"Size: {v} elements"))
        row1.addWidget(self.size_slider)

        row1.addStretch()

        # Run Button
        self.run_btn = QPushButton("⚡ Run Benchmark")
        self.run_btn.setProperty("class", "primary-btn")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self._on_run_clicked)
        row1.addWidget(self.run_btn)

        layout.addLayout(row1)

        # Row 2: Algorithm Checkboxes Container
        self.chk_container = QWidget()
        self.chk_layout = QHBoxLayout(self.chk_container)
        self.chk_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_layout.setSpacing(14)

        # Create Sorting checkboxes
        self.chk_layout.addWidget(QLabel("Select Algorithms:"))
        for slug, cls in SORTING_ALGORITHMS.items():
            chk = QCheckBox(cls().get_metadata().name)
            chk.setChecked(True)
            self.sorting_checkboxes[slug] = chk
            self.chk_layout.addWidget(chk)

        # Create Pathfinding checkboxes (hidden initially)
        for slug, cls in PATHFINDING_ALGORITHMS.items():
            chk = QCheckBox(cls().get_metadata().name)
            chk.setChecked(True)
            chk.hide()
            self.pathfinding_checkboxes[slug] = chk
            self.chk_layout.addWidget(chk)

        self.chk_layout.addStretch()
        layout.addWidget(self.chk_container)

        return card

    def _create_table_card(self) -> QFrame:
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
        layout.setSpacing(8)

        t_lbl = QLabel("Benchmark Results Table")
        t_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(t_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Algorithm", "Time (ms)", "Comparisons", "Swaps / Writes", "Space Complexity", "Correctness", "Asymptotics"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(210)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        return card

    def _create_chart_card(self) -> QFrame:
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
        layout.setSpacing(8)

        header_row = QHBoxLayout()
        c_lbl = QLabel("Comparative Performance Visualization")
        c_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        header_row.addWidget(c_lbl)
        header_row.addStretch()

        # Switch between runtime vs operations
        header_row.addWidget(QLabel("Metric:"))
        self.radio_time = QRadioButton("Execution Time (ms)")
        self.radio_time.setChecked(True)
        self.radio_time.toggled.connect(self._on_metric_toggled)
        header_row.addWidget(self.radio_time)

        self.radio_ops = QRadioButton("Total Operations")
        self.radio_ops.toggled.connect(self._on_metric_toggled)
        header_row.addWidget(self.radio_ops)

        layout.addLayout(header_row)

        self.chart = ComparisonBarChartView()
        layout.addWidget(self.chart)

        return card

    def _on_category_changed(self):
        self.category = self.cat_combo.currentData()
        is_sorting = (self.category == "sorting")

        # Toggle preset dropdown options
        self.preset_combo.clear()
        if is_sorting:
            self.preset_combo.addItem("Random Array", "random")
            self.preset_combo.addItem("Nearly Sorted", "nearly_sorted")
            self.preset_combo.addItem("Reverse Sorted", "reverse")
            self.preset_combo.addItem("Duplicate-Heavy", "duplicates")
            self.size_lbl.show()
            self.size_slider.show()
            for chk in self.sorting_checkboxes.values():
                chk.show()
            for chk in self.pathfinding_checkboxes.values():
                chk.hide()
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "Algorithm", "Time (ms)", "Comparisons", "Swaps / Writes", "Space Complexity", "Correctness", "Asymptotics"
            ])
        else:
            self.preset_combo.addItem("Random Obstacles", "random")
            self.preset_combo.addItem("Recursive Division Maze", "division")
            self.preset_combo.addItem("Weighted River Terrain", "river")
            self.size_lbl.hide()
            self.size_slider.hide()
            for chk in self.sorting_checkboxes.values():
                chk.hide()
            for chk in self.pathfinding_checkboxes.values():
                chk.show()
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "Algorithm", "Time (ms)", "Visited Nodes", "Path Length", "Total Cost", "Optimal?", "Weights?"
            ])

        self._on_run_clicked()

    def _on_metric_toggled(self):
        mode = "runtime" if self.radio_time.isChecked() else "operations"
        self.chart._mode = mode
        self.chart.update()

    def _on_run_clicked(self):
        if self.category == "sorting":
            self._run_sorting_comparison()
        else:
            self._run_pathfinding_comparison()

    def _run_sorting_comparison(self):
        selected_slugs = [slug for slug, chk in self.sorting_checkboxes.items() if chk.isChecked()]
        if not selected_slugs:
            return

        size = self.size_slider.value()
        preset = self.preset_combo.currentData() or "random"

        if preset == "random":
            arr = ValidationService.generate_random(size)
        elif preset == "nearly_sorted":
            arr = ValidationService.generate_nearly_sorted(size)
        elif preset == "reverse":
            arr = ValidationService.generate_reverse_sorted(size)
        else:
            arr = ValidationService.generate_duplicate_heavy(size)

        results = ComparisonService.compare_sorting(selected_slugs, arr)

        # Update table
        self.table.setRowCount(len(results))
        chart_data = []

        for row, res in enumerate(results):
            meta = SORTING_ALGORITHMS[selected_slugs[row]]().get_metadata()
            self.table.setItem(row, 0, QTableWidgetItem(res.algorithm_name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{res.runtime_ms:.3f} ms"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{res.comparisons:,}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{res.swaps + res.writes:,}"))
            self.table.setItem(row, 4, QTableWidgetItem(meta.space_complexity))
            self.table.setItem(row, 5, QTableWidgetItem("✓ Verified" if res.is_correct else "✗ Failed"))
            self.table.setItem(row, 6, QTableWidgetItem(f"Avg: {meta.avg_time}"))

            chart_data.append((res.algorithm_name, res.runtime_ms, res.comparisons + res.swaps + res.writes))

        self.chart.set_data(chart_data, mode="runtime" if self.radio_time.isChecked() else "operations")

    def _run_pathfinding_comparison(self):
        selected_slugs = [slug for slug, chk in self.pathfinding_checkboxes.items() if chk.isChecked()]
        if not selected_slugs:
            return

        grid = GridMap(rows=20, cols=30, start=(10, 4), target=(10, 25))
        preset = self.preset_combo.currentData() or "random"

        if preset == "random":
            MazeGenerator.random_walls(grid)
        elif preset == "division":
            MazeGenerator.recursive_division(grid)
        elif preset == "river":
            MazeGenerator.weighted_river(grid)

        results = ComparisonService.compare_pathfinding(selected_slugs, grid)

        self.table.setRowCount(len(results))
        chart_data = []

        for row, res in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(res.algorithm_name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{res.runtime_ms:.3f} ms"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{res.visited_nodes}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{res.path_length} steps" if res.path_found else "No Path"))
            self.table.setItem(row, 4, QTableWidgetItem(str(res.path_cost)))
            self.table.setItem(row, 5, QTableWidgetItem("Yes (Guaranteed)" if res.guarantees_shortest else "No"))
            self.table.setItem(row, 6, QTableWidgetItem("Yes" if res.supports_weights else "No"))

            chart_data.append((res.algorithm_name, res.runtime_ms, res.visited_nodes))

        self.chart.set_data(chart_data, mode="runtime" if self.radio_time.isChecked() else "operations")
