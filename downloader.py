import os
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import settings


class DownloadWorker(QThread):
    """Worker thread để download video từ URL list."""
    progress = pyqtSignal(int, str)   # (row_index, status_text)
    log = pyqtSignal(str)
    row_progress = pyqtSignal(int, int)  # (row_index, percent)
    finished = pyqtSignal(int, int)   # (success_count, error_count)

    def __init__(self, tasks: list, output_dir: str, options: dict = None):
        """
        tasks: list of {'url': str, 'row': int}
        options: dict with keys: quality, no_watermark, ytdlp_path, proxy, cookies_tiktok, cookies_instagram
        """
        super().__init__()
        self.tasks = tasks
        self.output_dir = output_dir
        self.options = options or {}
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        s = settings.load_settings()
        ytdlp = self.options.get("ytdlp_path") or s.get("ytdlp_path", "yt-dlp")
        quality = self.options.get("quality") or s.get("download_quality", "best")
        no_watermark = self.options.get("no_watermark", s.get("no_watermark_tiktok", True))
        proxy = self.options.get("proxy") or s.get("proxy", "")

        success = 0
        errors = 0

        for task in self.tasks:
            if self._stop:
                break

            url = task["url"].strip()
            row = task["row"]

            if not url:
                continue

            self.progress.emit(row, "Dang tai...")
            self.log.emit(f"[Download] Bat dau tai: {url}")

            # Detect platform
            platform = self._detect_platform(url)

            # Build command
            cmd = self._build_command(url, platform, ytdlp, quality, no_watermark, proxy)

            try:
                result = subprocess.run(
                    cmd, shell=True,
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    success += 1
                    settings.increment("stat_downloaded")
                    self.progress.emit(row, "Xong")
                    self.row_progress.emit(row, 100)
                    self.log.emit(f"[OK] Tai thanh cong: {url}")
                else:
                    errors += 1
                    settings.increment("stat_errors")
                    self.progress.emit(row, "Loi")
                    self.log.emit(f"[ERR] Loi tai {url}:\n{result.stderr[:300]}")
            except Exception as e:
                errors += 1
                self.progress.emit(row, "Loi")
                self.log.emit(f"[ERR] Exception: {e}")

        self.finished.emit(success, errors)

    def _detect_platform(self, url: str) -> str:
        url_lower = url.lower()
        if "tiktok.com" in url_lower or "vm.tiktok" in url_lower:
            return "tiktok"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "instagram.com" in url_lower:
            return "instagram"
        elif "facebook.com" in url_lower or "fb.watch" in url_lower:
            return "facebook"
        return "auto"

    def _build_command(self, url, platform, ytdlp, quality, no_watermark, proxy):
        output_dir = self.output_dir.replace("\\", "/")
        output_template = f'"{output_dir}/%(title).80s.%(ext)s"'

        format_str = ""
        if quality == "best":
            format_str = "-f bestvideo+bestaudio/best"
        elif quality == "1080p":
            format_str = "-f bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality == "720p":
            format_str = "-f bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality == "480p":
            format_str = "-f bestvideo[height<=480]+bestaudio/best[height<=480]"
        else:
            format_str = "-f bestvideo+bestaudio/best"

        extra = ""
        if platform == "tiktok" and no_watermark:
            # TikTok no watermark via different post URL pattern
            url_nw = url.replace("@", "").replace("www.tiktok.com", "tikwm.com")
            extra = "--add-header 'referer:https://www.tiktok.com/'"

        if proxy:
            extra += f" --proxy {proxy}"

        cmd = (
            f'{ytdlp} {format_str} '
            f'--merge-output-format mp4 '
            f'--no-playlist '
            f'--embed-thumbnail --embed-metadata '
            f'-o {output_template} '
            f'{extra} '
            f'"{url}"'
        )
        return cmd
