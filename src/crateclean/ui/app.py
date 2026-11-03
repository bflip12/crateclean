"""Starts the app and holds its main window.

The window is empty for now; it exists so the packaged build can be tried from the start.
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

APP_NAME = "CrateClean"


class MainWindow(QMainWindow):
    """The app's main window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(960, 600)
        self.setCentralWidget(QLabel("Add a music folder to get started."))


def main() -> int:
    """Start the app and return its exit code when the last window closes."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
