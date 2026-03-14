import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QFileDialog, QMessageBox,
    QComboBox, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt
import settings


def _sep():
    """Tao duong phan cach ngang mong."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color: #21262d; background: #21262d; max-height: 1px;")
    return line


def _section(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setStyleSheet(
        "color: #58a6ff; font-size: 12px; font-weight: 700; "
        "letter-spacing: 0.8px; background: transparent; padding: 4px 0 2px 0;"
    )
    return lbl


class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_from_settings()

    def _build_ui(self):
        # Scroll area wrapping content
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 14, 20, 20)
        layout.setSpacing(14)

        # ── TOOLS ────────────────────────────────────────────
        layout.addWidget(_section("CONG CU"))

        ffmpeg_lbl = QLabel("Duong dan FFmpeg:")
        ffmpeg_lbl.setObjectName("field_label")
        layout.addWidget(ffmpeg_lbl)
        ff_row = QHBoxLayout()
        self.ffmpeg_input = QLineEdit()
        self.ffmpeg_input.setPlaceholderText("ffmpeg  hoac  C:/ffmpeg/bin/ffmpeg.exe")
        ff_row.addWidget(self.ffmpeg_input)
        btn_ff = QPushButton("Tim file")
        btn_ff.setFixedWidth(80)
        btn_ff.clicked.connect(lambda: self._browse_exe(self.ffmpeg_input))
        ff_row.addWidget(btn_ff)
        layout.addLayout(ff_row)

        ytdlp_lbl = QLabel("Duong dan yt-dlp:")
        ytdlp_lbl.setObjectName("field_label")
        layout.addWidget(ytdlp_lbl)
        yt_row = QHBoxLayout()
        self.ytdlp_input = QLineEdit()
        self.ytdlp_input.setPlaceholderText("yt-dlp  hoac  C:/tools/yt-dlp.exe")
        yt_row.addWidget(self.ytdlp_input)
        btn_yt = QPushButton("Tim file")
        btn_yt.setFixedWidth(80)
        btn_yt.clicked.connect(lambda: self._browse_exe(self.ytdlp_input))
        yt_row.addWidget(btn_yt)
        layout.addLayout(yt_row)

        layout.addWidget(_sep())

        # ── FOLDERS ──────────────────────────────────────────
        layout.addWidget(_section("THU MUC MAC DINH"))

        out_lbl = QLabel("Thu muc xuat mac dinh:")
        out_lbl.setObjectName("field_label")
        layout.addWidget(out_lbl)
        out_row = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("D:/ReupOutput")
        out_row.addWidget(self.output_input)
        btn_out = QPushButton("Chon")
        btn_out.setFixedWidth(80)
        btn_out.clicked.connect(lambda: self._browse_folder(self.output_input))
        out_row.addWidget(btn_out)
        layout.addLayout(out_row)

        sc_lbl = QLabel("Thu muc Scripts:")
        sc_lbl.setObjectName("field_label")
        layout.addWidget(sc_lbl)
        sc_row = QHBoxLayout()
        self.scripts_input = QLineEdit()
        self.scripts_input.setPlaceholderText("scripts")
        sc_row.addWidget(self.scripts_input)
        btn_sc = QPushButton("Chon")
        btn_sc.setFixedWidth(80)
        btn_sc.clicked.connect(lambda: self._browse_folder(self.scripts_input))
        sc_row.addWidget(btn_sc)
        layout.addLayout(sc_row)

        layout.addWidget(_sep())

        # ── DOWNLOAD OPTIONS ─────────────────────────────────
        layout.addWidget(_section("TUY CHON TAI VE"))

        ql_lbl = QLabel("Chat luong mac dinh:")
        ql_lbl.setObjectName("field_label")
        layout.addWidget(ql_lbl)
        self.combo_quality = QComboBox()
        self.combo_quality.addItems(["best", "1080p", "720p", "480p"])
        self.combo_quality.setFixedWidth(200)
        layout.addWidget(self.combo_quality)

        self.chk_no_watermark = QCheckBox("Khong watermark TikTok (mac dinh)")
        layout.addWidget(self.chk_no_watermark)

        proxy_lbl = QLabel("Proxy (de trong neu khong dung):")
        proxy_lbl.setObjectName("field_label")
        layout.addWidget(proxy_lbl)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:7890")
        layout.addWidget(self.proxy_input)

        layout.addWidget(_sep())

        # ── PROCESSING OPTIONS ───────────────────────────────
        layout.addWidget(_section("TUY CHON XU LY"))

        nm_lbl = QLabel("Mau ten file xuat ({name} = ten goc):")
        nm_lbl.setObjectName("field_label")
        layout.addWidget(nm_lbl)
        self.naming_input = QLineEdit()
        self.naming_input.setPlaceholderText("{name}_reup")
        layout.addWidget(self.naming_input)

        layout.addWidget(_sep())

        # ── SAVE / RESET ─────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Luu tat ca cai dat")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setMinimumWidth(200)
        self.btn_reset = QPushButton("Reset ve mac dinh")
        self.btn_reset.setObjectName("btn_flat")
        self.btn_reset.setFixedHeight(40)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_reset)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

        scroll.setWidget(container)

        # Full-size scroll area in self
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.btn_save.clicked.connect(self._save)
        self.btn_reset.clicked.connect(self._reset)

    # ─────────────────────────────────────────────────────────

    def _browse_exe(self, target: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chon file thuc thi", "", "Executables (*.exe);;All Files (*)"
        )
        if path:
            target.setText(path)

    def _browse_folder(self, target: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Chon thu muc")
        if folder:
            target.setText(folder)

    def _load_from_settings(self):
        s = settings.load_settings()
        self.ffmpeg_input.setText(s.get("ffmpeg_path", "ffmpeg"))
        self.ytdlp_input.setText(s.get("ytdlp_path", "yt-dlp"))
        self.output_input.setText(s.get("output_folder", ""))
        self.scripts_input.setText(s.get("scripts_folder", "scripts"))
        self.proxy_input.setText(s.get("proxy", ""))
        self.naming_input.setText(s.get("output_naming", "{name}_reup"))
        self.chk_no_watermark.setChecked(s.get("no_watermark_tiktok", True))
        try:
            idx = ["best", "1080p", "720p", "480p"].index(s.get("download_quality", "best"))
            self.combo_quality.setCurrentIndex(idx)
        except ValueError:
            pass

    def _save(self):
        s = settings.load_settings()
        s["ffmpeg_path"]       = self.ffmpeg_input.text().strip() or "ffmpeg"
        s["ytdlp_path"]        = self.ytdlp_input.text().strip() or "yt-dlp"
        s["output_folder"]     = self.output_input.text().strip()
        s["scripts_folder"]    = self.scripts_input.text().strip() or "scripts"
        s["proxy"]             = self.proxy_input.text().strip()
        s["output_naming"]     = self.naming_input.text().strip() or "{name}_reup"
        s["no_watermark_tiktok"] = self.chk_no_watermark.isChecked()
        s["download_quality"]  = self.combo_quality.currentText()
        settings.save_settings(s)
        QMessageBox.information(self, "Da luu", "Cai dat da duoc luu thanh cong!")

    def _reset(self):
        reply = QMessageBox.question(
            self, "Reset cai dat",
            "Ban co chac muon reset ve mac dinh?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            settings.save_settings(dict(settings.DEFAULT_SETTINGS))
            self._load_from_settings()
