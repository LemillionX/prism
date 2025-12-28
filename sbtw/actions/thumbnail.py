from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from qtpy.QtCore import QDir
from qtpy.QtWidgets import QFileDialog

from sbtw.actions.base import ActionBase
from sbtw.core.project import Project


class AddThumbnail(ActionBase):
    @staticmethod
    def name() -> str:
        return "Add Thumbnail"

    def get_thumbnail(self) -> Path | None:
        return QFileDialog.getOpenFileName(
            None,
            "Select Image to use as thumbnail",
            QDir.rootPath(),
            "Images (*.png *.xpm *.jpg)",
        )[0]

    def _execute(self, **kwargs: Any) -> None:
        path = Path(kwargs.get("path"))
        project = Project(path=path)
        dest = project.get_thumbnail_path(path)
        if src := self.get_thumbnail():
            # Copy thumbnail for project's element
            shutil.copy2(src, dest)

        # For project itself, need to update the config file
        if dest.parent.stem == ".project":
            project.save(thumbnail=dest.as_posix())

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and hasattr(view, "updated"):
            path = Path(kwargs.get("path"))
            if path.is_dir():
                path = path.parent.parent
            view.updated.emit(view, path)


class CaptureThumbnail(AddThumbnail):
    @staticmethod
    def name() -> str:
        return "CaptureThumbnail"
