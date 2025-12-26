import shutil
from pathlib import Path

from sbtw.actions.base import ActionBase
from sbtw.core.log import logger


class Increment(ActionBase):
    @staticmethod
    def name() -> str:
        return "Increment"

    def _execute(self, **kwargs):
        path = Path(kwargs.get("path"))
        task = path.parent.stem
        entity = path.parent.parent.stem
        version = int(path.stem.rsplit("_", 1)[-1][1:]) + 1
        file = (path.parent / f"{entity}_{task}_v{version:03d}").with_suffix(
            path.suffix
        )

        logger.info("Creating file %s", file.as_posix())
        shutil.copy2(path, file)
