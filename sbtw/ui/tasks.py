from __future__ import annotations

from typing import Any

from qtpy.QtWidgets import QWidget

from sbtw.ui.row import Row
from sbtw.ui.view import View


class TasksView(View):
    def __init__(
        self,
        rows: list[dict] | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(rows=rows, actions=actions, parent=parent)

    def is_action_valid(self, **kwargs: Any):
        if task := kwargs.get("key"):
            row = kwargs.get("row")
            name = row.data.get("name") if isinstance(row, Row) else "TasksView"
            return task == name or (
                name != "TasksView" and super().is_action_valid(**kwargs)
            )
        return super().is_action_valid(**kwargs)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [{"name": name} for name in ["Design", "Modeling", "Texture", "Rig"]]

    view = TasksView(rows=_data)
    view.show()

    sys.exit(app.exec())
