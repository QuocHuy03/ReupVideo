import sys
import os

# Ensure working directory is the app's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui_main import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ReupVideo Pro")
    app.setOrganizationName("ReupTool")
    app.setApplicationVersion("2.0")

    # Set app font
    from PyQt5.QtGui import QFont
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
