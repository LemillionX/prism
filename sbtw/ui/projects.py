from __future__ import annotations

from functools import partial
from pathlib import Path

from qtpy.QtCore import QEvent, QObject, QRect, QSize, Qt, Signal
from qtpy.QtGui import QMouseEvent, QPixmap
from qtpy.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from sbtw.core.constant import BROWSER_EXPLORER_ICON, PLUS_ICON, PROJECTS_THUMBNAIL
from sbtw.core.log import logger
from sbtw.ui.label import Label


def scale_and_crop_center(pixmap: QPixmap, target_size: QSize) -> QPixmap:
    if pixmap.isNull():
        return pixmap

    # Step 1: scale (expand to cover)
    scaled = pixmap.scaled(
        target_size,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation,
    )

    # Step 2: crop center
    x = (scaled.width() - target_size.width()) // 2
    y = (scaled.height() - target_size.height()) // 2

    return scaled.copy(QRect(x, y, target_size.width(), target_size.height()))


class ProjectsGrid(QWidget):
    project_clicked = Signal(str)
    project_opened = Signal()

    def __init__(self, projects: list[dict], parent: QWidget | None = None):
        super().__init__(parent=parent)

        # ------------- UI Settings -------------
        if not parent:
            self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

        # ------------- Layout -------------
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        # ------------- Projects -------------
        cols = 3
        for i, project in enumerate(projects):
            row = i // cols
            col = i % cols
            project_label = ProjectLabel(
                text=project.get("name"),
                thumbnail=project.get("thumbnail"),
                parent=self,
            )
            project_label.clicked.connect(partial(self.on_project_clicked, project))
            main_layout.addWidget(project_label, row, col)

        # ------------- Actions -------------
        actions = [
            {"name": "Create new Project", "icon": PLUS_ICON},
            {
                "name": "Open current Project in Explorer",
                "icon": BROWSER_EXPLORER_ICON,
            },
        ]
        row = len(projects) // cols
        for col, action in enumerate(actions):
            btn = ProjectLabel(
                text=action.get("name"), thumbnail=action.get("icon"), parent=self
            )
            btn.clicked.connect(
                partial(self.on_project_clicked, {"action": action.get("name")})
            )
            main_layout.addWidget(btn, row + 1, col)

        if parent:
            parent.installEventFilter(self)

    def on_project_clicked(self, project: dict):
        if project.get("action") == "Create new Project":
            logger.info("Creating a new project")
        elif project.get("action") == "Open current Project in Explorer":
            logger.info("Opening current project in Explorer ")
            self.project_opened.emit()
        else:
            logger.info("Switching on project %s", project.get("name"))
            self.project_clicked.emit(project.get("name"))
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent):
        # If there is a click
        if event.type() == QEvent.MouseButtonPress and isinstance(event, QMouseEvent):
            # Check if click is outside this widget
            if not self.geometry().contains(event.globalPos()):
                self.hide()

        return super().eventFilter(watched, event)


class ProjectsLabel(Label):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(text="Projects", icon=PROJECTS_THUMBNAIL, parent=parent)


class ProjectLabel(QWidget):
    clicked = Signal()

    def __init__(
        self, text: str, thumbnail: Path | None = None, parent: QWidget | None = None
    ):
        super().__init__(parent=parent)

        width, height = 200, 112
        text_height = 24
        thumbnail = thumbnail or PROJECTS_THUMBNAIL

        # ------------- Layout -------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------- Container -------------
        container = QWidget(self)
        container.setFixedSize(width, height)
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)

        # ------------- Image -------------
        icon = QLabel(container)
        icon.setFixedSize(width, height)
        icon.setPixmap(scale_and_crop_center(QPixmap(thumbnail), QSize(width, height)))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.show()  # make sure it paints

        # ------------- Text -------------
        label = QLabel(text, container)
        label.setFixedSize(width, text_height)
        label.move(0, height - text_height)  # position at bottom
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
            }
        """)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        label.show()  # must call show manually

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    from sbtw.core.constant import PROJECTS_THUMBNAIL

    app = QApplication(sys.argv)

    _projects = [
        {"name": f"MyProject{i:02d}", "thumbnail": PROJECTS_THUMBNAIL}
        for i in range(10)
    ]

    view = ProjectsGrid(projects=_projects)
    view.show()

    sys.exit(app.exec())
