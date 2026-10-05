"""Complexity lab page."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from app.theme import Colors
from ui.components.header import PageHeader

class ComplexityPage(QWidget):
    """Complexity & Big-O lab page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComplexityPage")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        
        header = PageHeader(
            title="Complexity & Big-O Lab",
            subtitle="Asymptotic growth classes, interactive curves, dominant operations, and space complexity."
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
        p_label = QLabel("Interactive complexity curves and worked Big-O examples will be wired in Phase 5.")
        p_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 14px;")
        p_layout.addWidget(p_label)
        
        layout.addWidget(placeholder_frame)
        layout.addStretch()
