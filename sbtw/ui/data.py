from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget

if TYPE_CHECKING:
    from pathlib import Path


class DataView(QWidget):
    def __init__(self, data: dict, parent: QWidget | None = None):
        super().__init__(parent=parent)

        # ---------- Layout ----------
        self.main_layout = QGridLayout(parent=self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setHorizontalSpacing(40)
        self.main_layout.setVerticalSpacing(4)

        # Ensure the layout is installed on this widget so children are shown
        self.setLayout(self.main_layout)

        self.set_data(data=data)

    def set_data(self, data: dict):
        cols = 2

        # Clear existing widgets from the layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item:
                w = item.widget()
                if w:
                    w.setParent(None)

        for i, (key, value) in enumerate(data.items()):
            row = i // cols
            col = i % cols
            alignment = Qt.AlignmentFlag.AlignLeft if col == 0 else Qt.AlignmentFlag.AlignRight
            alignment = alignment | Qt.AlignmentFlag.AlignVCenter
            if key == "icon":
                alignment = Qt.AlignmentFlag.AlignLeft
            label = self.get_icons(value, parent=self) if key in {"icon"} else QLabel(str(value))
            if key == "status":
                label.setProperty("status", value)
            self.main_layout.addWidget(label, row, col, alignment=alignment)

    def get_icons(self, icons: list[Path], parent: QWidget | None = None) -> QWidget:
        container = QWidget(parent=parent)
        layout = QHBoxLayout()
        container.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        size = 24
        for icon in icons:
            label = QLabel()
            label.setPixmap(
                QPixmap(icon).scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)

        return container


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    view = DataView(
        {
            "name": "Clementine",
            "author": "Telltale Games",
            "status": "wtg",
            "date": "24/12/2025, 15:54",
            "size": "14.59 mb",
        }
    )
    view.show()

    sys.exit(app.exec())
