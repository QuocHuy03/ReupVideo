import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "ffmpeg_path": "ffmpeg",
    "ytdlp_path": "yt-dlp",
    "output_folder": "",
    "input_folder": "",
    "scripts_folder": "scripts",
    "download_quality": "best",
    "no_watermark_tiktok": True,
    "auto_reup_after_download": False,
    "output_naming": "{name}_reup",
    "scheduler_enabled": False,
    "scheduler_hour": 6,
    "scheduler_minute": 0,
    "scheduler_action": "download_and_process",
    "theme": "dark",
    "max_workers": 2,
    "stat_downloaded": 0,
    "stat_processed": 0,
    "stat_errors": 0,
    "cookies_instagram": "",
    "cookies_tiktok": "",
    "proxy": "",
    "last_urls": [],
    "recent_logs": []
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge with defaults for any missing keys
            merged = {**DEFAULT_SETTINGS, **data}
            return merged
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Settings] Lỗi lưu settings: {e}")


def get(key: str, default=None):
    s = load_settings()
    return s.get(key, default)


def set_value(key: str, value):
    s = load_settings()
    s[key] = value
    save_settings(s)


def increment(key: str, by: int = 1):
    s = load_settings()
    s[key] = s.get(key, 0) + by
    save_settings(s)
