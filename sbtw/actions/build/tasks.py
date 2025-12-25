from pathlib import Path

from sbtw.actions.base import BuildBase
from sbtw.core.log import logger


class BuildScene(BuildBase):
    def _execute(self, **kwargs):
        path = Path(kwargs.get("path"))
        task = path.stem
        entity = path.parent.stem
        version = 1

        logger.info("Creating file %s", f"{entity}_{task}_v{version:03d}")
