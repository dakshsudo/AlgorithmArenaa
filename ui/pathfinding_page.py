"""Pathfinding lab page."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from app.theme import Colors
from ui.components.header import PageHeader

class PathfindingPage(QWidget):
    """Pathfinding visualizer lab page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PathfindingPage")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        
        header = PageHeader(
            title="Pathfinding & Graph Lab",
            subtitle="Interactive grid navigation for BFS, DFS, Dijkstra, and A* with obstacle generation."
        )
        layout.addWidget(header)
        
        placeholder_frame = QFrame()
        placeholder_frame.setStyleSheet(f"""
            background-color: {Colors.BG_SURFACE};
            border: 1px dashed {Colors.BORDER_DEFAULT};
            border-radius: 12px;
            padding: 32px;
        """)
        p_layout = QVBoxLayout(placeholder_frame)
        p_label = QLabel("Interactive grid editor and pathfinding algorithms will be wired in Phase 3.")
        p_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 14px;")
        p_layout.addWidget(p_label)
        
        layout.addWidget(placeholder_frame)
        layout.addStretch()
