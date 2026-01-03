from __future__ import annotations

import sys

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QSlider, QWidget

from sbtw.core.config import ACTIONS
from sbtw.core.constant import PROJECTS_THUMBNAIL
from sbtw.ui.label import LogLabel, RefreshLabel, UserLabel
from sbtw.ui.projects import ProjectLabel, ProjectsLabel, ProjectsView


class Header(QWidget):
    def __init__(self, name: str, projects: list[dict] | None, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Variables -------------
        self.name = name
        self.projects = projects or []

        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(30)

        # ------------- Current Project -------------
        self.project_label = ProjectLabel(parent=self)
        main_layout.addWidget(self.project_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # ------------- User -------------
        main_layout.addStretch()
        user_btn = UserLabel(name=self.name, parent=self)
        user_btn.text_updated.connect(self.set_name)
        main_layout.addWidget(user_btn, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Projects -------------
        self.projects_label = ProjectsLabel(parent=self)
        self.projects_label.clicked.connect(self.toggle_projects_grid)
        self.projects_view = ProjectsView(projects=self.projects, actions=ACTIONS, parent=None)
        main_layout.addWidget(self.projects_label, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Refresh -------------
        self.refresh_btn = RefreshLabel()
        main_layout.addWidget(self.refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Open Logs -------------
        logs_btn = LogLabel(parent=self)
        main_layout.addWidget(logs_btn, alignment=Qt.AlignmentFlag.AlignRight)

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


class Footer(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.addStretch()
        # ------------- Slider for Thumbnail size -------------
        self.size_slider = SizeSlider(parent=self)
        main_layout.addWidget(self.size_slider, alignment=Qt.AlignmentFlag.AlignRight)


class SizeSlider(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # ------------- Slider -------------
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TickPosition.NoTicks)
        main_layout.addWidget(self.slider)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    _projects = [{"name": f"MyProject{i:02d}", "thumbnail": PROJECTS_THUMBNAIL} for i in range(10)]

    view = Header(name="Larsene", projects=_projects)
    view.show()

    sys.exit(app.exec())
    sys.exit(app.exec())
