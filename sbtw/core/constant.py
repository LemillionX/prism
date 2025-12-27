import os
from enum import Enum
from pathlib import Path

# -------------------- Medias --------------------
MEDIAS_FOLDER = Path(__file__).parent.parent.resolve() / "medias"
DEFAULT_THUMBNAIL = MEDIAS_FOLDER / "default-thumbnail.png"
USER_THUMBNAIL = MEDIAS_FOLDER / "user-thumbnail.png"
PROJECTS_THUMBNAIL = MEDIAS_FOLDER / "project-thumbnail.png"
REFRESH_ICON = MEDIAS_FOLDER / "refresh-icon.png"
PLUS_ICON = MEDIAS_FOLDER / "plus-icon.png"
BROWSER_EXPLORER_ICON = MEDIAS_FOLDER / "browse-explorer-icon.png"

# -------------------- Folders --------------------
APPDATA = Path(os.getenv("APPDATA"), "sbtw")
APPDATA.mkdir(parents=True, exist_ok=True)
CONFIG = APPDATA / "config.json"
CONFIG.touch(exist_ok=True)


# -------------------- Status --------------------
class Status(str, Enum):
    WTG = "Waiting to Start"
    HLD = "On Hold"
    WIP = "Work In Progress"
    OK = "Approved"
