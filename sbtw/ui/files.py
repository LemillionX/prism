from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QTreeWidgetItem, QWidget

from sbtw.actions.utils import get_last_version, get_next_version
from sbtw.core.log import logger
from sbtw.core.project import Project
from sbtw.ui.view import View

if TYPE_CHECKING:
    from qtpy.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent


class FilesView(View):
    files_dropped = Signal(object)

    def __init__(
        self,
        rows: list[dict] | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(rows=rows, keys=["author", "icon", "date", "size"], actions=actions, parent=parent)
        self.setAcceptDrops(True)
        self.files_dropped.connect(self.on_files_dropped)

    def on_item_clicked(self, item: QTreeWidgetItem):
        pass

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths: list[Path] = []

        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]

        if paths:
            self.files_dropped.emit(paths)

        event.acceptProposedAction()

    def on_files_dropped(self, paths: list[Path]) -> None:
        if not self.entity:
            logger.warning("Cannot drag and drop files: you are not on a Task")
            return

        file = Path(
            self.entity.get("path"), f"{self.entity.get('path').parent.stem}_{self.entity.get('path').stem}_v000"
        )
        project = Project()
        for path in paths:
            # -------------------- Get conformed filename --------------------
            file.with_suffix(path.suffix).touch(exist_ok=True)
            last_version = get_last_version(file.with_suffix(path.suffix))
            new_path = get_next_version(last_version)
            file.with_suffix(path.suffix).unlink(missing_ok=True)

            # -------------------- Copying file --------------------
            logger.info("Creating %s from  %s ", new_path.as_posix(), path.as_posix())
            shutil.copy2(path, new_path)

            # -------------------- Set metadata --------------------
            project.set_file_metadata(new_path, author=self.entity.get("username"))

        if paths:
            self.row_selected.emit({"path": file})


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [
        {
            "name": "Clementine",
            "author": "Telltale Games",
            "status": "wtg",
            "date": "24/12/2025, 15:54",
            "size": f"{i:02d} MB",
            "thumbnail": r"E:\Sammy\Clem.png",
        }
        for i in range(10)
    ]

    view = FilesView(rows=_data)
    view.show()

    sys.exit(app.exec())

    sys.exit(app.exec())
    sys.exit(app.exec())
