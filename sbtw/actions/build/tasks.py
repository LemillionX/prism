import json
from pathlib import Path
from typing import Any

from qtpy.QtWidgets import QInputDialog

from sbtw.actions.base import ActionBase, BuildBase, MenuBase
from sbtw.core.constant import Status
from sbtw.core.log import logger
from sbtw.ui.view import View


class AddTask(ActionBase):
    @staticmethod
    def name() -> str:
        return "Add Task"

    def _execute(self, **kwargs: Any) -> None:
        if path := kwargs.get("path"):
            task_name, ok = QInputDialog.getText(None, "Task", "Enter Task name:")
            task_name = task_name.title().replace("_", " ").replace(" ", "")
            if ok:
                task: Path = path / task_name / ".status"
                task.parent.mkdir(exist_ok=True, parents=True)
                task.touch(exist_ok=True)
                with task.open(mode="w", encoding="utf8") as f:
                    json.dump({"name": task_name, "status": Status.WTG.name}, f, indent=4)
                kwargs["path"] = task.parent

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and isinstance(view, View):
            view.updated.emit(view, kwargs.get("path"))


class BuildScene(BuildBase):
    def _execute(self, **kwargs: Any) -> None:
        if path := Path(kwargs.get("path")):
            task = path.stem
            entity = path.parent.stem
            version = 1

            logger.info("Creating file %s", f"{entity}_{task}_v{version:03d}")


class EditStatus(MenuBase):
    @staticmethod
    def name() -> str:
        return "Edit Status"

    def _execute(self, **kwargs: Any) -> None:
        return super()._execute(**kwargs)


class SetStatus(ActionBase):
    def __init__(self, status: Status):
        super().__init__()
        self.status = status

    def name(self):
        return self.status.name

    def _execute(self, **kwargs: Any) -> None:
        if path := Path(kwargs.get("path")):
            task = path / ".status"
            with task.open(mode="r", encoding="utf8") as f:
                data = json.load(f)
            data["status"] = self.status.name
            with task.open(mode="w", encoding="utf8") as f:
                json.dump(data, f, indent=4)

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and isinstance(view, View):
            view.updated.emit(view, kwargs.get("path", Path()).parent)
