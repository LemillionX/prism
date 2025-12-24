from __future__ import annotations

import math

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QWidget


class DataView(QWidget):
    def __init__(self, data: dict, parent: QWidget | None = None):
        super().__init__(parent=parent)

        # ---------- Layout ----------
        self.main_layout = QGridLayout(parent=self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setHorizontalSpacing(40)
        self.main_layout.setVerticalSpacing(4)

        self.set_data(data=data)

    def set_data(self, data: dict):
        cols = 2

        for i, value in enumerate(data.values()):
            row = i // cols
            col = i % cols

            label = QLabel(str(value))
            label.setAlignment(
                Qt.AlignmentFlag.AlignLeft if col == 0 else Qt.AlignmentFlag.AlignRight
            )
            self.main_layout.addWidget(label, row, col)


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
