from __future__ import annotations

from functools import partial
from pathlib import Path

from qtpy.QtCore import QDir, QEvent, QObject, QRect, QRegularExpression, QSize, Qt, Signal
from qtpy.QtGui import QMouseEvent, QPixmap, QRegularExpressionValidator
from qtpy.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sbtw.core.constant import BROWSER_EXPLORER_ICON, PLUS_ICON, PROJECTS_THUMBNAIL
from sbtw.core.log import logger
from sbtw.core.manager import ProjectManager
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
    project_updated = Signal(str)

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
            btn = ProjectLabel(text=action.get("name"), thumbnail=action.get("icon"), parent=self)
            btn.clicked.connect(partial(self.on_project_clicked, {"action": action.get("name")}))
            main_layout.addWidget(btn, row + 1, col)

        if parent:
            parent.installEventFilter(self)

    def on_project_clicked(self, project: dict):
        if project.get("action") == "Create new Project":
            dialog = ProjectForm()
            if dialog.exec() == QDialog.Accepted:
                logger.info("Creating a new project")
                name, root = dialog.get_projects_data()
                manager: ProjectManager = ProjectManager()
                manager.create(name=name, root=root)
                self.project_updated.emit(name)

        elif project.get("action") == "Open current Project in Explorer":
            logger.info("Opening current project in Explorer ")
            self.project_opened.emit()
        else:
            logger.info("Switching on project %s", project.get("name"))
            self.project_clicked.emit(project.get("name"))
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent):
        # If there is a click inside the widget
        if (
            event.type() == QEvent.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and not self.geometry().contains(event.globalPos())
        ):
            self.hide()

        return super().eventFilter(watched, event)


class ProjectsLabel(Label):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(text="Projects", icon=PROJECTS_THUMBNAIL, parent=parent)


class ProjectLabel(QWidget):
    clicked = Signal()

    def __init__(self, text: str, thumbnail: Path | None = None, parent: QWidget | None = None):
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
        label.show()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ProjectForm(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- UI Settings -------------
        self.setWindowTitle("Create a project")

        # ------------- Layout -------------
        main_layout = QFormLayout(self)
        self.setLayout(main_layout)

        # ------------- Project Name -------------
        self.name = QLineEdit(parent=self, placeholderText="MyProjectName")
        self.name.setFixedWidth(200)
        main_layout.addRow("Project Name:", self.name)

        # Add validator to restrict characters to Windows folder name rules
        regex = QRegularExpression(r'^[^\s\.\\\/:*?"<>|][^\s\\\/:*?"<>|]*[^\s\.\\\/:*?"<>|]$')
        validator = QRegularExpressionValidator(regex, self.name)
        self.name.setValidator(validator)

        # ------------- Project Path -------------
        self.path_edit = QLineEdit(parent=self, placeholderText=f"C:/Path/To/Root/Folder. Default is {QDir.rootPath()}")
        self.path_edit.setMinimumWidth(250)
        self.browse_button = QPushButton("Browse", parent=self)
        self.browse_button.clicked.connect(self.browse_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        main_layout.addRow("Project Path:", path_layout)

        # ------------- Buttons -------------
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addRow(button_box)

    def browse_path(self):
        # Get the default disk (C: on Windows)
        default_dir = QDir.rootPath()  # This gives the root directory, e.g., "C:/" on Windows
        folder = QFileDialog.getExistingDirectory(self, "Select Project Directory", default_dir)
        if folder:
            self.path_edit.setText(folder)

    def get_projects_data(self) -> tuple[str, Path]:
        return self.name.text(), Path(self.path_edit.text() or "C:/", self.name.text())


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = ProjectForm()
    view.show()

    sys.exit(app.exec())
