"""Application settings, constants, and path configurations."""
from pathlib import Path

APP_NAME = "Algorithm Arena"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "AlgorithmArena"

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"
DATA_DIR = BASE_DIR / "data"

# Default window settings
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1100
MIN_WINDOW_HEIGHT = 650

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "arena_progress.db"
