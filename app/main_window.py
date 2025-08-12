import os
import time
import re
from typing import Dict, List

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QFileDialog, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet

from .script_manager import (
    list_script_files,
    read_script,
    extract_placeholders,
    categorize_placeholder,
    default_value_for,
    parse_param_meta,
)
from .ffmpeg_runner import run_ffmpeg


RESERVED_PLACEHOLDERS = {"input", "output", "output_base", "filename", "name_no_ext", "ext", "now_ts"}


class VideoReupTool(QWidget):
    def __init__(self) -> None:
        super().__init__()
        apply_stylesheet(self, theme='light_blue.xml')
        self.setWindowTitle("Reup Video Tool")
        self.resize(1000, 780)

        self._placeholder_widgets: Dict[str, QLineEdit] = {}

        self._build_ui()
        self._connect_events()
        self._load_script_list()

    def _build_ui(self) -> None:
        self.input_folder = QLineEdit()
        self.output_folder = QLineEdit()
        self.script_combo = QComboBox()
        self.command_preview = QTextEdit()

        self.browse_input_btn = QPushButton("📁 Chọn thư mục video")
        self.browse_output_btn = QPushButton("📁 Chọn thư mục xuất")
        self.refresh_script_btn = QPushButton("🔄 Làm mới danh sách script")
        self.load_script_btn = QPushButton("📜 Xem mã FFmpeg")
        self.run_btn = QPushButton("⚙️ Chạy xử lý")

        # Params area
        self.params_group = QGroupBox("Thông số script (placeholder)")
        self.params_form = QFormLayout()
        self.params_group.setLayout(self.params_form)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["TÊN VIDEO", "THỜI GIAN (S)", "TRẠNG THÁI"])
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        for widgets in (
            (self.input_folder, self.browse_input_btn),
            (self.output_folder, self.browse_output_btn),
            (self.script_combo, self.refresh_script_btn),
        ):
            h = QHBoxLayout()
            h.addWidget(widgets[0])
            h.addWidget(widgets[1])
            layout.addLayout(h)

        action_row = QHBoxLayout()
        action_row.addWidget(self.load_script_btn)
        action_row.addWidget(self.run_btn)
        layout.addLayout(action_row)

        layout.addWidget(QLabel("📄 Preview mã FFmpeg:"))
        layout.addWidget(self.command_preview)

        layout.addWidget(self.params_group)

        layout.addWidget(QLabel("📋 Bảng kết quả xử lý:"))
        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def _connect_events(self) -> None:
        self.browse_input_btn.clicked.connect(self._select_input_folder)
        self.browse_output_btn.clicked.connect(self._select_output_folder)
        self.refresh_script_btn.clicked.connect(self._load_script_list)
        self.load_script_btn.clicked.connect(self._load_ffmpeg_script)
        self.run_btn.clicked.connect(self._process_videos)

    def _select_input_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa video")
        if folder:
            self.input_folder.setText(folder)

    def _select_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất video")
        if folder:
            self.output_folder.setText(folder)

    def _load_script_list(self) -> None:
        self.script_combo.clear()
        self.script_combo.addItems(list_script_files())

    def _clear_params_form(self) -> None:
        # Remove old widgets from form
        while self.params_form.rowCount():
            self.params_form.removeRow(0)
        self._placeholder_widgets.clear()

    def _add_param_input(self, name: str, category: str, default_value: str) -> None:
        field = QLineEdit()
        if default_value:
            field.setText(default_value)
        field.setPlaceholderText(name)

        if category == "file":
            browse_btn = QPushButton("...")
            def browse_file() -> None:
                path, _ = QFileDialog.getOpenFileName(self, f"Chọn file cho {name}")
                if path:
                    field.setText(path)
            container = QHBoxLayout()
            container_widget = QWidget()
            container.addWidget(field)
            container.addWidget(browse_btn)
            container.setContentsMargins(0, 0, 0, 0)
            container_widget.setLayout(container)
            browse_btn.clicked.connect(browse_file)
            self.params_form.addRow(QLabel(name), container_widget)
        else:
            self.params_form.addRow(QLabel(name), field)

        self._placeholder_widgets[name] = field

    def _load_ffmpeg_script(self) -> None:
        selected = self.script_combo.currentText()
        if not selected:
            return
        content = read_script(selected)
        self.command_preview.setPlainText(content)
        # Build param inputs
        self._clear_params_form()
        metas = parse_param_meta(content)
        for name in extract_placeholders(content):
            if name in RESERVED_PLACEHOLDERS:
                continue
            # Apply meta override
            if name in metas:
                meta = metas[name]
                category = meta.type
                default_value = meta.default if meta.default is not None else default_value_for(name)
                label = meta.label or name
                # For now reuse QLineEdit; file inputs will use the file dialog; future: number spinbox, dropdown
                self._add_param_input(name, category, default_value)
                # Update label text if custom label provided
                row = self.params_form.rowCount() - 1
                item_label = self.params_form.itemAt(row, QFormLayout.LabelRole)
                if item_label and isinstance(item_label.widget(), QLabel) and meta.label:
                    item_label.widget().setText(meta.label)
            else:
                category = categorize_placeholder(name)
                default_value = default_value_for(name)
                self._add_param_input(name, category, default_value)

    def _process_videos(self) -> None:
        self.run_btn.setEnabled(False)
        self.result_table.setRowCount(0)

        input_dir = self.input_folder.text().strip()
        output_dir = self.output_folder.text().strip()
        command_template = self.command_preview.toPlainText().strip()

        if not input_dir or not output_dir or not command_template:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin.")
            self.run_btn.setEnabled(True)
            return

        os.makedirs(output_dir, exist_ok=True)

        files = [
            f for f in os.listdir(input_dir)
            if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"))
        ]

        # Build user param values (as-is strings)
        user_params: Dict[str, str] = {name: widget.text().strip() for name, widget in self._placeholder_widgets.items()}

        for file in files:
            input_path = os.path.join(input_dir, file)
            name_no_ext, ext = os.path.splitext(file)
            ext = ext.lstrip('.')

            # Output base path (no extension)
            output_base = os.path.join(output_dir, f"{name_no_ext}_reup")

            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            self.result_table.setItem(row, 0, QTableWidgetItem(file))
            self.result_table.setItem(row, 1, QTableWidgetItem("..."))
            self.result_table.setItem(row, 2, QTableWidgetItem("🔧 Đang xử lý"))

            # Build replacements dictionary
            replacements: Dict[str, str] = {}

            # Standard placeholders
            replacements["input"] = f'"{input_path}"'
            replacements["output_base"] = f'"{output_base}"'
            # For convenience provide many output_* with extensions
            for out_ext in ("mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "aac", "m4a", "png", "jpg"):
                replacements[f"output_{out_ext}"] = f'"{output_base}.{out_ext}"'
            # Backward-compat: {output} equals base without extension
            replacements["output"] = f'"{output_base}"'

            # Context placeholders
            replacements["filename"] = f'"{file}"'
            replacements["name_no_ext"] = f'"{name_no_ext}"'
            replacements["ext"] = f'"{ext}"'
            replacements["now_ts"] = str(int(time.time()))

            # User-provided placeholders
            # Special-case file-like placeholders: auto-quote
            file_like_names = {n for n, _ in self._placeholder_widgets.items() if categorize_placeholder(n) == "file"}
            for key, value in user_params.items():
                if key in file_like_names and value:
                    replacements[key] = f'"{value}"'
                elif value:
                    replacements[key] = value

            # Perform replacement - replace longer keys first to avoid partial overlaps
            command = command_template
            for key in sorted(replacements.keys(), key=lambda k: -len(k)):
                command = command.replace("{" + key + "}", replacements[key])

            ok, duration, _ = run_ffmpeg(command)
            if ok:
                self.result_table.item(row, 1).setText(f"{duration:.2f}")
                self.result_table.item(row, 2).setText("✅ Hoàn tất")
            else:
                self.result_table.item(row, 1).setText("0.00")
                self.result_table.item(row, 2).setText("❌ Lỗi xử lý")

        self.run_btn.setEnabled(True)

