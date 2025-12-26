from __future__ import annotations

from pathlib import Path

from qtpy.QtCore import QObject, Qt, Signal
from qtpy.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSplitter, QWidget

from sbtw.core.config import ACTIONS
from sbtw.ui.assets import AssetsView
from sbtw.ui.files import FilesView
from sbtw.ui.tasks import TasksView
from sbtw.ui.view import View


class Browser(QWidget):
    row_selected = Signal(QObject, Path)
    row_clicked = Signal(Path)

    def __init__(self, data: dict, parent: QWidget | None = None):
        super().__init__(parent)

        # ---------- Layout ----------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        # ---------- Horizontal splitter ----------
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        splitter.addWidget(QSplitter(Qt.Vertical))

        # ---------- Entity ----------
        self.assets_view = AssetsView(rows=data, actions=ACTIONS, parent=self)
        splitter.addWidget(self.assets_view)

        # ---------- Tasks ----------
        self.tasks_view = TasksView(actions=ACTIONS, parent=self)
        self.tasks_view.layout().insertWidget(0, QLabel("Tasks"))
        splitter.addWidget(self.tasks_view)

        # ---------- Files ----------
        self.files_view = FilesView(actions=ACTIONS, parent=self)
        self.files_view.layout().insertWidget(0, QLabel("Files"))
        splitter.addWidget(self.files_view)

        # ---------- UI Settings----------
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setMinimumSize(0, 0)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        splitter.setStretchFactor(3, 5)
        splitter.setChildrenCollapsible(False)

        # ---------- Connections ----------
        self.assets_view.row_selected.connect(self.on_row_selected)
        self.tasks_view.row_selected.connect(self.on_row_selected)
        self.files_view.row_selected.connect(self.on_row_selected)
        self.files_view.row_clicked.connect(self.on_row_clicked)

    def on_row_selected(self, data: dict):
        if isinstance(self.sender(), View):
            self.row_selected.emit(self.sender(), data.get("path"))

    def on_row_clicked(self, data: dict):
        if isinstance(self.sender(), View):
            self.row_clicked.emit(data.get("path"))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [
        {
            "name": f"Clementine{i:02d}",
            "thumbnail": r"E:\Sammy\Clem.png",
            "tasks": [
                {
                    "name": task,
                    "path": Path(f"Clementine{i:02d}", task).as_posix(),
                    "files": [
                        {
                            "name": f"Clementine{i:02d}_{task}_v{idx:03d}",
                        }
                        for idx in range(32, 0, -1)
                    ],
                }
                for task in ["Design", "Modeling", "Texture", "Rig"]
            ],
        }
        for i in range(20)
    ]

    view = Browser(data=_data)
    view.show()

    sys.exit(app.exec())
