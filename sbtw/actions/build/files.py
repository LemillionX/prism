import shutil
from pathlib import Path

from sbtw.actions.base import ActionBase
from sbtw.actions.utils import get_next_version
from sbtw.core.log import logger


class Increment(ActionBase):
    @staticmethod
    def name() -> str:
        return "Increment"

    def _execute(self, **kwargs):
        path = Path(kwargs.get("path"))
        file = get_next_version(path)
        logger.info("Creating file %s", file.as_posix())
        shutil.copy2(path, file)
