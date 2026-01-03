import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from sbtw.core.constant import APPDATA

NAME = "SBTW"
# --------------- Log Folder ---------------
LOG_DIR = APPDATA / "logs"
LOG_DIR.mkdir(exist_ok=True)
timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"{NAME}_{timestamp}.log"

# --------------- Logger Configuration ---------------
logger = logging.getLogger(NAME)
logger.setLevel(logging.INFO)

# ------- Handler (max 10MB, keep 5 files) -------
rotating_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")

# ------- Format -------
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
rotating_handler.setFormatter(formatter)

# ------- Console Handler -------
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers only if they are not already present to avoid duplicate logging
if not logger.handlers:
    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)
else:
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        logger.addHandler(rotating_handler)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)

logger.propagate = False
