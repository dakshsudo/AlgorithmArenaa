"""Main window for Algorithm Arena with persistent sidebar and stacked views."""
from typing import Dict
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from app.settings import (
    APP_NAME, APP_VERSION, DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
)
from app.theme import Colors
from app.navigation import NAV_ITEMS, NavDestination
from ui.dashboard_page import DashboardPage
from ui.sorting_page import SortingPage
from ui.pathfinding_page import PathfindingPage
from ui.nqueens_page import NQueensPage
from ui.comparison_page import ComparisonPage
from ui.complexity_page import ComplexityPage
from ui.learning_page import LearningPage

class MainWindow(QMainWindow):
    """Main application window with persistent sidebar and stacked pages."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — DAA Interactive Laboratory")
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        self.page_map: Dict[str, QWidget] = {}
        self.nav_buttons: Dict[str, QPushButton] = {}
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self._init_ui()
        
    def _init_ui(self):
        # Central widget containing sidebar + stacked content
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # 1. Left Sidebar
        sidebar = self._create_sidebar()
        root_layout.addWidget(sidebar)
        
        # 2. Main Content Area (QStackedWidget)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {Colors.BG_BASE};")
        
        # Initialize and register all module pages
        self._register_pages()
        root_layout.addWidget(self.stack, 1)
        
        # Default to Dashboard
        self.navigate_to(NavDestination.DASHBOARD.value)
        
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("SidebarPanel")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame#SidebarPanel {{
                background-color: {Colors.BG_SIDEBAR};
                border-right: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(6)
        
        # Brand Logo / App Title
        brand_frame = QFrame()
        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setContentsMargins(6, 0, 6, 16)
        brand_layout.setSpacing(2)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        icon_label = QLabel("⚡")
        icon_label.setStyleSheet("font-size: 20px;")
        title_row.addWidget(icon_label)
        
        app_title = QLabel(APP_NAME)
        app_title.setObjectName("NavTitleLabel")
        title_row.addWidget(app_title)
        title_row.addStretch()
        
        brand_layout.addLayout(title_row)
        
        subtitle = QLabel("DAA LAB SUITE")
        subtitle.setObjectName("NavSubtitleLabel")
        brand_layout.addWidget(subtitle)
        
        layout.addWidget(brand_frame)
        
        # Section separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER_SUBTLE}; max-height: 1px; margin-bottom: 8px;")
        layout.addWidget(sep)
        
        # Navigation buttons
        for item in NAV_ITEMS:
            btn = QPushButton(f" {item.icon_char}   {item.title}")
            btn.setObjectName(f"nav_{item.id.value}")
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(item.description)
            
            dest_id = item.id.value
            btn.clicked.connect(lambda checked, d=dest_id: self.navigate_to(d))
            
            self.button_group.addButton(btn)
            self.nav_buttons[dest_id] = btn
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Footer in sidebar
        footer_frame = QFrame()
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(8, 8, 8, 0)
        footer_layout.setSpacing(4)
        
        status_lbl = QLabel("● Offline Mode Active")
        status_lbl.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 11px; font-weight: 600;")
        footer_layout.addWidget(status_lbl)
        
        ver_lbl = QLabel(f"Version {APP_VERSION}")
        ver_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        footer_layout.addWidget(ver_lbl)
        
        layout.addWidget(footer_frame)
        
        return sidebar
        
    def _register_pages(self):
        # 1. Dashboard
        dashboard = DashboardPage()
        dashboard.navigate_requested.connect(self.navigate_to)
        self._add_page(NavDestination.DASHBOARD.value, dashboard)
        
        # 2. Sorting
        sorting = SortingPage()
        self._add_page(NavDestination.SORTING.value, sorting)
        
        # 3. Pathfinding
        pathfinding = PathfindingPage()
        self._add_page(NavDestination.PATHFINDING.value, pathfinding)
        
        # 4. N-Queens
        nqueens = NQueensPage()
        self._add_page(NavDestination.NQUEENS.value, nqueens)
        
        # 5. Comparison
        comparison = ComparisonPage()
        self._add_page(NavDestination.COMPARISON.value, comparison)
        
        # 6. Complexity
        complexity = ComplexityPage()
        self._add_page(NavDestination.COMPLEXITY.value, complexity)
        
        # 7. Learning
        learning = LearningPage()
        self._add_page(NavDestination.LEARNING.value, learning)

    def _add_page(self, key: str, widget: QWidget):
        self.page_map[key] = widget
        self.stack.addWidget(widget)

    def navigate_to(self, key: str):
        """Navigate to the requested page key and update sidebar button state."""
        if key in self.page_map:
            widget = self.page_map[key]
            self.stack.setCurrentWidget(widget)
            
            # Update sidebar checked state
            if key in self.nav_buttons:
                self.nav_buttons[key].setChecked(True)
                
    def closeEvent(self, event):
        """Clean application shutdown."""
        event.accept()
