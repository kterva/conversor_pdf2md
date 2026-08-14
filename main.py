"""
Main Entrypoint for PDF to Markdown Converter Desktop Application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui import MainWindow, DARK_STYLE_SHEET


def main():
    """Configures environment and launches the PyQt6 Desktop GUI."""
    # Enable High DPI scaling for modern high-resolution displays
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("PDF to Markdown Converter")
    app.setOrganizationName("Antigravity")
    app.setStyleSheet(DARK_STYLE_SHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
