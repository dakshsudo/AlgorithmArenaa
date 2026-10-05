"""Design tokens and stylesheet for Algorithm Arena."""

class Colors:
    # Canvas & Surface
    BG_BASE = "#0b0f19"
    BG_SURFACE = "#111827"
    BG_SURFACE_ELEVATED = "#1f2937"
    BG_SURFACE_HOVER = "#283548"
    BG_SIDEBAR = "#0c1322"
    BG_SIDEBAR_ACTIVE = "#1e293b"
    
    # Borders
    BORDER_DEFAULT = "#1f293d"
    BORDER_SUBTLE = "#1e293b"
    BORDER_ACTIVE = "#38bdf8"
    BORDER_FOCUS = "#60a5fa"
    
    # Typography
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    TEXT_INVERTED = "#090d16"
    
    # Accents & Semantics
    PRIMARY = "#38bdf8"         # Sky blue accent
    PRIMARY_DARK = "#0284c7"
    PRIMARY_LIGHT = "#7dd3fc"
    
    SECONDARY = "#818cf8"       # Indigo accent
    SUCCESS = "#10b981"         # Emerald green
    WARNING = "#f59e0b"         # Amber
    DANGER = "#f43f5e"          # Rose red
    INFO = "#0ea5e9"            # Cyan info
    
    # Visualization status colors
    VIS_COMPARING = "#f59e0b"   # Amber/yellow
    VIS_SWAPPING = "#f43f5e"    # Rose/crimson
    VIS_SORTED = "#10b981"      # Emerald
    VIS_PIVOT = "#c084fc"       # Purple
    VIS_MERGE = "#38bdf8"       # Sky
    VIS_PATH = "#10b981"        # Path line
    VIS_VISITED = "#3b82f6"     # Visited node
    VIS_FRONTIER = "#fbbf24"    # Frontier node
    VIS_WALL = "#334155"        # Obstacle
    VIS_START = "#22c55e"       # Start
    VIS_TARGET = "#ef4444"      # Target
    VIS_QUEEN = "#fbbf24"       # Queen gold
    VIS_CONFLICT = "#f43f5e"    # Attack conflict


GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {Colors.BG_BASE};
    color: {Colors.TEXT_PRIMARY};
}}

QWidget {{
    background-color: transparent;
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}}

/* Tooltips */
QToolTip {{
    background-color: {Colors.BG_SURFACE_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
}}

/* Sidebar */
#SidebarPanel {{
    background-color: {Colors.BG_SIDEBAR};
    border-right: 1px solid {Colors.BORDER_DEFAULT};
}}

#NavTitleLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

#NavSubtitleLabel {{
    color: {Colors.PRIMARY};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* Navigation item buttons */
QPushButton.nav-btn {{
    background-color: transparent;
    color: {Colors.TEXT_SECONDARY};
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton.nav-btn:hover {{
    background-color: {Colors.BG_SURFACE_HOVER};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton.nav-btn:checked, QPushButton.nav-btn.active {{
    background-color: {Colors.BG_SIDEBAR_ACTIVE};
    color: {Colors.PRIMARY};
    font-weight: 600;
    border-left: 3px solid {Colors.PRIMARY};
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
}}

/* Generic Cards & Panels */
QFrame.card {{
    background-color: {Colors.BG_SURFACE};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 16px;
}}

QFrame.card-elevated {{
    background-color: {Colors.BG_SURFACE_ELEVATED};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 16px;
}}

/* Header labels */
QLabel.page-title {{
    font-size: 22px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
}}

QLabel.page-desc {{
    font-size: 13px;
    color: {Colors.TEXT_SECONDARY};
    margin-bottom: 8px;
}}

QLabel.section-title {{
    font-size: 15px;
    font-weight: 600;
    color: {Colors.TEXT_PRIMARY};
}}

/* Buttons */
QPushButton.primary-btn {{
    background-color: {Colors.PRIMARY};
    color: {Colors.TEXT_INVERTED};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton.primary-btn:hover {{
    background-color: {Colors.PRIMARY_LIGHT};
}}

QPushButton.primary-btn:pressed {{
    background-color: {Colors.PRIMARY_DARK};
}}

QPushButton.primary-btn:disabled {{
    background-color: {Colors.BG_SURFACE_ELEVATED};
    color: {Colors.TEXT_MUTED};
}}

QPushButton.secondary-btn {{
    background-color: {Colors.BG_SURFACE_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
}}

QPushButton.secondary-btn:hover {{
    background-color: {Colors.BG_SURFACE_HOVER};
    border-color: {Colors.BORDER_FOCUS};
}}

QPushButton.secondary-btn:pressed {{
    background-color: {Colors.BG_SURFACE};
}}

QPushButton.secondary-btn:disabled {{
    color: {Colors.TEXT_MUTED};
    border-color: {Colors.BORDER_DEFAULT};
}}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {Colors.BG_BASE};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {Colors.PRIMARY};
    selection-color: {Colors.TEXT_INVERTED};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {Colors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left-width: 0px;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_SURFACE_ELEVATED};
    border: 1px solid {Colors.BORDER_DEFAULT};
    selection-background-color: {Colors.PRIMARY_DARK};
    selection-color: {Colors.TEXT_PRIMARY};
    color: {Colors.TEXT_PRIMARY};
    padding: 4px;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 6px;
    background: {Colors.BG_SURFACE_ELEVATED};
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: {Colors.PRIMARY};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {Colors.TEXT_PRIMARY};
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {Colors.PRIMARY_LIGHT};
}}

/* ScrollBars */
QScrollBar:vertical {{
    border: none;
    background: {Colors.BG_BASE};
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {Colors.BG_SURFACE_ELEVATED};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {Colors.TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {Colors.BG_BASE};
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: {Colors.BG_SURFACE_ELEVATED};
    min-width: 20px;
    border-radius: 4px;
}}

/* Table Views */
QTableWidget, QTableView {{
    background-color: {Colors.BG_SURFACE};
    border: 1px solid {Colors.BORDER_DEFAULT};
    gridline-color: {Colors.BORDER_SUBTLE};
    color: {Colors.TEXT_PRIMARY};
    border-radius: 8px;
}}

QHeaderView::section {{
    background-color: {Colors.BG_SURFACE_ELEVATED};
    color: {Colors.TEXT_SECONDARY};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {Colors.BORDER_DEFAULT};
    font-weight: 600;
}}

/* Badges / Stat boxes */
QFrame.stat-box {{
    background-color: {Colors.BG_BASE};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 8px;
    padding: 8px 12px;
}}

QLabel.stat-title {{
    color: {Colors.TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel.stat-value {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 18px;
    font-weight: 700;
}}
"""
