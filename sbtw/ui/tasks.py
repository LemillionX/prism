from __future__ import annotations

from qtpy.QtWidgets import QMenu, QWidget

from sbtw.actions.base import ActionBase
from sbtw.ui.row import Row
from sbtw.ui.view import View


class TasksView(View):
    def __init__(self, rows: list[dict] | None = None, parent: QWidget | None = None):
        super().__init__(rows=rows, parent=parent)

    def add_action(self, menu: QMenu, key: str, action: ActionBase, row: Row):
        if key == row.data.get("name"):
            super().add_action(menu, key, action, row)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [{"name": name} for name in ["Design", "Modeling", "Texture", "Rig"]]

    view = TasksView(rows=_data)
    view.show()

    sys.exit(app.exec())
