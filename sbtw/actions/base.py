import os
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any

from sbtw.core.log import logger
from sbtw.ui.view import View


class ActionBase(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    def pre_run(self, **kwargs: Any):  # noqa: ARG002
        logger.debug("%s has no pre-run", self)

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and isinstance(view, View):
            view.row_selected.emit(kwargs)

    @abstractmethod
    def _execute(self, **kwargs: Any) -> None:
        pass

    @classmethod
    def execute(cls, **kwargs: Any) -> None:
        self = cls()
        logger.info("Executing '%s' action", cls.name())
        failed = None

        try:
            self.pre_run(**kwargs)
        except Exception:
            logger.exception("%s: pre-run has failed", cls.name())
            raise

        try:
            self._execute(**kwargs)
        except Exception as e:  # noqa: BLE001
            logger.exception("%s: execution has failed", cls.name())
            failed = e
        finally:
            try:
                self.post_run(**kwargs)
            except Exception:
                logger.exception("%s: post-run has failed", cls.name())
                raise

        if failed:
            raise failed


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
