"""Algorithm Arena - Entry point application launcher."""
import sys
from app.application import create_application
from ui.main_window import MainWindow

def main():
    app = create_application()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
