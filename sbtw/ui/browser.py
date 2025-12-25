from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSplitter, QWidget

from sbtw.ui.assets import AssetsView
from sbtw.ui.files import FilesView
from sbtw.ui.tasks import TasksView


class Browser(QWidget):
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
        self.assets_view = AssetsView(rows=data, parent=self)
        splitter.addWidget(self.assets_view)

        # ---------- Tasks ----------
        self.tasks_view = TasksView(parent=self)
        self.tasks_view.layout().insertWidget(0, QLabel("Tasks"))
        splitter.addWidget(self.tasks_view)

        # ---------- Files ----------
        self.files_view = FilesView(parent=self)
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

    def on_row_selected(self, data: dict):
        if isinstance(self.sender(), AssetsView):
            self.tasks_view.set_rows(rows=data.get("tasks", []))
            self.files_view.clear_tree()

        if isinstance(self.sender(), TasksView):
            self.files_view.set_rows(rows=data.get("files", []))


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
