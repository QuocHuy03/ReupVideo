import os
import subprocess
import urllib.request
import zipfile
import shutil
import socket
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QFileDialog, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet

def check_internet(timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        host = socket.gethostbyname("one.one.one.one")
        s = socket.create_connection((host, 80), timeout)
        s.close()
        return True
    except:
        return False

def ensure_ffmpeg_installed(log_func=print):
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")

    if os.path.isfile(ffmpeg_exe):
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
        log_func("✅ FFmpeg đã có sẵn.")
        return True

    log_func("⏳ Đang tải và cài FFmpeg...")

    try:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        local_zip = "ffmpeg.zip"

        urllib.request.urlretrieve(url, local_zip)

        with zipfile.ZipFile(local_zip, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")

        for root, dirs, files in os.walk("ffmpeg_temp"):
            for file in files:
                if file == "ffmpeg.exe":
                    os.makedirs(ffmpeg_dir, exist_ok=True)
                    shutil.copy(os.path.join(root, file), ffmpeg_exe)
                    break

        shutil.rmtree("ffmpeg_temp")
        os.remove(local_zip)

        os.environ["PATH"] += os.pathsep + ffmpeg_dir
        log_func("✅ Cài đặt FFmpeg hoàn tất.")
        return True
    except Exception as e:
        log_func(f"❌ Lỗi khi tải FFmpeg: {e}")
        return False

class VideoReupTool(QWidget):
    def __init__(self):
        super().__init__()
        apply_stylesheet(self, theme='light_blue.xml')
        self.setWindowTitle("FFmpeg Reup Video Tool")
        self.resize(900, 750)

        self.build_ui()

        if not check_internet():
            QMessageBox.critical(self, "Không có mạng", "Không thể kết nối Internet để tải FFmpeg.")
            exit(1)

        if not ensure_ffmpeg_installed():
            QMessageBox.critical(self, "Lỗi FFmpeg", "Không thể cài đặt FFmpeg.")
            exit(1)

        self.connect_events()
        self.load_script_list()

    def build_ui(self):
        self.input_folder = QLineEdit()
        self.output_folder = QLineEdit()
        self.script_combo = QComboBox()
        self.command_preview = QTextEdit()

        self.browse_input_btn = QPushButton("📁 Chọn thư mục video")
        self.browse_output_btn = QPushButton("📁 Chọn thư mục xuất")
        self.load_script_btn = QPushButton("📜 Load mã FFmpeg")
        self.run_btn = QPushButton("⚙️ Chạy xử lý")

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["TÊN VIDEO", "THỜI GIAN (S)", "TRẠNG THÁI"])
        self.result_table.horizontalHeader().setStretchLastSection(False)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)         # TÊN VIDEO kéo dãn linh hoạt
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # THỜI GIAN tự co theo nội dung
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # TRẠNG THÁI tự co theo nội dung

        layout = QVBoxLayout()
        layout.setSpacing(10)

        for w in [[self.input_folder, self.browse_input_btn], [self.output_folder, self.browse_output_btn], [self.script_combo, self.load_script_btn]]:
            hlayout = QHBoxLayout()
            for item in w: hlayout.addWidget(item)
            layout.addLayout(hlayout)

        layout.addWidget(QLabel("📄 Preview mã FFmpeg:"))
        layout.addWidget(self.command_preview)
        layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("📋 Bảng kết quả xử lý:"))
        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def connect_events(self):
        self.browse_input_btn.clicked.connect(self.select_input_folder)
        self.browse_output_btn.clicked.connect(self.select_output_folder)
        self.load_script_btn.clicked.connect(self.load_ffmpeg_script)
        self.run_btn.clicked.connect(self.process_videos)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa video")
        if folder:
            self.input_folder.setText(folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất video")
        if folder:
            self.output_folder.setText(folder)

    def load_script_list(self):
        os.makedirs("scripts", exist_ok=True)
        self.script_combo.clear()
        self.script_combo.addItems([f for f in os.listdir("scripts") if f.endswith(".txt")])

    def load_ffmpeg_script(self):
        selected = self.script_combo.currentText()
        if selected:
            with open(os.path.join("scripts", selected), "r", encoding="utf-8") as f:
                self.command_preview.setPlainText(f.read())

    def process_videos(self):
        self.run_btn.setEnabled(False)
        self.result_table.setRowCount(0)

        input_dir = self.input_folder.text()
        output_dir = self.output_folder.text()
        command_template = self.command_preview.toPlainText().strip()

        if not input_dir or not output_dir or not command_template:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin.")
            self.run_btn.setEnabled(True)
            return

        files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]

        for file in files:
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, os.path.splitext(file)[0] + "_reup.mp4")

            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            self.result_table.setItem(row, 0, QTableWidgetItem(file))
            self.result_table.setItem(row, 1, QTableWidgetItem("..."))
            self.result_table.setItem(row, 2, QTableWidgetItem("🔧 Đang xử lý"))

            command = command_template.replace("{input}", f'"{input_path}"').replace("{output}", f'"{output_path}"')
            try:
                start_time = time.time()
                subprocess.run(command, shell=True, check=True)
                duration = time.time() - start_time
                self.result_table.item(row, 1).setText(f"{duration:.2f}")
                self.result_table.item(row, 2).setText("✅ Hoàn tất")
            except subprocess.CalledProcessError:
                self.result_table.item(row, 1).setText("0.00")
                self.result_table.item(row, 2).setText("❌ Lỗi xử lý")

        self.run_btn.setEnabled(True)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = VideoReupTool()
    window.show()
    sys.exit(app.exec_())
