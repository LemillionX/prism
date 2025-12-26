from __future__ import annotations

import os

from qtpy.QtCore import QObject
from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from sbtw.core.log import logger
from sbtw.core.manager import ProjectManager
from sbtw.core.project import EntityType
from sbtw.ui.assets import AssetsView
from sbtw.ui.browser import Browser
from sbtw.ui.files import FilesView
from sbtw.ui.header import Header
from sbtw.ui.tasks import TasksView


class MainWindow(QMainWindow):
    def __init__(self, manager: ProjectManager | None = None):
        super().__init__()
        # ------------- UI  Settings -------------
        self.setWindowTitle("SBTW")
        self.setMinimumSize(800, 500)
        self.resize(1200, 500)

        # ------------- Variables -------------
        self.manager = manager or ProjectManager()

        # ------------- Layout -------------
        widget = QWidget(self)
        self.setCentralWidget(widget)

        main_layout = QVBoxLayout(widget)

        # ------------- Header -------------
        header = Header(
            name="Larsene", projects=self.manager.get_projects(), parent=self
        )
        main_layout.addWidget(header, stretch=1)

        # ------------- Browser -------------
        self.browser = Browser(data={}, parent=self)
        main_layout.addWidget(self.browser, stretch=19)

        # ------------- Signals -------------
        header.projects_grid.project_clicked.connect(self.on_project_clicked)
        header.projects_grid.project_opened.connect(self.on_project_opened)
        self.browser.row_selected.connect(self.on_row_selected)
        self.browser.row_clicked.connect(self.on_row_clicked)

    def on_project_opened(self):
        logger.info("Opening %s ...", self.manager.project.root.parent.as_posix())
        os.startfile(self.manager.project.root.parent)

    def on_project_clicked(self, project: str):
        self.manager.set_project(project)
        self.browser.assets_view.set_rows(self.manager.project.get_entities())
        self.browser.tasks_view.clear_tree()
        self.browser.files_view.clear_tree()

    def on_row_clicked(self, path: Path):
        logger.info("Opening %s ...", path.as_posix())
        os.startfile(path)

    def on_row_selected(self, sender: QObject, path: Path):
        tokens = path.parts
        if isinstance(sender, AssetsView):
            self.browser.tasks_view.set_rows(
                rows=self.manager.project.get_tasks(
                    entity=tokens[-1], entity_type=EntityType(tokens[-2])
                )
            )
            self.browser.files_view.clear_tree()

        if isinstance(sender, TasksView):
            self.browser.files_view.set_rows(
                rows=self.manager.project.get_files(
                    task=tokens[-1],
                    entity=tokens[-2],
                    entity_type=EntityType(tokens[-3]),
                )
            )

        if isinstance(sender, FilesView):
            self.browser.files_view.set_rows(
                rows=self.manager.project.get_files(
                    task=tokens[-2],
                    entity=tokens[-3],
                    entity_type=EntityType(tokens[-4]),
                )
            )


if __name__ == "__main__":
    import sys
    from pathlib import Path

    from qtpy.QtWidgets import QApplication

    from sbtw.core.constant import PROJECTS_THUMBNAIL

    app = QApplication(sys.argv)
    _data = [
        {
            "name": f"MyProject{i:02d}",
            "thumbnail": PROJECTS_THUMBNAIL,
            "data": [
                {
                    "name": f"Clementine{j:02d}",
                    "thumbnail": r"E:\Sammy\Clem.png",
                    "project": "Test",
                    "tasks": [
                        {
                            "name": task,
                            "path": Path(f"Clementine{j:02d}", task).as_posix(),
                            "files": [
                                {
                                    "name": f"Clementine{j:02d}_{task}_v{k:03d}",
                                }
                                for k in range(32, 0, -1)
                            ],
                        }
                        for task in ["Design", "Modeling", "Texture", "Rig"]
                    ],
                }
                for j in range(20)
            ],
        }
        for i in range(10)
    ]
    ui = MainWindow()
    ui.show()

    sys.exit(app.exec())
