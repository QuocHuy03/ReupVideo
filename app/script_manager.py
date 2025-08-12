import os
import re
import shlex
from dataclasses import dataclass
from typing import Dict, List, Set, Optional


SCRIPTS_DIR = "scripts"


def ensure_scripts_dir() -> None:
    os.makedirs(SCRIPTS_DIR, exist_ok=True)


def list_script_files() -> List[str]:
    """Return available script filenames (.txt) under scripts/ sorted alphabetically."""
    ensure_scripts_dir()
    scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.lower().endswith(".txt")]
    return sorted(scripts, key=str.lower)


def read_script(filename: str) -> str:
    """Read the script content from scripts/ directory."""
    ensure_scripts_dir()
    path = os.path.join(SCRIPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")


def extract_placeholders(script_text: str) -> List[str]:
    """Find all placeholder names inside curly braces, preserving order of first appearance."""
    seen: Set[str] = set()
    ordered: List[str] = []
    for match in PLACEHOLDER_PATTERN.finditer(script_text):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def categorize_placeholder(name: str) -> str:
    """Categorize known placeholders to drive UI input type.

    Returns one of: 'file', 'number', 'text'.
    """
    lower_name = name.lower()
    file_like = {
        "audio", "music", "bgm", "logo", "watermark", "image", "img",
        "subtitle", "sub", "srt", "ass", "font", "input2"
    }
    if lower_name in file_like:
        return "file"

    numeric_like = {
        "width", "height", "fps", "crf", "bitrate", "gop", "speed_factor",
        "atempo", "contrast", "brightness", "saturation", "hue", "gamma",
        "pos_x", "pos_y", "x", "y", "fontsize", "opacity", "denoise_strength",
        "blur_strength", "mp3_quality", "angle", "start", "end", "duration"
    }
    if lower_name in numeric_like:
        return "number"

    return "text"


def default_value_for(name: str) -> str:
    lower_name = name.lower()
    defaults: Dict[str, str] = {
        "fps": "30",
        "crf": "23",
        "bitrate": "2500k",
        "speed_factor": "1.25",
        "atempo": "1.25",
        "contrast": "1.1",
        "brightness": "0.02",
        "saturation": "1.1",
        "pos_x": "10",
        "pos_y": "10",
        "fontsize": "32",
        "opacity": "0.7",
        "denoise_strength": "6",
        "blur_strength": "2:1",
        "mp3_quality": "2",
        "angle": "5",
        "start": "00:00:00",
        "end": "",
        "duration": "",
    }
    return defaults.get(lower_name, "")


@dataclass
class ParamMeta:
    name: str
    type: str = "text"  # text | number | file | choice
    label: Optional[str] = None
    default: Optional[str] = None
    choices: Optional[List[str]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    file_filter: Optional[str] = None


PARAM_LINE_RE = re.compile(r"^\s*#\s*PARAM\s+(.*)$", re.IGNORECASE)


def parse_param_meta(script_text: str) -> Dict[str, ParamMeta]:
    """Parse optional per-parameter metadata from lines starting with '# PARAM ...'.

    Syntax examples:
      # PARAM logo type=file label="Logo" filter="Images (*.png;*.jpg)"
      # PARAM fps type=number min=1 max=120 step=1 default=30
      # PARAM method type=choice choices=fast,quality default=fast label="Chế độ"
      # PARAM name=font type=file label="Font" filter="Fonts (*.ttf;*.otf)"
    """
    metas: Dict[str, ParamMeta] = {}
    for line in script_text.splitlines()[:50]:  # only scan header
        m = PARAM_LINE_RE.match(line)
        if not m:
            continue
        payload = m.group(1).strip()
        if not payload:
            continue
        try:
            parts = shlex.split(payload)
        except Exception:
            parts = payload.split()

        name: Optional[str] = None
        kwargs: Dict[str, str] = {}
        for idx, token in enumerate(parts):
            if "=" in token:
                key, val = token.split("=", 1)
                kwargs[key.strip().lower()] = val.strip()
            elif idx == 0 and name is None:
                name = token

        if name is None:
            name = kwargs.get("name")
        if not name:
            continue

        meta = ParamMeta(name=name)
        if "type" in kwargs:
            meta.type = kwargs["type"].lower()
        if "label" in kwargs:
            meta.label = kwargs["label"]
        if "default" in kwargs:
            meta.default = kwargs["default"]
        if "choices" in kwargs:
            meta.choices = [c.strip() for c in kwargs["choices"].split(",") if c.strip()]
        if "min" in kwargs:
            try:
                meta.min = float(kwargs["min"])
            except ValueError:
                pass
        if "max" in kwargs:
            try:
                meta.max = float(kwargs["max"])
            except ValueError:
                pass
        if "step" in kwargs:
            try:
                meta.step = float(kwargs["step"])
            except ValueError:
                pass
        if "filter" in kwargs:
            meta.file_filter = kwargs["filter"]

        metas[name] = meta
    return metas


