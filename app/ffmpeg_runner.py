import subprocess
import time
import sys
from typing import Tuple


def run_ffmpeg(command: str) -> Tuple[bool, float, str]:
    """Run an ffmpeg command, returning (ok, duration_seconds, error_message)."""
    start = time.time()
    creationflags = 0
    if sys.platform.startswith("win"):
        # CREATE_NO_WINDOW
        creationflags = 0x08000000
    try:
        subprocess.run(command, shell=True, check=True, creationflags=creationflags)
        return True, time.time() - start, ""
    except subprocess.CalledProcessError as exc:
        return False, 0.0, str(exc)

