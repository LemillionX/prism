import shutil
from pathlib import Path
from typing import Any

from sbtw.actions.base import ActionBase
from sbtw.actions.utils import get_next_version
from sbtw.core.constant import Status
from sbtw.core.log import logger
from sbtw.core.project import Project


class Increment(ActionBase):
    @staticmethod
    def name() -> str:
        return "Increment"

    def _execute(self, **kwargs: Any) -> None:
        path = Path(kwargs.get("path"))
        if file := get_next_version(path):
            # -------------------- Increment file --------------------
            logger.info("Creating file %s", file.as_posix())
            shutil.copy2(path, file)

            # -------------------- Set Metadata --------------------
            project = Project()
            metadata = project.get_file_metadata(path)
            project.set_file_metadata(file, **metadata)
            project.set_file_metadata(file, status=Status.WTG.name)
        else:
            logger.error("Couldn't increment %s", path.as_posix())
