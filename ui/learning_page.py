"""Learning and viva centre page."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from app.theme import Colors
from ui.components.header import PageHeader

class LearningPage(QWidget):
    """Learning and viva examination prep centre."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LearningPage")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        
        header = PageHeader(
            title="Learning & Viva Centre",
            subtitle="Curated revision notes, pseudocode, multiple-choice quizzes, and viva voce practice."
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
        p_label = QLabel("Educational notes, viva questions, and interactive quizzes will be wired in Phase 6.")
        p_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 14px;")
        p_layout.addWidget(p_label)
        
        layout.addWidget(placeholder_frame)
        layout.addStretch()
