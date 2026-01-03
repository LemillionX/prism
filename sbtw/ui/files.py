from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QTreeWidgetItem, QWidget

from sbtw.actions.utils import get_next_version
from sbtw.core.log import logger
from sbtw.core.manager import ProjectManager
from sbtw.core.project import Project
from sbtw.ui.view import View

if TYPE_CHECKING:
    from qtpy.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent


# Match an optional group of numeric dot-suffixes before the final extension, e.g. `.1001` in `name_v001.1001.txt`
RE_FILE = re.compile(r"^(?P<base>.+?)(?P<suffix>(?:\.\w+)+)?\.(?P<ext>[^.]+)$")


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
        element = ProjectManager().get_current_element()

        file = Path(element.get("path"), f"{element.get('entity')}_{element.get('path').stem}_v000")
        project = Project()
        for path in paths:
            # -------------------- Get conformed filename --------------------
            suffix = ""
            ext = path.suffix.lstrip(".")
            # Try to detect a trailing numeric suffix like `.1001.ext`
            if m2 := RE_FILE.match(path.name):
                suffix = m2.group("suffix") or ""
                ext = m2.group("ext")

            template = file.with_name(f"{file.name}{suffix}.{ext}")
            logger.info("Conforming %s Using template %s", path.as_posix(), template.as_posix())

            # Ensure template exists temporarily so helper functions can inspect directory
            template.touch(exist_ok=True)
            try:
                new_path = get_next_version(template)
            finally:
                template.unlink(missing_ok=True)

            # -------------------- Copying file --------------------
            logger.info("Creating %s from  %s ", new_path.as_posix(), path.as_posix())
            shutil.copy2(path, new_path)

            # -------------------- Set metadata --------------------
            project.set_file_metadata(new_path, author=element.get("username"))

        if paths:
            self.row_selected.emit({"path": element.get("path")})


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
