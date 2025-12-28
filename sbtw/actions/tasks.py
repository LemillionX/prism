import json
from pathlib import Path
from typing import Any

from sbtw.actions.base import ActionBase, AddEntityBase, BuildBase, MenuBase
from sbtw.core.constant import METADATA, Status
from sbtw.core.log import logger
from sbtw.core.project import get_meta_path
from sbtw.ui.view import View


class AddTask(AddEntityBase):
    def __init__(self):
        super().__init__(entity_type="Task")


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
            meta = get_meta_path(path)
            meta.mkdir(parents=True, exist_ok=True)
            task = meta / METADATA
            with task.open(mode="r", encoding="utf8") as f:
                data = json.load(f)
            data["status"] = self.status.name
            with task.open(mode="w", encoding="utf8") as f:
                json.dump(data, f, indent=4)

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and isinstance(view, View):
            view.updated.emit(view, kwargs.get("path", Path()).parent)
