from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QWidget

from sbtw.core.config import ACTIONS
from sbtw.core.constant import PROJECTS_THUMBNAIL
from sbtw.ui.label import RefreshLabel, UserLabel
from sbtw.ui.projects import ProjectsLabel, ProjectsView


class Header(QWidget):
    def __init__(self, name: str, projects: list[dict] | None, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Variables -------------
        self.name = name
        self.projects = projects or []

        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(30)

        # ------------- User -------------
        main_layout.addStretch()
        user_label = UserLabel(name=self.name, parent=self)
        user_label.text_updated.connect(self.set_name)
        main_layout.addWidget(user_label, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Projects -------------
        self.projects_label = ProjectsLabel(parent=self)
        self.projects_label.clicked.connect(self.toggle_projects_grid)
        self.projects_view = ProjectsView(projects=self.projects, actions=ACTIONS, parent=None)
        main_layout.addWidget(self.projects_label, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Refresh -------------
        refresh_icon = RefreshLabel()
        main_layout.addWidget(refresh_icon, alignment=Qt.AlignmentFlag.AlignRight)

    def set_name(self, name: str):
        self.name = name

    def toggle_projects_grid(self):
        if self.projects_view.isVisible():
            self.projects_view.hide()
        else:
            self.show_projects_grid()

    def show_projects_grid(self):
        # Position grid under the label
        global_bottom_right = self.projects_label.mapToGlobal(self.projects_label.rect().bottomRight())

        x = global_bottom_right.x() - self.projects_view.width()
        y = global_bottom_right.y()

        self.projects_view.move(x, y)
        self.projects_view.show()


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    _projects = [{"name": f"MyProject{i:02d}", "thumbnail": PROJECTS_THUMBNAIL} for i in range(10)]

    view = Header(name="Larsene", projects=_projects)
    view.show()

    sys.exit(app.exec())
