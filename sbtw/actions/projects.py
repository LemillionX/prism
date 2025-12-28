from typing import Any

from qtpy.QtWidgets import QMessageBox

from sbtw.actions.base import ActionBase
from sbtw.core.log import NAME
from sbtw.core.manager import ProjectManager


class RemoveProject(ActionBase):
    @staticmethod
    def name() -> str:
        return "Remove project"

    def _execute(self, **kwargs: Any) -> None:
        # -------------- Get args --------------
        parent = kwargs.get("parent")
        project = kwargs.get("project")

        # -------------- Pop up --------------
        reply = QMessageBox.question(
            parent,
            self.name(),
            f"Are you sure you want to remove the project:\n\n{project} ? \n \n"
            f"NB: This will NOT delete files on your disk, it will simply remove the project from {NAME}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        # -------------- Remove on confirmation --------------
        if reply == QMessageBox.Yes:
            manager = ProjectManager()
            manager.remove_project(project)

    def post_run(self, **kwargs: Any) -> None:
        if view := kwargs.get("view"):
            view.removed.emit()
