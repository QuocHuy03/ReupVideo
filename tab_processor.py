import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QFileDialog, QAbstractItemView, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
import settings
import processor

STATUS_COLORS = {
    "Dang xu ly...": "#e3b341",
    "Xong":   "#2ea043",
    "Loi":    "#f85149",
    "Bo qua": "#8b949e",
    "Cho":    "#484f58",
}


class ProcessorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        # ── Folders row ───────────────────────────────────────
        folders_row = QHBoxLayout()
        folders_row.setSpacing(16)

        in_col = QVBoxLayout()
        in_col.addWidget(QLabel("Thu muc video dau vao:"))
        in_h = QHBoxLayout()
        self.input_dir = QLineEdit()
        self.input_dir.setPlaceholderText("Chon thu muc chua video...")
        in_h.addWidget(self.input_dir)
        btn_in = QPushButton("Chon")
        btn_in.setFixedWidth(68)
        btn_in.clicked.connect(self._browse_input)
        in_h.addWidget(btn_in)
        in_col.addLayout(in_h)
        folders_row.addLayout(in_col)

        out_col = QVBoxLayout()
        out_col.addWidget(QLabel("Thu muc xuat:"))
        out_h = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Chon thu muc xuat...")
        out_h.addWidget(self.output_dir)
        btn_out = QPushButton("Chon")
        btn_out.setFixedWidth(68)
        btn_out.clicked.connect(self._browse_output)
        out_h.addWidget(btn_out)
        out_col.addLayout(out_h)
        folders_row.addLayout(out_col)

        root.addLayout(folders_row)

        # ── Script selector row ───────────────────────────────
        sc_row = QHBoxLayout()
        sc_row.setSpacing(16)

        combo_col = QVBoxLayout()
        combo_col.addWidget(QLabel("Chon Script FFmpeg:"))
        sc_h = QHBoxLayout()
        self.script_combo = QComboBox()
        sc_h.addWidget(self.script_combo, stretch=1)
        btn_load = QPushButton("Load")
        btn_load.setFixedWidth(68)
        btn_load.clicked.connect(self._load_script)
        sc_h.addWidget(btn_load)
        btn_ref = QPushButton("Refresh")
        btn_ref.setFixedWidth(78)
        btn_ref.clicked.connect(self._refresh_scripts)
        sc_h.addWidget(btn_ref)
        combo_col.addLayout(sc_h)
        sc_row.addLayout(combo_col, stretch=2)

        naming_col = QVBoxLayout()
        naming_col.addWidget(QLabel("Ten file xuat ({name} = ten goc):"))
        self.naming_input = QLineEdit("{name}_reup")
        naming_col.addWidget(self.naming_input)
        sc_row.addLayout(naming_col, stretch=1)

        root.addLayout(sc_row)

        # ── Script preview ────────────────────────────────────
        root.addWidget(QLabel("Preview lenh FFmpeg (co the sua truc tiep):"))
        self.script_preview = QTextEdit()
        self.script_preview.setPlaceholderText("ffmpeg -y -i {input} ... {output}.mp4")
        self.script_preview.setFixedHeight(62)
        self.script_preview.setFont(QFont("Consolas", 11))
        self.script_preview.setStyleSheet(
            "background-color: #010409; color: #7ee787;"
            " border: 1px solid #30363d; border-radius: 6px; padding: 8px;"
        )
        root.addWidget(self.script_preview)

        # ── Action buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_load_files = QPushButton("Load video tu thu muc")
        self.btn_load_files.setObjectName("btn_primary")
        self.btn_run  = QPushButton("Bat dau xu ly")
        self.btn_run.setObjectName("btn_success")
        self.btn_stop = QPushButton("Dung")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setEnabled(False)
        self.btn_skip = QPushButton("Bo qua file hien tai")
        self.btn_skip.setEnabled(False)
        for b in [self.btn_load_files, self.btn_run, self.btn_stop, self.btn_skip]:
            b.setFixedHeight(36)
        btn_row.addWidget(self.btn_load_files)
        btn_row.addWidget(self.btn_run)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_skip)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # ── Splitter: file table | log ────────────────────────
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        tbl_frame = QWidget()
        tbl_lay = QVBoxLayout(tbl_frame)
        tbl_lay.setContentsMargins(0, 0, 0, 0)
        tbl_lay.setSpacing(4)
        tbl_lay.addWidget(QLabel("Danh sach video:"))
        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(["Ten file", "Kich thuoc", "Trang thai"])
        h = self.file_table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_table.verticalHeader().setVisible(False)
        tbl_lay.addWidget(self.file_table)
        splitter.addWidget(tbl_frame)

        log_frame = QWidget()
        log_lay = QVBoxLayout(log_frame)
        log_lay.setContentsMargins(0, 0, 0, 0)
        log_lay.setSpacing(4)
        log_lay.addWidget(QLabel("Log xu ly:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Consolas", 11))
        log_lay.addWidget(self.log_box)
        splitter.addWidget(log_frame)

        splitter.setSizes([260, 130])
        root.addWidget(splitter, stretch=1)

        # ── Connections ───────────────────────────────────────
        self.btn_load_files.clicked.connect(self._load_files)
        self.btn_run.clicked.connect(self._start_processing)
        self.btn_stop.clicked.connect(self._stop_processing)
        self.btn_skip.clicked.connect(self._skip_file)

        self._refresh_scripts()
        s = settings.load_settings()
        if s.get("input_folder"):
            self.input_dir.setText(s["input_folder"])
        if s.get("output_folder"):
            self.output_dir.setText(s["output_folder"])

    # ─────────────────────────────────────────────────────────

    def _refresh_scripts(self):
        s = settings.load_settings()
        self.script_combo.clear()
        self.script_combo.addItems(processor.get_scripts(s.get("scripts_folder", "scripts")))

    def _load_script(self):
        name = self.script_combo.currentText()
        if name:
            s = settings.load_settings()
            self.script_preview.setPlainText(
                processor.read_script(name, s.get("scripts_folder", "scripts"))
            )

    def _browse_input(self):
        folder = QFileDialog.getExistingDirectory(self, "Chon thu muc video")
        if folder:
            self.input_dir.setText(folder)
            settings.set_value("input_folder", folder)
            self._load_files()

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Chon thu muc xuat")
        if folder:
            self.output_dir.setText(folder)
            settings.set_value("output_folder", folder)

    def _load_files(self):
        folder = self.input_dir.text().strip()
        if not folder:
            folder = QFileDialog.getExistingDirectory(self, "Chon thu muc video")
            if folder:
                self.input_dir.setText(folder)
        if not folder:
            return
        files = processor.get_video_files(folder)
        self.file_table.setRowCount(0)
        for f in files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            self.file_table.setItem(row, 0, QTableWidgetItem(os.path.basename(f)))
            size_mb = os.path.getsize(f) / (1024 * 1024)
            self.file_table.setItem(row, 1, QTableWidgetItem(f"{size_mb:.1f} MB"))
            si = QTableWidgetItem("Cho")
            si.setForeground(QColor("#484f58"))
            self.file_table.setItem(row, 2, si)
        self._log(f"Da load {len(files)} file video")

    def _start_processing(self):
        if self._worker and self._worker.isRunning():
            return
        in_dir  = self.input_dir.text().strip()
        out_dir = self.output_dir.text().strip()
        cmd     = self.script_preview.toPlainText().strip()
        if not in_dir or not out_dir or not cmd:
            self._log("Vui long dien day du thu muc va script!")
            return
        files = processor.get_video_files(in_dir)
        if not files:
            self._log("Khong tim thay video trong thu muc dau vao!")
            return
        tasks  = [{"path": f, "row": i} for i, f in enumerate(files)]
        naming = self.naming_input.text().strip() or "{name}_reup"
        self._worker = processor.ProcessWorker(tasks, out_dir, cmd, naming)
        self._worker.file_status.connect(self._on_file_status)
        self._worker.log.connect(self._log)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_skip.setEnabled(True)
        self._log(f"Bat dau xu ly {len(files)} video...")

    def _stop_processing(self):
        if self._worker:
            self._worker.stop()
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_skip.setEnabled(False)

    def _skip_file(self):
        if self._worker:
            self._worker.skip()

    def _on_file_status(self, row: int, status: str):
        item = self.file_table.item(row, 2)
        if item:
            item.setText(status)
            item.setForeground(QColor(STATUS_COLORS.get(status, "#e6edf3")))

    def _on_finished(self, success: int, errors: int):
        self._log(f"Xong! {success} OK | {errors} loi")
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_skip.setEnabled(False)

    def _log(self, msg: str):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum())
