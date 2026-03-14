import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QTextEdit, QLineEdit,
    QFrame, QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import settings
import processor


class ScriptManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_script = None
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(10)

        # Horizontal splitter: left list | right editor
        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.setChildrenCollapsible(False)

        # ---- Left: list ----
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(8)

        list_label = QLabel("Danh sach scripts:")
        list_label.setObjectName("field_label")
        left_layout.addWidget(list_label)

        self.script_list = QListWidget()
        self.script_list.currentTextChanged.connect(self._on_select_script)
        left_layout.addWidget(self.script_list, stretch=1)

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("Tao moi")
        self.btn_new.setObjectName("btn_success")
        self.btn_new.setFixedHeight(34)
        self.btn_delete = QPushButton("Xoa")
        self.btn_delete.setObjectName("btn_danger")
        self.btn_delete.setFixedHeight(34)
        btn_row.addWidget(self.btn_new)
        btn_row.addWidget(self.btn_delete)
        left_layout.addLayout(btn_row)

        self.btn_duplicate = QPushButton("Nhan ban")
        self.btn_duplicate.setFixedHeight(34)
        left_layout.addWidget(self.btn_duplicate)

        h_splitter.addWidget(left_widget)

        # ---- Right: editor ----
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(6)

        name_lbl = QLabel("Ten file (vi du: 21_custom.txt):")
        name_lbl.setObjectName("field_label")
        right_layout.addWidget(name_lbl)
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(34)
        self.name_input.setPlaceholderText("21_ten_script.txt")
        right_layout.addWidget(self.name_input)

        content_lbl = QLabel("Lenh FFmpeg (dung {input} va {output}):")
        content_lbl.setObjectName("field_label")
        right_layout.addWidget(content_lbl)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.editor.setStyleSheet(
            "background-color: #010409; color: #7ee787;"
            " border: 1px solid #30363d; border-radius: 8px; padding: 12px;"
        )
        self.editor.setPlaceholderText(
            "ffmpeg -y -i {input} -vf \"hflip,eq=contrast=1.2\" -c:v libx264 -c:a aac {output}.mp4"
        )
        right_layout.addWidget(self.editor, stretch=1)

        preview_lbl = QLabel("Xem truoc lenh thuc te:")
        preview_lbl.setObjectName("field_label")
        right_layout.addWidget(preview_lbl)
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet(
            "color: #8b949e; background: #161b22; border: 1px solid #21262d;"
            " border-radius: 6px; padding: 8px; font-family: Consolas; font-size: 11px;"
        )
        self.preview_label.setMinimumHeight(48)
        right_layout.addWidget(self.preview_label)

        action_row = QHBoxLayout()
        self.btn_save = QPushButton("Luu script")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.setFixedHeight(36)
        self.btn_preview_btn = QPushButton("Preview")
        self.btn_preview_btn.setFixedHeight(36)
        action_row.addWidget(self.btn_save)
        action_row.addWidget(self.btn_preview_btn)
        action_row.addStretch()
        right_layout.addLayout(action_row)

        h_splitter.addWidget(right_widget)
        h_splitter.setStretchFactor(0, 1)
        h_splitter.setStretchFactor(1, 3)
        h_splitter.setSizes([220, 580])

        outer.addWidget(h_splitter, stretch=1)

        # Help bar
        help_frame = QFrame()
        help_frame.setObjectName("card")
        help_layout = QVBoxLayout(help_frame)
        help_layout.setContentsMargins(12, 8, 12, 8)
        help_lbl = QLabel(
            "<b>Bien:</b> "
            "<code style='color:#00d4ff;'>{input}</code> = duong dan video dau vao &nbsp;"
            "<code style='color:#00d4ff;'>{output}</code> = duong dan xuat (khong can .mp4)<br>"
            "<code style='color:#7ee787;'>ffmpeg -y -i {input} -vf hflip {output}.mp4</code>"
        )
        help_lbl.setTextFormat(Qt.RichText)
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet("color: #8b949e; font-size: 12px; background: transparent;")
        help_layout.addWidget(help_lbl)
        outer.addWidget(help_frame)

        # Connections
        self.btn_new.clicked.connect(self._new_script)
        self.btn_delete.clicked.connect(self._delete_script)
        self.btn_duplicate.clicked.connect(self._duplicate_script)
        self.btn_save.clicked.connect(self._save_script)
        self.btn_preview_btn.clicked.connect(self._update_preview)
        self.editor.textChanged.connect(self._update_preview)

    def _refresh_list(self):
        s = settings.load_settings()
        scripts = processor.get_scripts(s.get("scripts_folder", "scripts"))
        self.script_list.clear()
        for sc in scripts:
            self.script_list.addItem(sc)

    def _on_select_script(self, name: str):
        if not name:
            return
        self._current_script = name
        self.name_input.setText(name)
        s = settings.load_settings()
        content = processor.read_script(name, s.get("scripts_folder", "scripts"))
        self.editor.setPlainText(content)
        self._update_preview()

    def _new_script(self):
        self._current_script = None
        self.script_list.clearSelection()
        next_num = self.script_list.count() + 1
        self.name_input.setText(f"{next_num:02d}_new_script.txt")
        self.editor.clear()
        self.preview_label.clear()

    def _delete_script(self):
        item = self.script_list.currentItem()
        if not item:
            return
        name = item.text()
        reply = QMessageBox.question(self, "Xac nhan xoa",
                                     f"Ban co chac muon xoa '{name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            s = settings.load_settings()
            processor.delete_script(name, s.get("scripts_folder", "scripts"))
            self._refresh_list()
            self.editor.clear()
            self.name_input.clear()

    def _duplicate_script(self):
        item = self.script_list.currentItem()
        if not item:
            return
        s = settings.load_settings()
        name = item.text()
        content = processor.read_script(name, s.get("scripts_folder", "scripts"))
        new_name = name.replace(".txt", "_copy.txt")
        processor.save_script(new_name, content, s.get("scripts_folder", "scripts"))
        self._refresh_list()

    def _save_script(self):
        name = self.name_input.text().strip()
        content = self.editor.toPlainText().strip()
        if not name:
            return
        if not name.endswith(".txt"):
            name += ".txt"
        s = settings.load_settings()
        processor.save_script(name, content, s.get("scripts_folder", "scripts"))
        self._current_script = name
        self._refresh_list()
        for i in range(self.script_list.count()):
            if self.script_list.item(i).text() == name:
                self.script_list.setCurrentRow(i)
                break

    def _update_preview(self):
        content = self.editor.toPlainText().strip()
        if content:
            demo = (content
                    .replace("{input}", '"E:/Videos/sample.mp4"')
                    .replace("{output}", '"E:/Output/sample_reup"'))
            self.preview_label.setText(demo[:300])
        else:
            self.preview_label.setText("")
