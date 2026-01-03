from __future__ import annotations

import ctypes
import os
import sys
from enum import Enum
from pathlib import Path

# -------------------- Medias --------------------
BASE_FOLDER = Path(__file__).parent.parent.resolve()
MEDIAS_FOLDER = BASE_FOLDER / "medias"
APP_ICON = MEDIAS_FOLDER / "sbtw-icon.ico"
DEFAULT_THUMBNAIL = MEDIAS_FOLDER / "default-thumbnail.png"
USER_THUMBNAIL = MEDIAS_FOLDER / "user-thumbnail.png"
PROJECTS_THUMBNAIL = MEDIAS_FOLDER / "project-thumbnail.png"
REFRESH_ICON = MEDIAS_FOLDER / "refresh-icon.png"
PLUS_ICON = MEDIAS_FOLDER / "plus-icon.png"
BROWSER_EXPLORER_ICON = MEDIAS_FOLDER / "browse-explorer-icon.png"
SPLASH_SCREEN = MEDIAS_FOLDER / "splash-screen.png"
LOG_THUMBNAIL = MEDIAS_FOLDER / "log-thumbnail.png"
STYLESHEET = BASE_FOLDER / "style" / "dark.qss"

# -------------------- Folders --------------------
APPDATA = Path(os.getenv("APPDATA"), "sbtw")
APPDATA.mkdir(parents=True, exist_ok=True)
CONFIG = APPDATA / "config.json"
CONFIG.touch(exist_ok=True)

# -------------------- Variables --------------------
METADATA = ".sbtw"


# -------------------- Entities --------------------
class EntityType(str, Enum):
    Asset = "Assets"
    Shot = "Shots"


# -------------------- Status --------------------
class Status(str, Enum):
    WTG = "Waiting to Start"
    RTK = "Retake"
    HLD = "On Hold"
    WIP = "Work In Progress"
    OK = "Approved"


# -------------------- Softwares --------------------
SOFTWARES = {
    ".ma": [MEDIAS_FOLDER / "maya-icon.png"],
    ".mb": [MEDIAS_FOLDER / "maya-icon.png"],
    ".psd": [MEDIAS_FOLDER / "photoshop-icon.png", MEDIAS_FOLDER / "clip-studio-icon.png"],
    ".blend": [MEDIAS_FOLDER / "blender-icon.png"],
    ".fbx": [MEDIAS_FOLDER / "fbx-icon.png"],
    ".obj": [MEDIAS_FOLDER / "obj-icon.png"],
    ".png": [MEDIAS_FOLDER / "image-icon.png"],
    ".jpg": [MEDIAS_FOLDER / "image-icon.png"],
    ".jpeg": [MEDIAS_FOLDER / "image-icon.png"],
    ".mp4": [MEDIAS_FOLDER / "video-icon.png"],
    ".mov": [MEDIAS_FOLDER / "video-icon.png"],
    ".mp3": [MEDIAS_FOLDER / "audio-icon.png"],
    ".wav": [MEDIAS_FOLDER / "audio-icon.png"],
    ".txt": [MEDIAS_FOLDER / "file-icon.png"],
}


# -------------------- UI --------------------
def enable_windows_dark_titlebar(hwnd: int):
    if sys.platform != "win32":
        return

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10 1903+  # noqa: N806
    value = ctypes.c_int(1)

    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(value),
        ctypes.sizeof(value),
    )
