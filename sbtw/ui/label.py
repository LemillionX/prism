from __future__ import annotations

import os
from typing import TYPE_CHECKING

from core.log import LOG_DIR
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QMouseEvent, QPixmap
from qtpy.QtWidgets import QHBoxLayout, QInputDialog, QLabel, QWidget

from sbtw.core.constant import LOG_THUMBNAIL, REFRESH_ICON, USER_THUMBNAIL
from sbtw.core.manager import ProjectManager

if TYPE_CHECKING:
    from pathlib import Path


class Label(QWidget):
    clicked = Signal()

    def __init__(self, text: str, icon: Path, size: int = 32, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Variables -------------
        self.label = QLabel(text)
        self.size = size
        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)
        self.setLayout(main_layout)

        # ------------- Icon -------------
        self.icon = QLabel()
        self.set_icon(icon)

        # ------------- UI -------------
        main_layout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addStretch()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)

    def set_text(self, text: str):
        self.label.setText(text)

    def set_icon(self, icon: Path):
        self.icon.setPixmap(
            QPixmap(icon).scaled(
                self.size,
                self.size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class UserLabel(Label):
    text_updated = Signal(str)

    def __init__(self, name: str, parent: QWidget | None = None):
        super().__init__(text=name, icon=USER_THUMBNAIL, size=40, parent=parent)
        self.clicked.connect(self.set_name)

    def set_name(self):
        name, ok = QInputDialog.getText(None, "Change Username", "Username:", text=self.label.text())
        if ok:
            manager = ProjectManager()
            manager.save_config(username=name)
            self.label.setText(name)
            self.text_updated.emit(name)


class RefreshLabel(Label):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(text="", icon=REFRESH_ICON, parent=parent)


class LogLabel(Label):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(text="Logs", icon=LOG_THUMBNAIL, parent=parent)
        self.clicked.connect(self.open_logs_folder)

    def open_logs_folder(self):
        os.startfile(LOG_DIR)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = UserLabel(name="Larsene")
    view.show()

    sys.exit(app.exec())
