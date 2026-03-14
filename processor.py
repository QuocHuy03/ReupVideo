import os
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import settings


class ProcessWorker(QThread):
    """Worker thread chạy FFmpeg commands trên batch video files."""
    progress = pyqtSignal(int, int)       # (current, total)
    file_status = pyqtSignal(int, str)    # (row_index, status)
    log = pyqtSignal(str)
    finished = pyqtSignal(int, int)       # (success, errors)

    def __init__(self, input_files: list, output_dir: str, command_template: str, naming_pattern: str = "{name}_reup"):
        """
        input_files: list of {'path': str, 'row': int}
        command_template: FFmpeg command với {input} và {output} placeholder
        naming_pattern: {name}_reup => output file name
        """
        super().__init__()
        self.input_files = input_files
        self.output_dir = output_dir
        self.command_template = command_template
        self.naming_pattern = naming_pattern
        self._stop = False
        self._skip_current = False

    def stop(self):
        self._stop = True

    def skip(self):
        self._skip_current = True

    def run(self):
        total = len(self.input_files)
        success = 0
        errors = 0

        for idx, task in enumerate(self.input_files):
            if self._stop:
                self.log.emit("[STOP] Da dung xu ly.")
                break

            self._skip_current = False
            input_path = task["path"]
            row = task["row"]
            filename = os.path.basename(input_path)
            name_no_ext = os.path.splitext(filename)[0]

            output_name = self.naming_pattern.replace("{name}", name_no_ext)
            # Ensure output_name ends with .mp4 if command has {output}.mp4
            if not output_name.endswith(".mp4"):
                output_name += ".mp4"

            output_path = os.path.join(self.output_dir, output_name)

            # Handle duplicate output
            counter = 1
            base_out = output_path.replace(".mp4", "")
            while os.path.exists(output_path):
                output_path = f"{base_out}_{counter}.mp4"
                counter += 1

            cmd = self.command_template.strip()
            cmd = cmd.replace("{input}", f'"{input_path}"')
            cmd = cmd.replace("{output}", f'"{output_path.replace(".mp4", "")}"')

            self.file_status.emit(row, "Dang xu ly...")
            self.log.emit(f"[Process] Xu ly: {filename}")
            self.log.emit(f"   -> {cmd[:120]}{'...' if len(cmd)>120 else ''}")

            try:
                proc = subprocess.Popen(
                    cmd, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                out, err = proc.communicate()

                if self._skip_current:
                    proc.kill()
                    self.file_status.emit(row, "⏭ Bỏ qua")
                    self.log.emit(f"⏭ Bỏ qua: {filename}")
                    continue

                if proc.returncode == 0:
                    success += 1
                    settings.increment("stat_processed")
                    self.file_status.emit(row, "Xong")
                    self.log.emit(f"[OK] Xong: {filename} -> {os.path.basename(output_path)}")
                else:
                    errors += 1
                    settings.increment("stat_errors")
                    self.file_status.emit(row, "Loi")
                    err_short = (err or "").strip()[-200:] if err else ""
                    self.log.emit(f"[ERR] Loi xu ly {filename}:\n   {err_short}")

            except Exception as e:
                errors += 1
                self.file_status.emit(row, "Loi")
                self.log.emit(f"[ERR] Exception [{filename}]: {e}")

            self.progress.emit(idx + 1, total)

        self.finished.emit(success, errors)


def get_scripts(scripts_folder: str = "scripts") -> list:
    """Trả về list tên file script .txt trong thư mục scripts."""
    if not os.path.exists(scripts_folder):
        os.makedirs(scripts_folder)
    files = []
    for f in sorted(os.listdir(scripts_folder)):
        if f.endswith(".txt"):
            files.append(f)
    return files


def read_script(name: str, scripts_folder: str = "scripts") -> str:
    path = os.path.join(scripts_folder, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def save_script(name: str, content: str, scripts_folder: str = "scripts"):
    if not os.path.exists(scripts_folder):
        os.makedirs(scripts_folder)
    path = os.path.join(scripts_folder, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def delete_script(name: str, scripts_folder: str = "scripts"):
    path = os.path.join(scripts_folder, name)
    if os.path.exists(path):
        os.remove(path)


def get_video_files(folder: str) -> list:
    """Trả về list đường dẫn tuyệt đối của video files trong folder."""
    exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.ts', '.wmv')
    files = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith(exts):
                files.append(os.path.join(folder, f))
    return sorted(files)
