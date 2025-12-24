from __future__ import annotations

from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from sbtw.ui.data import DataView
from sbtw.ui.thumbnail import Thumbnail


class Row(QWidget):
    def __init__(self, data: dict, parent: QWidget | None = None):
        super().__init__(parent=parent)

        # ------------- Layout -------------
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # ------------- Thumbnail -------------
        self.thumbnail = Thumbnail()
        self.thumbnail.set_image(QPixmap(data.get("thumbnail")))
        self.thumbnail.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.thumbnail, 0)
        # ------------- Data -------------
        self.data_view = DataView(
            data={k: v for k, v in data.items() if k != "thumbnail"},
        )
        self.data_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        main_layout.addWidget(self.data_view, 1)

        # Default Settings
        self.setMinimumSize(500, 10)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    row = Row(
        {
            "name": "Clementine",
            "author": "Telltale Games",
            "status": "wtg",
            "date": "24/12/2025, 15:54",
            "size": "14.59 mb",
            "thumbnail": r"E:\Sammy\Clem.png",
        }
    )
    row.show()

    sys.exit(app.exec())
