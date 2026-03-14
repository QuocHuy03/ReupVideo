
DARK_THEME = """
/* ===== Global ===== */
QWidget {
 background-color: #0d1117;
 color: #e6edf3;
 font-family: 'Open Sans', 'Segoe UI', 'Arial', sans-serif;
 font-size: 13px;
}

QMainWindow {
 background-color: #0d1117;
}

/* ===== Scrollbar ===== */
QScrollBar:vertical {
 background: #161b22;
 width: 8px;
 border-radius: 4px;
}
QScrollBar::handle:vertical {
 background: #30363d;
 border-radius: 4px;
 min-height: 20px;
}
QScrollBar::handle:vertical:hover {
 background: #00d4ff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
 height: 0px;
}
QScrollBar:horizontal {
 background: #161b22;
 height: 8px;
 border-radius: 4px;
}
QScrollBar::handle:horizontal {
 background: #30363d;
 border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
 background: #00d4ff;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
 width: 0px;
}

/* ===== Sidebar ===== */
#sidebar {
 background-color: #010409;
 border-right: 1px solid #21262d;
 min-width: 200px;
 max-width: 200px;
}

#sidebar_btn {
 background-color: transparent;
 color: #8b949e;
 border: none;
 border-radius: 8px;
 text-align: left;
 padding: 10px 16px;
 font-size: 13px;
 font-weight: 500;
}
#sidebar_btn:hover {
 background-color: #161b22;
 color: #e6edf3;
}
#sidebar_btn[active="true"] {
 background-color: #1f2937;
 color: #00d4ff;
 border-left: 3px solid #00d4ff;
}

#logo_label {
 color: #00d4ff;
 font-size: 18px;
 font-weight: 700;
 padding: 20px 16px 10px 16px;
 letter-spacing: 1px;
}

#version_label {
 color: #484f58;
 font-size: 11px;
 padding: 0px 16px 16px 16px;
}

/* ===== Cards ===== */
#card {
 background-color: #161b22;
 border: 1px solid #21262d;
 border-radius: 10px;
 padding: 16px;
}

#stat_card {
 background-color: #161b22;
 border: 1px solid #21262d;
 border-radius: 12px;
 padding: 16px;
 min-width: 140px;
}

#stat_number {
 color: #00d4ff;
 font-size: 28px;
 font-weight: 700;
}

#stat_label {
 color: #8b949e;
 font-size: 12px;
}

/* ===== Labels ===== */
#section_title {
 color: #e6edf3;
 font-size: 20px;
 font-weight: 700;
 padding-bottom: 4px;
}

#section_sub {
 color: #8b949e;
 font-size: 13px;
 padding-bottom: 12px;
}

#field_label {
 color: #8b949e;
 font-size: 12px;
 font-weight: 600;
 padding-bottom: 3px;
 padding-top: 6px;
}

/* ===== Inputs ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
 background-color: #0d1117;
 border: 1px solid #30363d;
 border-radius: 8px;
 padding: 8px 12px;
 color: #e6edf3;
 selection-background-color: #1f6feb;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
 border: 1px solid #00d4ff;
 outline: none;
}
QLineEdit:read-only {
 background-color: #161b22;
 color: #8b949e;
}

/* ===== ComboBox ===== */
QComboBox {
 background-color: #161b22;
 border: 1px solid #30363d;
 border-radius: 8px;
 padding: 8px 12px;
 color: #e6edf3;
 min-height: 20px;
}
QComboBox:hover {
 border-color: #58a6ff;
}
QComboBox:focus {
 border-color: #00d4ff;
}
QComboBox::drop-down {
 border: none;
 width: 24px;
}
QComboBox::down-arrow {
 image: none;
 border-left: 5px solid transparent;
 border-right: 5px solid transparent;
 border-top: 5px solid #8b949e;
 margin-right: 8px;
}
QComboBox QAbstractItemView {
 background-color: #161b22;
 border: 1px solid #30363d;
 border-radius: 8px;
 selection-background-color: #1f2937;
 color: #e6edf3;
 padding: 4px;
}

/* ===== Buttons ===== */
QPushButton {
 background-color: #21262d;
 color: #e6edf3;
 border: 1px solid #30363d;
 border-radius: 8px;
 padding: 8px 16px;
 font-weight: 600;
 font-size: 13px;
 min-height: 20px;
}
QPushButton:hover {
 background-color: #30363d;
 border-color: #484f58;
}
QPushButton:pressed {
 background-color: #161b22;
}
QPushButton:disabled {
 color: #484f58;
 border-color: #21262d;
 background-color: #161b22;
}

#btn_primary {
 background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #00d4ff);
 color: #0d1117;
 border: none;
 font-weight: 700;
 border-radius: 8px;
 padding: 9px 20px;
}
#btn_primary:hover {
 background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #22d3ee);
}
#btn_primary:pressed {
 background: #0284c7;
}
#btn_primary:disabled {
 background: #21262d;
 color: #484f58;
}

#btn_danger {
 background-color: #da3633;
 color: #fff;
 border: none;
 font-weight: 600;
}
#btn_danger:hover {
 background-color: #f85149;
}

#btn_success {
 background-color: #238636;
 color: #fff;
 border: none;
 font-weight: 600;
}
#btn_success:hover {
 background-color: #2ea043;
}

#btn_warning {
 background-color: #9e6a03;
 color: #fff;
 border: none;
 font-weight: 600;
}
#btn_warning:hover {
 background-color: #bb8009;
}

#btn_flat {
 background-color: transparent;
 border: 1px solid #30363d;
 color: #8b949e;
 border-radius: 6px;
 padding: 6px 12px;
 font-size: 12px;
}
#btn_flat:hover {
 background-color: #161b22;
 color: #e6edf3;
}

/* ===== Tables ===== */
QTableWidget {
 background-color: #161b22;
 border: 1px solid #21262d;
 border-radius: 8px;
 gridline-color: #21262d;
 alternate-background-color: #0d1117;
}
QTableWidget::item {
 padding: 8px 12px;
 border-bottom: 1px solid #21262d;
}
QTableWidget::item:selected {
 background-color: #1f2937;
 color: #e6edf3;
}
QHeaderView::section {
 background-color: #010409;
 color: #8b949e;
 padding: 8px 12px;
 font-size: 12px;
 font-weight: 600;
 text-transform: uppercase;
 letter-spacing: 0.5px;
 border: none;
 border-bottom: 1px solid #21262d;
}

/* ===== Progress Bar ===== */
QProgressBar {
 background-color: #21262d;
 border-radius: 6px;
 height: 10px;
 text-align: center;
 color: transparent;
 border: none;
}
QProgressBar::chunk {
 background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #00d4ff);
 border-radius: 6px;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
 border: 1px solid #21262d;
 border-radius: 8px;
 background-color: #161b22;
}
QTabBar::tab {
 background-color: #0d1117;
 color: #8b949e;
 padding: 8px 20px;
 border: 1px solid #21262d;
 border-bottom: none;
 border-top-left-radius: 6px;
 border-top-right-radius: 6px;
 margin-right: 2px;
}
QTabBar::tab:selected {
 background-color: #161b22;
 color: #00d4ff;
 border-color: #30363d;
}

/* ===== CheckBox ===== */
QCheckBox {
 color: #e6edf3;
 spacing: 8px;
}
QCheckBox::indicator {
 width: 16px;
 height: 16px;
 border: 2px solid #30363d;
 border-radius: 4px;
 background-color: #0d1117;
}
QCheckBox::indicator:checked {
 background-color: #00d4ff;
 border-color: #00d4ff;
 image: none;
}
QCheckBox::indicator:hover {
 border-color: #58a6ff;
}

/* ===== Spin Box / Time Edit ===== */
QSpinBox, QTimeEdit {
 background-color: #161b22;
 border: 1px solid #30363d;
 border-radius: 8px;
 padding: 8px 12px;
 color: #e6edf3;
}
QSpinBox:focus, QTimeEdit:focus {
 border-color: #00d4ff;
}
QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {
 background-color: transparent;
 border: none;
 width: 0px;
}

/* ===== Log / TextBrowser ===== */
QTextBrowser {
 background-color: #010409;
 border: 1px solid #21262d;
 border-radius: 8px;
 color: #8b949e;
 font-family: 'Consolas', 'Courier New', monospace;
 font-size: 12px;
 padding: 8px;
}

/* ===== Splitter ===== */
QSplitter::handle {
 background-color: #21262d;
}

/* ===== Status Bar ===== */
QStatusBar {
 background-color: #010409;
 color: #484f58;
 border-top: 1px solid #21262d;
 font-size: 12px;
}

/* ===== Group Box ===== */
QGroupBox {
 border: 1px solid #21262d;
 border-radius: 8px;
 margin-top: 12px;
 padding: 12px 8px 8px 8px;
 color: #8b949e;
 font-size: 12px;
 font-weight: 600;
}
QGroupBox::title {
 subcontrol-origin: margin;
 subcontrol-position: top left;
 padding: 0 8px;
 color: #8b949e;
 left: 12px;
}

/* ===== List Widget ===== */
QListWidget {
 background-color: #161b22;
 border: 1px solid #21262d;
 border-radius: 8px;
 color: #e6edf3;
 padding: 4px;
}
QListWidget::item {
 padding: 8px 12px;
 border-radius: 6px;
}
QListWidget::item:selected {
 background-color: #1f2937;
 color: #00d4ff;
}
QListWidget::item:hover {
 background-color: #21262d;
}

/* ===== Content Header ===== */
#content_header {
 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
  stop:0 #111827, stop:0.7 #0f172a, stop:1 #161b22);
 border-bottom: 1px solid #21262d;
 min-height: 68px;
 max-height: 68px;
}

#header_title {
 color: #e6edf3;
 font-size: 20px;
 font-weight: 700;
 background: transparent;
 border: none;
 letter-spacing: 0.3px;
}

#header_sub {
 color: #8b949e;
 font-size: 12px;
 background: transparent;
 border: none;
}

#header_badge {
 color: #00d4ff;
 background-color: rgba(0, 212, 255, 0);
 border: 1px solid #30363d;
 border-radius: 12px;
 padding: 4px 14px;
 font-size: 11px;
 font-weight: 600;
 letter-spacing: 0.5px;
}

"""
