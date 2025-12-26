from __future__ import annotations

from qtpy.QtWidgets import QWidget

from sbtw.ui.view import View


class TasksView(View):
    def __init__(self, rows: list[dict] | None = None, parent: QWidget | None = None):
        super().__init__(rows=rows, parent=parent)

    def is_action_valid(self, **kwargs):
        if (task := kwargs.get("key")) and (row := kwargs.get("row")):
            return task == row.data.get("name") or super().is_action_valid(**kwargs)
        return super().is_action_valid(**kwargs)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [{"name": name} for name in ["Design", "Modeling", "Texture", "Rig"]]

    view = TasksView(rows=_data)
    view.show()

    sys.exit(app.exec())
