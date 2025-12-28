import json
import os
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any

from qtpy.QtWidgets import QInputDialog

from sbtw.core.constant import EntityType, Status
from sbtw.core.log import logger


class ActionBase(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    def pre_run(self, **kwargs: Any):  # noqa: ARG002
        logger.debug("%s has no pre-run", self)

    def post_run(self, **kwargs: Any):
        if view := (kwargs.get("view")):
            view.row_selected.emit(kwargs)

    @abstractmethod
    def _execute(self, **kwargs: Any) -> None:
        pass

    def execute(self, **kwargs: Any) -> None:
        logger.info("Executing '%s' action", self.name())
        failed = None

        try:
            self.pre_run(**kwargs)
        except Exception:
            logger.exception("%s: pre-run has failed", self.name())
            raise

        try:
            self._execute(**kwargs)
        except Exception as e:  # noqa: BLE001
            logger.exception("%s: execution has failed", self.name())
            failed = e
        finally:
            try:
                self.post_run(**kwargs)
            except Exception:
                logger.exception("%s: post-run has failed", self.name())
                raise

        if failed:
            raise failed


class MenuBase(ActionBase):
    def __init__(self, actions: list[ActionBase]):
        super().__init__()
        self.actions = actions

    @staticmethod
    def name() -> str:
        return "Menu"


class AddEntityBase(ActionBase):
    def __init__(self, entity_type: str):
        super().__init__()
        self.entity_type = entity_type

    def name(self) -> str:
        return f"Add {self.entity_type}"

    def _execute(self, **kwargs: Any) -> None:
        if path := kwargs.get("path"):
            entity_name, ok = QInputDialog.getText(None, self.entity_type, f"Enter {self.entity_type} name:")
            entity_name = entity_name.title().replace("_", " ").replace(" ", "")
            if ok:
                try:
                    # For Entities
                    entity: Path = path / EntityType[self.entity_type].value / entity_name / ".status"
                except KeyError:
                    # For Tasks and others
                    entity: Path = path / entity_name / ".status"

                # Add status and create folder
                entity.parent.mkdir(exist_ok=True, parents=True)
                entity.touch(exist_ok=True)
                with entity.open(mode="w", encoding="utf8") as f:
                    json.dump({"name": entity_name, "status": Status.WTG.name}, f, indent=4)

    def post_run(self, **kwargs: Any):
        if view := (kwargs.get("view")):
            view.updated.emit(view, kwargs.get("path"))


class BuildBase(ActionBase):
    @staticmethod
    def name() -> str:
        return "Build"


class OpenInExplorer(ActionBase):
    @staticmethod
    def name() -> str:
        return "Open In Explorer"

    def _execute(self, **kwargs: Any) -> None:
        path = Path(kwargs.get("path"))
        os.startfile(path.parent)
