"""Dashboard page: central hub for Algorithm Arena."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from app.theme import Colors
from app.navigation import NavDestination
from ui.components.header import PageHeader
from ui.components.card import ActionCard

class DashboardPage(QWidget):
    """Main dashboard displaying quick launch cards, project features, and stats."""
    
    navigate_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardPage")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for responsive content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(28, 28, 28, 28)
        container_layout.setSpacing(24)
        
        # Header
        header = PageHeader(
            title="Algorithm Arena",
            subtitle="Interactive Design and Analysis of Algorithms (DAA) Laboratory & Visualization Platform"
        )
        container_layout.addWidget(header)
        
        # Hero Banner
        hero_card = QFrame()
        hero_card.setObjectName("HeroCard")
        hero_card.setStyleSheet(f"""
            QFrame#HeroCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111e38, stop:0.5 #162444, stop:1 #0f172a);
                border: 1px solid #1e3a66;
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setSpacing(10)
        
        hero_title = QLabel("Master Computer Science Algorithms Step-by-Step")
        hero_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.PRIMARY_LIGHT};")
        hero_layout.addWidget(hero_title)
        
        hero_desc = QLabel(
            "Welcome to Algorithm Arena — an educational desktop suite built for computer science students. "
            "Explore sorting, graph traversals, backtracking, asymptotic growth, and viva questions with "
            "100% deterministic, step-by-step playback, real event counts, and verifiable correctness."
        )
        hero_desc.setWordWrap(True)
        hero_desc.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; line-height: 1.5;")
        hero_layout.addWidget(hero_desc)
        
        # Key Highlights Row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        
        highlights = [
            ("6 Core Modules", "Sorting, Graphs, N-Queens, Comparison, Big-O, Viva"),
            ("100% Offline", "No cloud or external APIs required"),
            ("Accurate Metrics", "Real operation counters, separate benchmark timing"),
            ("Viva Ready", "Pseudocode, analysis, and oral exam prep"),
        ]
        
        for title, subtitle in highlights:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                background-color: rgba(15, 23, 42, 0.6);
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 8px;
                padding: 10px 14px;
            """)
            s_layout = QVBoxLayout(stat_frame)
            s_layout.setContentsMargins(0, 0, 0, 0)
            s_layout.setSpacing(2)
            
            st_lbl = QLabel(title)
            st_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
            sb_lbl = QLabel(subtitle)
            sb_lbl.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED};")
            sb_lbl.setWordWrap(True)
            
            s_layout.addWidget(st_lbl)
            s_layout.addWidget(sb_lbl)
            stats_row.addWidget(stat_frame)
            
        hero_layout.addLayout(stats_row)
        container_layout.addWidget(hero_card)
        
        # Modules Section Title
        sec_title = QLabel("Explore Visualizer Modules")
        sec_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        container_layout.addWidget(sec_title)
        
        # Module Cards Grid (2 columns or 3 columns)
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)
        
        modules = [
            (
                "Sorting Algorithm Lab",
                "Visualize Bubble, Selection, Insertion, Merge, Quick, and Heap Sort with step-by-step bar animations and exact comparison counts.",
                "📶",
                "6 Algorithms",
                NavDestination.SORTING.value
            ),
            (
                "Pathfinding Lab",
                "Explore BFS, DFS, Dijkstra, and A* on an interactive grid with obstacle walls, heuristics, and frontier tracking.",
                "🗺",
                "4 Algorithms",
                NavDestination.PATHFINDING.value
            ),
            (
                "N-Queens Backtracking Lab",
                "Inspect recursive backtracking, candidate placements, attack collisions, and all-solution enumeration.",
                "♛",
                "Backtracking",
                NavDestination.NQUEENS.value
            ),
            (
                "Comparison Lab",
                "Run side-by-side benchmarks on identical inputs. Compare operations, correctness, and execution times without animation lag.",
                "⚖",
                "Multi-Run",
                NavDestination.COMPARISON.value
            ),
            (
                "Complexity & Big-O Lab",
                "Interactive growth curves (O(1) to O(2ⁿ)), input-size sliders, dominant operations, and space-complexity notes.",
                "📈",
                "Asymptotics",
                NavDestination.COMPLEXITY.value
            ),
            (
                "Learning & Viva Centre",
                "Curated revision notes, pseudocode, multiple-choice quizzes with explanations, and oral viva exam questions.",
                "🎓",
                "Study & Quiz",
                NavDestination.LEARNING.value
            ),
        ]
        
        for idx, (title, desc, icon, badge, dest_id) in enumerate(modules):
            row = idx // 3
            col = idx % 3
            card = ActionCard(
                title=title,
                description=desc,
                icon_char=icon,
                badge_text=badge,
                button_text="Launch Lab"
            )
            card.clicked.connect(lambda d=dest_id: self.navigate_requested.emit(d))
            cards_grid.addWidget(card, row, col)
            
        container_layout.addLayout(cards_grid)
        
        # Quick-Start Guidelines Card
        guide_card = QFrame()
        guide_card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 12px;
                padding: 18px;
            }}
        """)
        guide_layout = QVBoxLayout(guide_card)
        guide_layout.setSpacing(8)
        
        g_title = QLabel("💡 Quick-Start & DAA Viva Tips")
        g_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.WARNING};")
        guide_layout.addWidget(g_title)
        
        tips = (
            "• <b>Independent Benchmarks:</b> The Comparison Lab measures pure algorithmic execution time on cloned inputs — never animation render time.<br>"
            "• <b>Exact Event Generation:</b> Visualizers yield deterministic state events (compares, swaps, visits, backtracks) for reproducible steps.<br>"
            "• <b>Step Forward:</b> Use the step buttons to pause and step through tricky partition or recursive calls at your own pace."
        )
        g_desc = QLabel(tips)
        g_desc.setTextFormat(Qt.TextFormat.RichText)
        g_desc.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; line-height: 1.5;")
        guide_layout.addWidget(g_desc)
        
        container_layout.addWidget(guide_card)
        container_layout.addStretch()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
