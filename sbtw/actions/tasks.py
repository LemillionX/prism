from pathlib import Path
from typing import Any

from qtpy.QtWidgets import QInputDialog

from sbtw.actions.base import ActionBase, AddEntityBase, BuildBase, MenuBase
from sbtw.actions.utils import prettier
from sbtw.core.constant import Status
from sbtw.core.log import logger
from sbtw.core.project import Project


class AddTask(AddEntityBase):
    def __init__(self):
        super().__init__(entity_type="Task")

    def get_entity_name(self):
        # Hardcoded choices presented in an editable dropdown; user can also type a new name.
        choices = [
            "",
            "Reference",
            "Design",
            "Modeling",
            "Rig",
            "Layout",
            "Animation",
            "Lighting",
            "Compo",
        ]

        name, ok = QInputDialog.getItem(
            None, "Add Task", "Select or enter Task name:", choices, current=0, editable=True
        )
        name = prettier(name)
        if ok and name:
            return name
        return None


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
            project = Project()
            project.set_task_metadata(path, status=self.status.name)

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and hasattr(view, "updated"):
            view.updated.emit(view, kwargs.get("path", Path()).parent)
            view.updated.emit(view, kwargs.get("path", Path()).parent)
