import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QFileDialog, QAbstractItemView,
    QSplitter, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import settings
from downloader import DownloadWorker

STATUS_COLORS = {
    "Dang tai...": "#e3b341",
    "Xong":        "#2ea043",
    "Loi":         "#f85149",
    "Cho":         "#484f58",
}


class DownloaderTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        # ── Section 1: URL input ──────────────────────────────
        url_lbl = QLabel("Danh sach URL (moi dong 1 link):")
        url_lbl.setObjectName("field_label")
        root.addWidget(url_lbl)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "https://www.tiktok.com/@user/video/...\n"
            "https://www.youtube.com/watch?v=...\n"
            "https://www.instagram.com/p/..."
        )
        self.url_input.setFixedHeight(100)
        root.addWidget(self.url_input)

        # ── Section 2: Options row ────────────────────────────
        opts = QHBoxLayout()
        opts.setSpacing(16)

        # Platform
        p_col = QVBoxLayout()
        p_col.addWidget(QLabel("Nen tang:"))
        self.combo_platform = QComboBox()
        self.combo_platform.addItems([
            "Tu dong nhan dien", "TikTok", "YouTube", "Instagram", "Facebook"
        ])
        p_col.addWidget(self.combo_platform)
        opts.addLayout(p_col)

        # Quality
        q_col = QVBoxLayout()
        q_col.addWidget(QLabel("Chat luong:"))
        self.combo_quality = QComboBox()
        self.combo_quality.addItems(["best", "1080p", "720p", "480p"])
        q_col.addWidget(self.combo_quality)
        opts.addLayout(q_col)

        # Output folder
        o_col = QVBoxLayout()
        o_col.addWidget(QLabel("Thu muc tai ve:"))
        o_row = QHBoxLayout()
        self.out_dir = QLineEdit()
        self.out_dir.setPlaceholderText("Thu muc luu video...")
        o_row.addWidget(self.out_dir)
        btn_browse = QPushButton("Chon")
        btn_browse.setFixedWidth(68)
        btn_browse.clicked.connect(self._browse_output)
        o_row.addWidget(btn_browse)
        o_col.addLayout(o_row)
        opts.addLayout(o_col, stretch=2)

        root.addLayout(opts)

        # ── Section 3: Checkboxes ─────────────────────────────
        chk_row = QHBoxLayout()
        self.chk_no_watermark = QCheckBox("Khong watermark (TikTok)")
        self.chk_no_watermark.setChecked(True)
        self.chk_auto_reup = QCheckBox("Xu ly ngay sau khi tai xong")
        chk_row.addWidget(self.chk_no_watermark)
        chk_row.addWidget(self.chk_auto_reup)
        chk_row.addStretch()
        root.addLayout(chk_row)

        # ── Section 4: Action buttons ─────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_add   = QPushButton("Them vao Queue")
        self.btn_add.setObjectName("btn_primary")
        self.btn_start = QPushButton("Bat dau tai")
        self.btn_start.setObjectName("btn_success")
        self.btn_stop  = QPushButton("Dung")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setEnabled(False)
        self.btn_clear = QPushButton("Xoa tat ca")
        self.btn_clear.setObjectName("btn_flat")
        for b in [self.btn_add, self.btn_start, self.btn_stop, self.btn_clear]:
            b.setFixedHeight(36)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear)
        root.addLayout(btn_row)

        # ── Section 5: Splitter — queue table | log ───────────
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        # Queue table
        tbl_frame = QWidget()
        tbl_lay = QVBoxLayout(tbl_frame)
        tbl_lay.setContentsMargins(0, 0, 0, 0)
        tbl_lay.setSpacing(4)
        tbl_lay.addWidget(QLabel("Queue tai:"))

        self.queue_table = QTableWidget(0, 3)
        self.queue_table.setHorizontalHeaderLabels(["URL", "Nen tang", "Trang thai"])
        h = self.queue_table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.queue_table.setAlternatingRowColors(True)
        self.queue_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.queue_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.queue_table.verticalHeader().setVisible(False)
        tbl_lay.addWidget(self.queue_table)
        splitter.addWidget(tbl_frame)

        # Log
        log_frame = QWidget()
        log_lay = QVBoxLayout(log_frame)
        log_lay.setContentsMargins(0, 0, 0, 0)
        log_lay.setSpacing(4)
        log_lay.addWidget(QLabel("Log:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        log_lay.addWidget(self.log_box)
        splitter.addWidget(log_frame)

        splitter.setSizes([280, 130])
        root.addWidget(splitter, stretch=1)

        # ── Connections ───────────────────────────────────────
        self.btn_add.clicked.connect(self._add_to_queue)
        self.btn_start.clicked.connect(self._start_download)
        self.btn_stop.clicked.connect(self._stop_download)
        self.btn_clear.clicked.connect(self._clear_queue)

        # Load saved settings
        s = settings.load_settings()
        if s.get("output_folder"):
            self.out_dir.setText(s["output_folder"])
        try:
            q_idx = ["best", "1080p", "720p", "480p"].index(s.get("download_quality", "best"))
            self.combo_quality.setCurrentIndex(q_idx)
        except ValueError:
            pass
        self.chk_no_watermark.setChecked(s.get("no_watermark_tiktok", True))
        self.chk_auto_reup.setChecked(s.get("auto_reup_after_download", False))

    # ───────────────────── helpers ──────────────────────────

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Chon thu muc tai ve")
        if folder:
            self.out_dir.setText(folder)
            settings.set_value("output_folder", folder)

    def _detect_platform(self, url: str) -> str:
        u = url.lower()
        if "tiktok" in u:              return "TikTok"
        if "youtube" in u or "youtu.be" in u: return "YouTube"
        if "instagram" in u:           return "Instagram"
        if "facebook" in u or "fb.watch" in u: return "Facebook"
        return "Khac"

    def _add_to_queue(self):
        raw = self.url_input.toPlainText().strip()
        if not raw:
            return
        for url in [u.strip() for u in raw.splitlines() if u.strip()]:
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)
            self.queue_table.setItem(row, 0, QTableWidgetItem(url))
            self.queue_table.setItem(row, 1, QTableWidgetItem(self._detect_platform(url)))
            si = QTableWidgetItem("Cho")
            si.setForeground(QColor("#484f58"))
            self.queue_table.setItem(row, 2, si)
        self.url_input.clear()

    def _start_download(self):
        if self._worker and self._worker.isRunning():
            return
        out = self.out_dir.text().strip()
        if not out:
            self._log("Vui long chon thu muc tai ve!")
            return
        tasks = [{"url": self.queue_table.item(r, 0).text(), "row": r}
                 for r in range(self.queue_table.rowCount())]
        if not tasks:
            self._log("Queue trong, hay them URL truoc!")
            return
        opts = {"quality": self.combo_quality.currentText(),
                "no_watermark": self.chk_no_watermark.isChecked()}
        self._worker = DownloadWorker(tasks, out, opts)
        self._worker.progress.connect(self._on_progress)
        self._worker.log.connect(self._log)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self._log("Bat dau tai batch...")

    def _stop_download(self):
        if self._worker:
            self._worker.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def _clear_queue(self):
        self.queue_table.setRowCount(0)

    def _on_progress(self, row: int, status: str):
        item = self.queue_table.item(row, 2)
        if item:
            item.setText(status)
            item.setForeground(QColor(STATUS_COLORS.get(status, "#e6edf3")))

    def _on_finished(self, success: int, errors: int):
        self._log(f"Hoan thanh! {success} OK | {errors} loi")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def _log(self, msg: str):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum())
