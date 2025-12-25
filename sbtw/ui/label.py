from __future__ import annotations

from pathlib import Path

from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QHBoxLayout, QLabel, QWidget

from sbtw.core.constant import PROJECTS_THUMBNAIL, REFRESH_ICON, USER_THUMBNAIL


class Label(QWidget):
    def __init__(self, text: str, icon: Path, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Variables -------------
        size = 32
        self.label = QLabel(text)

        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)

        # ------------- Icon -------------
        icon_label = QLabel()
        icon_label.setPixmap(
            QPixmap(icon).scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        # ------------- UI -------------
        main_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addStretch()


class UserLabel(Label):
    def __init__(self, name: str, parent: QWidget | None = None):
        super().__init__(text=name, icon=USER_THUMBNAIL, parent=parent)


class ProjectsLabel(Label):
    def __init__(self, parent=None):
        super().__init__(text="Projects", icon=PROJECTS_THUMBNAIL, parent=parent)


class RefreshLabel(Label):
    def __init__(self, parent=None):
        super().__init__(text="", icon=REFRESH_ICON, parent=parent)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = UserLabel(name="Larsene")
    view.show()

    sys.exit(app.exec())
