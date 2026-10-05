"""Complexity & Big-O Lab page: interactive asymptotic growth curves and education."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt

from app.theme import Colors
from ui.components.header import PageHeader
from visualizers.chart_view import ComplexityCurvesChartView
from services.complexity_service import COMPLEXITY_CLASSES, ComplexityService

class ComplexityPage(QWidget):
    """Interactive Complexity & Big-O Lab page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComplexityPage")

        self._init_ui()
        self._on_n_slider_changed(20)

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        header = PageHeader(
            title="Complexity & Big-O Lab",
            subtitle="Asymptotic growth classes, interactive growth curves, dominant operations, and space complexity."
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

        # 1. Interactive Slider Card
        slider_card = QFrame()
        slider_card.setObjectName("CompSliderCard")
        slider_card.setStyleSheet(f"""
            QFrame#CompSliderCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        s_layout = QHBoxLayout(slider_card)
        s_layout.setContentsMargins(14, 12, 14, 12)
        s_layout.setSpacing(14)

        slider_lbl = QLabel("Input Size (N):")
        slider_lbl.setStyleSheet(f"background: transparent; border: none; font-weight: 600;")
        s_layout.addWidget(slider_lbl)

        self.n_slider = QSlider(Qt.Orientation.Horizontal)
        self.n_slider.setRange(1, 50)
        self.n_slider.setValue(20)
        self.n_slider.setFixedWidth(240)
        self.n_slider.valueChanged.connect(self._on_n_slider_changed)
        s_layout.addWidget(self.n_slider)

        self.n_label = QLabel("N = 20")
        self.n_label.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.PRIMARY_LIGHT}; min-width: 60px; background: transparent; border: none;")
        s_layout.addWidget(self.n_label)

        s_layout.addStretch()

        help_lbl = QLabel("Drag slider to inspect asymptotic growth scaling across growth classes.")
        help_lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        s_layout.addWidget(help_lbl)

        layout.addWidget(slider_card)

        # 2. Main Curves & Real-time Values Splitter
        viz_splitter = QSplitter(Qt.Orientation.Horizontal)
        viz_splitter.setChildrenCollapsible(False)

        # Left: Curves Chart Card
        chart_card = QFrame()
        chart_card.setObjectName("CompCurvesCard")
        chart_card.setStyleSheet(f"""
            QFrame#CompCurvesCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        c_layout = QVBoxLayout(chart_card)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setSpacing(8)

        c_header = QLabel("Asymptotic Growth Trajectory (N = 1 to 50)")
        c_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        c_layout.addWidget(c_header)

        self.chart = ComplexityCurvesChartView()
        c_layout.addWidget(self.chart, 1)

        # Chart Legend
        leg_row = QHBoxLayout()
        leg_row.setSpacing(12)
        for cls_info in COMPLEXITY_CLASSES:
            box = QHBoxLayout()
            box.setSpacing(4)
            badge = QWidget()
            badge.setFixedSize(10, 10)
            badge.setStyleSheet(f"background-color: {cls_info.color_hex}; border-radius: 2px;")
            lbl = QLabel(cls_info.notation)
            lbl.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent; border: none; padding: 0px;")
            box.addWidget(badge)
            box.addWidget(lbl)
            leg_row.addLayout(box)
        leg_row.addStretch()
        c_layout.addLayout(leg_row)

        viz_splitter.addWidget(chart_card)

        # Right: Real-time Growth Values Table Card
        table_card = QFrame()
        table_card.setObjectName("CompValuesCard")
        table_card.setStyleSheet(f"""
            QFrame#CompValuesCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(12, 12, 12, 12)
        t_layout.setSpacing(8)

        t_header = QLabel("Operation Counts at Current N")
        t_header.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        t_layout.addWidget(t_header)

        self.values_table = QTableWidget()
        self.values_table.setColumnCount(3)
        self.values_table.setHorizontalHeaderLabels(["Class", "Name", "Theoretical Operations"])
        self.values_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.values_table.verticalHeader().setVisible(False)
        self.values_table.setRowCount(len(COMPLEXITY_CLASSES))
        t_layout.addWidget(self.values_table)

        viz_splitter.addWidget(table_card)
        viz_splitter.setStretchFactor(0, 3)
        viz_splitter.setStretchFactor(1, 2)
        viz_splitter.setSizes([650, 350])
        layout.addWidget(viz_splitter)

        # 3. Comprehensive Asymptotic Guide Cards
        guide_card = QFrame()
        guide_card.setObjectName("CompGuideCard")
        guide_card.setStyleSheet(f"""
            QFrame#CompGuideCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        g_layout = QVBoxLayout(guide_card)
        g_layout.setContentsMargins(16, 16, 16, 16)
        g_layout.setSpacing(12)

        g_title = QLabel("📚 Asymptotic Foundations for DAA Examinations & Viva")
        g_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.PRIMARY_LIGHT}; background: transparent; border: none;")
        g_layout.addWidget(g_title)

        content_html = """
        <div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
            <p><b>1. Formal Definition of Big-O:</b><br>
            A function <i>f(n) &isin; O(g(n))</i> if there exist positive constants <b>c &gt; 0</b> and <b>n₀ &gt; 0</b> 
            such that for all <i>n &ge; n₀</i>, <b>0 &le; f(n) &le; c &middot; g(n)</b>. 
            Big-O defines an asymptotic <i>upper bound</i> on growth rate — it does <b>not</b> measure exact wall-clock milliseconds on a single test run.</p>

            <p><b>2. The Principle of Dominant Operations:</b><br>
            When analyzing algorithms, lower-order terms and constant coefficients are dropped as <i>n &rarr; &infin;</i>. 
            For example, if an algorithm executes <i>3n² + 14n + 250</i> operations, the <b>n²</b> quadratic term dominates total execution time for large inputs.</p>

            <p><b>3. Auxiliary Space vs In-Place Sorting:</b><br>
            An algorithm is <b>in-place</b> if it requires only <b>O(1)</b> additional memory beyond the input array (e.g., Bubble, Selection, Insertion, and Heap Sort). 
            In contrast, Merge Sort requires <b>O(n)</b> auxiliary buffer space, and Quick Sort requires <b>O(log n)</b> recursion call-stack space.</p>
        </div>
        """
        guide_lbl = QLabel(content_html)
        guide_lbl.setTextFormat(Qt.TextFormat.RichText)
        guide_lbl.setWordWrap(True)
        g_layout.addWidget(guide_lbl)

        layout.addWidget(guide_card)

        scroll.setWidget(container)
        root_layout.addWidget(scroll, 1)

    def _on_n_slider_changed(self, n: int):
        self.n_label.setText(f"N = {n}")
        self.chart.set_n(n)

        # Update values table
        for row, cls_info in enumerate(COMPLEXITY_CLASSES):
            val = ComplexityService.compute_value(cls_info.notation, n)
            self.values_table.setItem(row, 0, QTableWidgetItem(cls_info.notation))
            self.values_table.setItem(row, 1, QTableWidgetItem(cls_info.name))

            if cls_info.notation == "O(2ⁿ)":
                val_str = f"{2**n:,}" if n <= 30 else f"> 10^{int(n*0.30103)}"
            elif cls_info.notation in ("O(log n)", "O(n log n)"):
                val_str = f"{val:.2f}"
            else:
                val_str = f"{int(val):,}"

            item = QTableWidgetItem(val_str)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.values_table.setItem(row, 2, item)
