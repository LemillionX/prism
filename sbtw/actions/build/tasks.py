from pathlib import Path
from typing import Any

from qtpy.QtWidgets import QInputDialog

from sbtw.actions.base import ActionBase, BuildBase
from sbtw.core.log import logger
from sbtw.ui.view import View


class AddTask(ActionBase):
    @staticmethod
    def name() -> str:
        return "Add Task"

    def _execute(self, **kwargs: Any) -> None:
        if path := kwargs.get("path"):
            task, ok = QInputDialog.getText(None, "Task", "Enter Task name:")
            task = task.title().replace("_", " ").replace(" ", "")
            if ok:
                (path / task).mkdir(exist_ok=True, parents=True)
                kwargs["path"] = path / task

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and isinstance(view, View):
            view.updated.emit(view, kwargs.get("path"))


class BuildScene(BuildBase):
    def _execute(self, **kwargs: Any) -> None:
        path = Path(kwargs.get("path"))
        task = path.stem
        entity = path.parent.stem
        version = 1

        logger.info("Creating file %s", f"{entity}_{task}_v{version:03d}")
