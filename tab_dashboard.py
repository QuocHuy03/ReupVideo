from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
import settings


class StatCard(QWidget):
    def __init__(self, title: str, value: str, color: str = "#00d4ff"):
        super().__init__()
        self.setObjectName("stat_card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 14, 16, 14)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat_number")
        self.value_label.setStyleSheet(
            f"color: {color}; font-size: 28px; font-weight: 700;"
            " background: transparent; border: none;"
        )
        title_label = QLabel(title)
        title_label.setObjectName("stat_label")
        title_label.setStyleSheet(
            "color: #8b949e; font-size: 12px; background: transparent; border: none;"
        )
        layout.addWidget(self.value_label)
        layout.addWidget(title_label)

    def set_value(self, v):
        self.value_label.setText(str(v))


class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self.refresh_stats)
        self._refresh_timer.start(5000)
        self.refresh_stats()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(14)

        # Stat cards — use expanding horizontal layout
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.card_downloaded = StatCard("Video da tai", "0", "#00d4ff")
        self.card_processed  = StatCard("Video da xu ly", "0", "#2ea043")
        self.card_errors     = StatCard("Loi", "0", "#f85149")
        self.card_scripts    = StatCard("Script FFmpeg", "0", "#e3b341")
        for c in [self.card_downloaded, self.card_processed, self.card_errors, self.card_scripts]:
            stats_row.addWidget(c)
        outer.addLayout(stats_row)

        # Quick actions card
        qa_frame = QFrame()
        qa_frame.setObjectName("card")
        qa_layout = QVBoxLayout(qa_frame)
        qa_layout.setSpacing(8)
        qa_title = QLabel("Thao tac nhanh")
        qa_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #e6edf3; background: transparent;"
        )
        qa_layout.addWidget(qa_title)

        btn_row = QHBoxLayout()
        self.btn_open_output = QPushButton("Mo thu muc xuat")
        self.btn_open_input  = QPushButton("Mo thu muc video")
        self.btn_reset_stats = QPushButton("Reset thong ke")
        self.btn_reset_stats.setObjectName("btn_flat")
        for b in [self.btn_open_output, self.btn_open_input, self.btn_reset_stats]:
            b.setFixedHeight(36)
        btn_row.addWidget(self.btn_open_output)
        btn_row.addWidget(self.btn_open_input)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_reset_stats)
        qa_layout.addLayout(btn_row)
        outer.addWidget(qa_frame)

        # System info card — flexible height
        info_frame = QFrame()
        info_frame.setObjectName("card")
        info_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        info_layout = QVBoxLayout(info_frame)
        info_title = QLabel("Thong tin he thong")
        info_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #e6edf3;"
            " background: transparent; padding-bottom: 6px;"
        )
        info_layout.addWidget(info_title)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignTop)
        self.info_label.setStyleSheet(
            "color: #8b949e; font-size: 13px; background: transparent;"
            " line-height: 180%;"
        )
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        outer.addWidget(info_frame, stretch=1)

        # Connections
        self.btn_open_output.clicked.connect(self._open_output)
        self.btn_open_input.clicked.connect(self._open_input)
        self.btn_reset_stats.clicked.connect(self._reset_stats)

    def refresh_stats(self):
        s = settings.load_settings()
        self.card_downloaded.set_value(s.get("stat_downloaded", 0))
        self.card_processed.set_value(s.get("stat_processed", 0))
        self.card_errors.set_value(s.get("stat_errors", 0))

        import os
        scripts_dir = s.get("scripts_folder", "scripts")
        n_scripts = 0
        if os.path.exists(scripts_dir):
            n_scripts = len([f for f in os.listdir(scripts_dir) if f.endswith(".txt")])
        self.card_scripts.set_value(n_scripts)

        ffmpeg = s.get("ffmpeg_path", "ffmpeg")
        ytdlp  = s.get("ytdlp_path", "yt-dlp")
        output = s.get("output_folder", "") or "(chua dat)"
        sched  = "Bat" if s.get("scheduler_enabled") else "Tat"
        self.info_label.setText(
            f"<b>FFmpeg:</b> {ffmpeg}<br>"
            f"<b>yt-dlp:</b> {ytdlp}<br>"
            f"<b>Thu muc xuat mac dinh:</b> {output}<br>"
            f"<b>Lich tu dong:</b> {sched}"
        )

    def _open_output(self):
        import subprocess, os
        folder = settings.get("output_folder", "")
        if folder and os.path.exists(folder):
            subprocess.Popen(f'explorer "{folder}"')

    def _open_input(self):
        import subprocess, os
        folder = settings.get("input_folder", "")
        if folder and os.path.exists(folder):
            subprocess.Popen(f'explorer "{folder}"')

    def _reset_stats(self):
        settings.set_value("stat_downloaded", 0)
        settings.set_value("stat_processed", 0)
        settings.set_value("stat_errors", 0)
        self.refresh_stats()
