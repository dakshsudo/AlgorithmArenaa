"""Module Card component for dashboard and action grids."""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from app.theme import Colors

class ActionCard(QFrame):
    """Interactive card with icon, title, description, and action button."""
    
    clicked = Signal()
    
    def __init__(
        self,
        title: str,
        description: str,
        icon_char: str = "⚡",
        badge_text: str = "",
        button_text: str = "Open Lab",
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("ActionCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setStyleSheet(f"""
            QFrame#ActionCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 12px;
                padding: 16px;
            }}
            QFrame#ActionCard:hover {{
                border-color: {Colors.PRIMARY_DARK};
                background-color: {Colors.BG_SURFACE_ELEVATED};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        # Header row: Icon + Badge
        header_row = QHBoxLayout()
        
        icon_label = QLabel(icon_char)
        icon_label.setStyleSheet(f"""
            font-size: 22px;
            background-color: {Colors.BG_SIDEBAR_ACTIVE};
            border-radius: 8px;
            padding: 4px 8px;
            color: {Colors.PRIMARY};
        """)
        header_row.addWidget(icon_label)
        header_row.addStretch()
        
        if badge_text:
            badge_label = QLabel(badge_text)
            badge_label.setStyleSheet(f"""
                background-color: #1e3a5f;
                color: {Colors.PRIMARY_LIGHT};
                font-size: 11px;
                font-weight: 600;
                padding: 3px 8px;
                border-radius: 10px;
                border: 1px solid {Colors.PRIMARY_DARK};
            """)
            header_row.addWidget(badge_label)
            
        layout.addLayout(header_row)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            font-size: 12px;
            color: {Colors.TEXT_SECONDARY};
            line-height: 1.4;
        """)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Action button
        btn = QPushButton(f"{button_text} →")
        btn.setProperty("class", "primary-btn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: {Colors.TEXT_INVERTED};
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        btn.clicked.connect(self.clicked.emit)
        layout.addWidget(btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
