from __future__ import annotations

from qtpy.QtWidgets import QWidget

from sbtw.ui.view import View


class FilesView(View):
    def __init__(self, rows: list[dict] | None = None, parent: QWidget | None = None):
        super().__init__(rows=rows, parent=parent)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [
        {
            "name": "Clementine",
            "author": "Telltale Games",
            "status": "wtg",
            "date": "24/12/2025, 15:54",
            "size": f"{i:02d} MB",
            "thumbnail": r"E:\Sammy\Clem.png",
        }
        for i in range(10)
    ]

    view = FilesView(rows=_data)
    view.show()

    sys.exit(app.exec())
