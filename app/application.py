"""QApplication factory and initialization."""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.settings import APP_NAME, APP_ORGANIZATION, APP_VERSION
from app.theme import GLOBAL_STYLESHEET

def create_application() -> QApplication:
    """Create and configure the PySide6 QApplication instance."""
    # Ensure instance is unique
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setApplicationVersion(APP_VERSION)
    
    # Configure default modern clean font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Apply global modern dark theme
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    return app
