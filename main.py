import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QFileDialog, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QTextBrowser,
    QCheckBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer

class VideoReupTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFmpeg Reup Video Tool - Full Auto Advanced")
        self.resize(900, 750)

        # Widgets
        self.input_folder = QLineEdit()
        self.output_folder = QLineEdit()
        self.download_url_list = QTextEdit()
        self.script_combo = QComboBox()
        self.command_preview = QTextEdit()
        self.log_browser = QTextBrowser()
        self.reup_after_download = QCheckBox("Reup sau khi tải")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        browse_input_btn = QPushButton("\U0001F4C1 Chọn thư mục video")
        browse_output_btn = QPushButton("\U0001F4C1 Chọn thư mục xuất")
        load_script_btn = QPushButton("\U0001F4DC Load mã FFmpeg")
        self.run_btn = QPushButton("\u2699\ufe0f Chạy xử lý")
        download_btn = QPushButton("\u2B07\ufe0f Tải video")

        # Layouts
        layout = QVBoxLayout()

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.input_folder)
        hlayout1.addWidget(browse_input_btn)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.output_folder)
        hlayout2.addWidget(browse_output_btn)

        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.script_combo)
        hlayout3.addWidget(load_script_btn)

        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addLayout(hlayout3)
        layout.addWidget(QLabel("\U0001F4CB Dán danh sách URL TikTok (mỗi dòng 1 link):"))
        layout.addWidget(self.download_url_list)
        layout.addWidget(download_btn)
        layout.addWidget(self.reup_after_download)
        layout.addWidget(QLabel("\U0001F4C4 Preview mã FFmpeg:"))
        layout.addWidget(self.command_preview)
        layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("\U0001F4CA Log xử lý:"))
        layout.addWidget(self.log_browser)
        layout.addWidget(QLabel("\U0001F501 Tiến độ:"))
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Connections
        browse_input_btn.clicked.connect(self.select_input_folder)
        browse_output_btn.clicked.connect(self.select_output_folder)
        load_script_btn.clicked.connect(self.load_ffmpeg_script)
        self.run_btn.clicked.connect(self.start_processing_thread)
        download_btn.clicked.connect(self.start_batch_download_thread)

        self.load_script_list()

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa video")
        if folder:
            self.input_folder.setText(folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất video")
        if folder:
            self.output_folder.setText(folder)

    def load_script_list(self):
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
        self.script_combo.clear()
        for file in os.listdir("scripts"):
            if file.endswith(".txt"):
                self.script_combo.addItem(file)

    def load_ffmpeg_script(self):
        selected = self.script_combo.currentText()
        if selected:
            path = os.path.join("scripts", selected)
            with open(path, "r", encoding="utf-8") as f:
                self.command_preview.setPlainText(f.read())

    def start_processing_thread(self):
        self.run_btn.setEnabled(False)
        self.log_browser.clear()
        threading.Thread(target=self.process_videos).start()

    def start_batch_download_thread(self):
        threading.Thread(target=self.download_videos_from_list).start()

    def process_videos(self):
        input_dir = self.input_folder.text()
        output_dir = self.output_folder.text()
        command_template = self.command_preview.toPlainText().strip()

        if not input_dir or not output_dir or not command_template:
            self.show_warning("Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin.")
            self.run_btn.setEnabled(True)
            return

        files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        total = len(files)
        for i, file in enumerate(files):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, os.path.splitext(file)[0] + "_reup.mp4")
            command = command_template.replace("{input}", f'"{input_path}"').replace("{output}", f'"{output_path}"')
            try:
                subprocess.run(command, shell=True, check=True)
                self.log_to_browser(f"✅ Xử lý xong: {file}")
            except subprocess.CalledProcessError as e:
                self.log_to_browser(f"❌ Lỗi: {file}\n{e}")
            self.progress_bar.setValue(int((i + 1) / total * 100))

        self.run_btn.setEnabled(True)

    def download_videos_from_list(self):
        urls = self.download_url_list.toPlainText().strip().splitlines()
        output_dir = self.input_folder.text().strip()

        if not urls or not output_dir:
            self.show_warning("Thiếu thông tin", "Vui lòng nhập URL và chọn thư mục video.")
            return

        for url in urls:
            if url.strip():
                try:
                    cmd = f'yt-dlp --no-playlist -o "{output_dir}/%(title)s.%(ext)s" "{url.strip()}"'
                    subprocess.run(cmd, shell=True, check=True)
                    self.log_to_browser(f"✅ Đã tải: {url.strip()}")
                except subprocess.CalledProcessError as e:
                    self.log_to_browser(f"❌ Lỗi tải: {url.strip()}\n{e}")
        if self.reup_after_download.isChecked():
            self.start_processing_thread()

    def show_warning(self, title, message):
        QTimer.singleShot(0, lambda: QMessageBox.warning(self, title, message))

    def log_to_browser(self, message):
        QTimer.singleShot(0, lambda: self.log_browser.append(message))

if __name__ == '__main__':
    app = QApplication([])
    window = VideoReupTool()
    window.show()
    app.exec_()
