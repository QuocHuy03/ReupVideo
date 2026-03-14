import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from style import DARK_THEME
from tab_dashboard import DashboardTab
from tab_downloader import DownloaderTab
from tab_processor import ProcessorTab
from tab_scheduler import SchedulerTab
from tab_script_manager import ScriptManagerTab
from tab_settings import SettingsTab


NAV_ITEMS = [
    ("Dashboard",      "Tong quan hoat dong va thong ke he thong",                DashboardTab),
    ("Tai Video",      "Tai video tu TikTok, YouTube, Instagram, Facebook...",     DownloaderTab),
    ("Xu Ly Video",    "Ap dung FFmpeg scripts de reup video hang loat",           ProcessorTab),
    ("Lich Trinh",     "Dat lich tu dong tai va xu ly video theo gio",             SchedulerTab),
    ("Script Manager", "Quan ly, tao va chinh sua cac script FFmpeg",              ScriptManagerTab),
    ("Cai Dat",        "Cau hinh duong dan cong cu va tuy chon mac dinh",          SettingsTab),
]


class SidebarButton(QPushButton):
    def __init__(self, label: str):
        super().__init__(f"  {label}")
        self.setObjectName("sidebar_btn")
        self.setCheckable(False)
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class ContentHeader(QWidget):
    """Header bar hien thi tren content area moi tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content_header")
        self.setFixedHeight(68)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(0)

        # Left: title + subtitle stack
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)

        self.title_lbl = QLabel("Dashboard")
        self.title_lbl.setObjectName("header_title")

        self.sub_lbl = QLabel("")
        self.sub_lbl.setObjectName("header_sub")

        text_col.addStretch()
        text_col.addWidget(self.title_lbl)
        text_col.addWidget(self.sub_lbl)
        text_col.addStretch()

        layout.addLayout(text_col, stretch=1)

        # Right: version badge
        badge = QLabel("ReupPro v2.0")
        badge.setObjectName("header_badge")
        layout.addWidget(badge)

    def set_page(self, title: str, subtitle: str):
        self.title_lbl.setText(title)
        self.sub_lbl.setText(subtitle)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReupVideo Pro - Full Auto Tool")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(DARK_THEME)

        self._nav_buttons = []
        self._build_ui()
        self._navigate(0)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_h = QHBoxLayout(central)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)

        # ===== SIDEBAR =====
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 0, 8, 12)
        sidebar_layout.setSpacing(4)

        logo = QLabel("ReupPro")
        logo.setObjectName("logo_label")
        version = QLabel("v2.0 | FFmpeg + yt-dlp")
        version.setObjectName("version_label")
        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(version)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #21262d;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(8)

        self.stack = QStackedWidget()
        for idx, (label, subtitle, TabClass) in enumerate(NAV_ITEMS):
            btn = SidebarButton(label)
            btn.clicked.connect(lambda checked, i=idx: self._navigate(i))
            self._nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

            tab = TabClass()
            self.stack.addWidget(tab)

        sidebar_layout.addStretch()

        bottom_lbl = QLabel("FFmpeg + yt-dlp")
        bottom_lbl.setStyleSheet("color: #30363d; font-size: 10px; padding: 4px 8px; background: transparent;")
        bottom_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(bottom_lbl)

        main_h.addWidget(sidebar)

        # ===== CONTENT AREA =====
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header bar
        self.header = ContentHeader()
        content_layout.addWidget(self.header)

        # Thin accent separator line
        accent_line = QFrame()
        accent_line.setFixedHeight(2)
        accent_line.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #0ea5e9, stop:0.5 #00d4ff, stop:1 #0d1117);"
            "border: none;"
        )
        content_layout.addWidget(accent_line)

        # Tab content
        content_layout.addWidget(self.stack)
        main_h.addWidget(content_wrapper, stretch=1)

        statusbar = QStatusBar()
        statusbar.showMessage("ReupVideo Pro khoi dong thanh cong")
        self.setStatusBar(statusbar)

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.set_active(i == index)
        label, subtitle, _ = NAV_ITEMS[index]
        self.header.set_page(label, subtitle)
        self.statusBar().showMessage(label)
