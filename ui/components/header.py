"""Page header component with title, subtitle, and action buttons."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from app.theme import Colors

class PageHeader(QFrame):
    """Standard header displayed at the top of each page."""
    
    def __init__(self, title: str, subtitle: str, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("PageHeader")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(4)
        
        # Title row
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("PageTitleLabel")
        self.title_label.setStyleSheet(f"""
            QLabel#PageTitleLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {Colors.TEXT_PRIMARY};
                letter-spacing: -0.3px;
            }}
        """)
        title_row.addWidget(self.title_label)
        title_row.addStretch()
        
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)
        title_row.addLayout(self.actions_layout)
        
        layout.addLayout(title_row)
        
        # Subtitle / description
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 13px;
            line-height: 1.4;
        """)
        layout.addWidget(self.subtitle_label)

    def add_action_widget(self, widget: QWidget):
        """Add an action button or widget to the right side of the header."""
        self.actions_layout.addWidget(widget)
