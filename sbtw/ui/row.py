from __future__ import annotations

from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from sbtw.core.constant import DEFAULT_THUMBNAIL
from sbtw.core.log import logger
from sbtw.ui.data import DataView
from sbtw.ui.thumbnail import Thumbnail


class Row(QWidget):
    def __init__(self, data: dict, keys: set[str] | None = None, parent: QWidget | None = None):
        super().__init__(parent=parent)

        # ------------- Variables -------------
        self.data = data
        self.name = self.data.get("name")
        self.keys = {"name"}
        self.keys.update(keys or {})

        # ------------- Layout -------------
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # ------------- Thumbnail -------------
        self.thumbnail = Thumbnail(parent=self)
        self.thumbnail.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # Update row height when thumbnail size changes
        self.thumbnail.size_changed.connect(self._on_thumbnail_size_changed)
        self.thumbnail.set_image(QPixmap(self.data.get("thumbnail", DEFAULT_THUMBNAIL.as_posix())))
        main_layout.addWidget(self.thumbnail, 0)

        # ------------- Data -------------
        self.data_view = DataView(data={k: v for k, v in self.data.items() if k in self.keys}, parent=self)
        self.data_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(self.data_view, 1)

    def _on_thumbnail_size_changed(self, height: int) -> None:  # noqa: ARG002
        try:
            self.updateGeometry()
            if self.parent():
                self.parent().updateGeometry()
        except Exception as e:  # noqa: BLE001
            logger.exception(f"Failed to update row geometry: {e}")


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
