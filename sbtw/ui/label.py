from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QMouseEvent, QPixmap
from qtpy.QtWidgets import QHBoxLayout, QInputDialog, QLabel, QWidget

from sbtw.core.constant import REFRESH_ICON, USER_THUMBNAIL
from sbtw.core.manager import ProjectManager

if TYPE_CHECKING:
    from pathlib import Path


class Label(QWidget):
    clicked = Signal()

    def __init__(self, text: str, icon: Path, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Variables -------------
        size = 32
        self.label = QLabel(text)

        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)
        self.setLayout(main_layout)

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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


class UserLabel(Label):
    text_updated = Signal(str)

    def __init__(self, name: str, parent: QWidget | None = None):
        super().__init__(text=name, icon=USER_THUMBNAIL, parent=parent)
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


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = UserLabel(name="Larsene")
    view.show()

    sys.exit(app.exec())
