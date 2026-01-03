from __future__ import annotations

import os
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from sbtw._version import __version__
from sbtw.core.constant import EntityType
from sbtw.core.log import NAME, logger
from sbtw.core.manager import ProjectManager
from sbtw.ui.browser import Browser
from sbtw.ui.entity import EntitiesView
from sbtw.ui.files import FilesView
from sbtw.ui.header import Footer, Header
from sbtw.ui.label import RefreshLabel
from sbtw.ui.tasks import TasksView

if TYPE_CHECKING:
    from pathlib import Path

    from qtpy.QtCore import QObject


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ------------- UI  Settings -------------
        self.setWindowTitle(f"{NAME} - v{__version__}")
        self.setMinimumSize(800, 500)
        self.resize(1200, 500)

        # ------------- Variables -------------
        self.manager = ProjectManager()

        # ------------- Layout -------------
        widget = QWidget(self)
        self.setCentralWidget(widget)

        main_layout = QVBoxLayout(widget)

        # ------------- Header -------------
        self.header = Header(name=self.manager.username, projects=self.manager.get_projects(), parent=self)
        main_layout.addWidget(self.header, stretch=1)

        # ------------- Browser -------------
        self.browser = Browser(data={}, parent=self)
        main_layout.addWidget(self.browser, stretch=19)

        # ------------- Footer -------------
        self.footer = Footer(parent=self)
        main_layout.addWidget(self.footer, stretch=1)

        # ------------- Signals -------------
        self.footer.size_slider.slider.valueChanged.connect(self.browser.set_thumbnail_size)
        self.header.projects_view.project_updated.connect(self.on_project_clicked)
        self.header.projects_view.project_clicked.connect(self.on_project_clicked)
        self.header.projects_view.project_clicked.connect(self.header.project_label.set_project)
        self.header.projects_view.project_opened.connect(self.on_project_opened)
        self.header.projects_view.project_removed.connect(self.on_project_removed)
        self.header.refresh_btn.clicked.connect(
            lambda: self.on_view_updated(self.header.refresh_btn, self.manager.current_path)
        )
        self.browser.row_selected.connect(self.on_row_selected)
        self.browser.row_clicked.connect(self.on_row_clicked)
        self.browser.assets_view.updated.connect(self.on_view_updated)
        self.browser.shots_view.updated.connect(self.on_view_updated)
        self.browser.files_view.updated.connect(self.on_view_updated)
        self.browser.tasks_view.updated.connect(self.on_view_updated)
        self.browser.entity_tabs.currentChanged.connect(
            lambda _: self.on_project_clicked(self.manager.project.name) if self.manager.project else None
        )

    def on_project_opened(self):
        logger.info("Opening %s ...", self.manager.project.root.parent.as_posix())
        os.startfile(self.manager.project.root.parent)

    def on_project_clicked(self, project: str):
        self.manager.set_project(project)
        self.header.projects_view.set_projects(self.manager.get_projects())
        entity_type = self.browser.get_current_entity_type()
        if entity_type == EntityType.Asset:
            self.browser.assets_view.set_rows(rows=self.manager.project.get_entities(entity_type=entity_type))
        if entity_type == EntityType.Shot:
            self.browser.shots_view.set_rows(rows=self.manager.project.get_entities(entity_type=entity_type))
        self.browser.tasks_view.clear_tree()
        self.browser.files_view.clear_tree()

    def on_project_removed(self):
        self.manager.project = None
        self.header.projects_view.set_projects(self.manager.get_projects())
        self.browser.assets_view.clear_tree()
        self.browser.tasks_view.clear_tree()
        self.browser.files_view.clear_tree()

    def on_row_clicked(self, path: Path):
        logger.info("Opening %s ...", path.as_posix())
        os.startfile(path)

    def on_row_selected(self, sender: QObject, path: Path):
        if not path:
            return

        self.manager.current_path = path
        element = self.manager.get_current_element()

        if isinstance(sender, (FilesView, TasksView)) and element.get("task") and element.get("entity"):
            self.browser.files_view.set_rows(
                rows=self.manager.project.get_files(
                    task=element["task"],
                    entity=element["entity"],
                    entity_type=element["entity_type"],
                ),
            )

        if isinstance(sender, EntitiesView) and element.get("entity"):
            self.browser.tasks_view.set_rows(
                rows=self.manager.project.get_tasks(entity=element["entity"], entity_type=element["entity_type"])
            )
            self.browser.files_view.clear_tree()

    def on_view_updated(self, sender: QObject, path: Path):
        self.manager.current_path = path
        element = self.manager.get_current_element()

        if isinstance(sender, FilesView) or (isinstance(sender, RefreshLabel) and element.get("task")):
            self.browser.files_view.set_rows(
                rows=self.manager.project.get_files(
                    task=element["task"],
                    entity=element["entity"],
                    entity_type=element["entity_type"],
                )
            )

        elif isinstance(sender, (TasksView, RefreshLabel)) and element.get("entity"):
            self.browser.tasks_view.set_rows(
                rows=self.manager.project.get_tasks(
                    entity=element["entity"],
                    entity_type=element["entity_type"],
                )
            )

        elif isinstance(sender, EntitiesView):
            self.on_project_clicked(self.manager.project.name)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()

    sys.exit(app.exec())
