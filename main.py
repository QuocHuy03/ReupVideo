import os
from PyQt5.QtWidgets import QApplication, QMessageBox


def check_ffmpeg_installed() -> bool:
    ffmpeg_exe = "ffmpeg.exe"  # Kiểm tra FFmpeg trong thư mục hiện tại
    return os.path.isfile(ffmpeg_exe)


if __name__ == '__main__':
    import sys
    from app.main_window import VideoReupTool

    app = QApplication(sys.argv)

    if not check_ffmpeg_installed():
        QMessageBox.critical(None, "Lỗi FFmpeg", "FFmpeg chưa được cài đặt. Vui lòng đặt ffmpeg.exe cạnh chương trình hoặc cài đặt FFmpeg.")
        sys.exit(1)

    window = VideoReupTool()
    window.show()
    sys.exit(app.exec_())
