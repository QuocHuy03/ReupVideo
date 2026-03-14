import sys
import os
import urllib.request

# Ensure working directory is the app's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from ui_main import MainWindow


FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
FONT_FILE = os.path.join(FONT_DIR, "OpenSans.ttf")
FONT_URL = (
    "https://github.com/google/fonts/raw/main/ofl/opensans/"
    "OpenSans%5Bwdth%2Cwght%5D.ttf"
)


def _ensure_font():
    """Download Open Sans neu chua co, tra ve True neu thanh cong."""
    if os.path.exists(FONT_FILE) and os.path.getsize(FONT_FILE) > 100_000:
        return True
    os.makedirs(FONT_DIR, exist_ok=True)
    try:
        print("Dang tai Open Sans font...")
        urllib.request.urlretrieve(FONT_URL, FONT_FILE)
        return os.path.getsize(FONT_FILE) > 100_000
    except Exception as e:
        print(f"Khong tai duoc font: {e}")
        return False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ReupVideo Pro")
    app.setOrganizationName("ReupTool")
    app.setApplicationVersion("2.0")

    # Load Open Sans
    font_loaded = False
    if _ensure_font():
        font_id = QFontDatabase.addApplicationFont(FONT_FILE)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                app_font = QFont(families[0], 10)
                app.setFont(app_font)
                font_loaded = True
                print(f"Font loaded: {families[0]}")

    if not font_loaded:
        # Fallback
        app.setFont(QFont("Segoe UI", 10))
        print("Dung font fallback: Segoe UI")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
