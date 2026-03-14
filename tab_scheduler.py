from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTimeEdit, QCheckBox, QFrame, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QTime
import settings


class SchedulerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_schedule)
        self._timer.start(30000)
        self._build_ui()
        self._refresh_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)



        cfg_frame = QFrame()
        cfg_frame.setObjectName("card")
        cfg_layout = QVBoxLayout(cfg_frame)
        cfg_layout.setSpacing(14)

        self.chk_enable = QCheckBox("Bat lich tu dong")
        self.chk_enable.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.chk_enable.toggled.connect(self._on_toggle)
        cfg_layout.addWidget(self.chk_enable)

        time_row = QHBoxLayout()
        time_lbl = QLabel("Gio chay:")
        time_lbl.setObjectName("field_label")
        time_lbl.setFixedWidth(80)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setFixedWidth(100)
        self.time_edit.setFixedHeight(38)
        time_row.addWidget(time_lbl)
        time_row.addWidget(self.time_edit)
        time_row.addStretch()
        cfg_layout.addLayout(time_row)

        action_row = QHBoxLayout()
        action_lbl = QLabel("Hanh dong:")
        action_lbl.setObjectName("field_label")
        action_lbl.setFixedWidth(100)
        self.combo_action = QComboBox()
        self.combo_action.addItems([
            "Tai video + Xu ly",
            "Chi tai video",
            "Chi xu ly video",
        ])
        action_row.addWidget(action_lbl)
        action_row.addWidget(self.combo_action)
        action_row.addStretch()
        cfg_layout.addLayout(action_row)

        btn_save = QPushButton("Luu cai dat lich")
        btn_save.setObjectName("btn_primary")
        btn_save.setFixedHeight(38)
        btn_save.setFixedWidth(200)
        btn_save.clicked.connect(self._save_schedule)
        cfg_layout.addWidget(btn_save)

        layout.addWidget(cfg_frame)

        status_frame = QFrame()
        status_frame.setObjectName("card")
        status_layout = QVBoxLayout(status_frame)
        status_title = QLabel("Trang thai lich")
        status_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #e6edf3; background: transparent;")
        status_layout.addWidget(status_title)

        self.status_label = QLabel("Chua bat lich")
        self.status_label.setStyleSheet("color: #8b949e; font-size: 13px; background: transparent; padding: 8px 0;")
        status_layout.addWidget(self.status_label)

        self.next_run_label = QLabel()
        self.next_run_label.setStyleSheet("color: #00d4ff; font-size: 13px; background: transparent;")
        status_layout.addWidget(self.next_run_label)

        layout.addWidget(status_frame)

        log_title = QLabel("Lich su chay:")
        log_title.setObjectName("field_label")
        layout.addWidget(log_title)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        layout.addStretch()

    def _refresh_ui(self):
        s = settings.load_settings()
        enabled = s.get("scheduler_enabled", False)
        self.chk_enable.setChecked(enabled)
        h = s.get("scheduler_hour", 6)
        m = s.get("scheduler_minute", 0)
        self.time_edit.setTime(QTime(h, m))

        action_map = {
            "download_and_process": 0,
            "download_only": 1,
            "process_only": 2,
        }
        idx = action_map.get(s.get("scheduler_action", "download_and_process"), 0)
        self.combo_action.setCurrentIndex(idx)
        self._update_status_display(enabled, h, m)

    def _on_toggle(self, checked: bool):
        settings.set_value("scheduler_enabled", checked)
        s = settings.load_settings()
        self._update_status_display(checked, s.get("scheduler_hour", 6), s.get("scheduler_minute", 0))

    def _save_schedule(self):
        t = self.time_edit.time()
        action_vals = ["download_and_process", "download_only", "process_only"]
        action = action_vals[self.combo_action.currentIndex()]
        s = settings.load_settings()
        s["scheduler_hour"] = t.hour()
        s["scheduler_minute"] = t.minute()
        s["scheduler_action"] = action
        s["scheduler_enabled"] = self.chk_enable.isChecked()
        settings.save_settings(s)
        self._log(f"Da luu lich: {t.toString('HH:mm')} - {self.combo_action.currentText()}")
        self._update_status_display(s["scheduler_enabled"], t.hour(), t.minute())

    def _update_status_display(self, enabled: bool, hour: int, minute: int):
        if enabled:
            self.status_label.setText("Lich tu dong dang BAT")
            self.status_label.setStyleSheet("color: #2ea043; font-size: 13px; background: transparent;")
            self.next_run_label.setText(f"Lan chay tiep theo: {hour:02d}:{minute:02d}")
        else:
            self.status_label.setText("Lich tu dong dang TAT")
            self.status_label.setStyleSheet("color: #8b949e; font-size: 13px; background: transparent;")
            self.next_run_label.setText("")

    def _check_schedule(self):
        from datetime import datetime
        s = settings.load_settings()
        if not s.get("scheduler_enabled"):
            return
        now = datetime.now()
        h = s.get("scheduler_hour", 6)
        m = s.get("scheduler_minute", 0)
        if now.hour == h and now.minute == m:
            self._log(f"Lich tu dong kich hoat: {now.strftime('%H:%M %d/%m/%Y')}")

    def _log(self, msg: str):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )
