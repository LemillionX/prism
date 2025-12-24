import logging
import tempfile
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

NAME = "SBTW"
# --------------- Log Folder ---------------
log_dir = Path(tempfile.gettempdir()) / f"{NAME}_logs"
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"{NAME}_{timestamp}.log"

# --------------- Logger Configuration ---------------
logger = logging.getLogger(NAME)
logger.setLevel(logging.INFO)

# ------- Handler (max 10MB, keep 5 files) -------
rotating_handler = RotatingFileHandler(
    log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)

# ------- Format -------
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
rotating_handler.setFormatter(formatter)

# ------- Console Handler -------
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(rotating_handler)
logger.addHandler(console_handler)
logger.propagate = False
