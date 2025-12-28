from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qtpy.QtCore import QObject, QPoint, Qt, Signal
from qtpy.QtWidgets import QAction, QMenu, QSizePolicy, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from sbtw.actions.base import MenuBase
from sbtw.ui.row import Row

if TYPE_CHECKING:
    from sbtw.actions.base import ActionBase


class Base(QWidget):
    updated = Signal(QObject, Path)

    def __init__(self, actions: dict | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.action_base = self.__class__.__name__.replace("View", "Base")
        self.action_view = self.__class__.__name__
        self.actions = actions or {}

    def is_action_valid(self, **kwargs: Any):
        if (task := kwargs.get("key")) and (data := kwargs.get("data")):
            name = data.get("name") if data.get("is_element", False) else self.action_view
            return task == name or (name != self.action_view and (self.action_base in task or task == "Base"))
        return False

    def add_actions(
        self,
        menu: QMenu,
        actions: dict,
        data: dict | None = None,
    ):
        for key, _actions in actions.items():
            for action in _actions:
                if self.is_action_valid(action=action, data=data, key=key):
                    if isinstance(action, MenuBase):
                        submenu = menu.addMenu(action.name())
                        self.add_actions(submenu, {key: action.actions}, data)
                    else:
                        self.add_action(menu, action, data)

    def add_action(
        self,
        menu: QMenu,
        action: ActionBase,
        data: dict | None = None,
    ):
        qaction = QAction(action.name(), self)
        if data:
            menu.addAction(qaction)
            qaction.triggered.connect(partial(action.execute, **data, view=self))


class View(Base):
    row_selected = Signal(dict)
    row_clicked = Signal(dict)

    def __init__(
        self,
        rows: list[dict] | None = None,
        keys: set | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(actions=actions, parent=parent)
        # ---------- Variables ----------
        self.keys = {"name"}
        self.keys.update(keys or {})
        self.entity = None

        # ---------- Layout ----------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        # ---------- Tree ----------
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(partial(self.show_context_menu, self.actions))
        self.tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.tree.setMinimumWidth(0)
        self.tree.header().setStretchLastSection(True)
        main_layout.addWidget(self.tree)

        # ---------- UI ----------
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setMinimumWidth(0)

        # ---------- Init Data ----------
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.set_rows(rows=rows or [])

    def add_row(self, data: dict, parent_item: QTreeWidgetItem | None = None):
        item = QTreeWidgetItem()

        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree.addTopLevelItem(item)

        row = Row(data=data, keys=self.keys, parent=self)
        self.tree.setItemWidget(item, 0, row)

        return item

    def clear_tree(self):
        if isinstance(self.tree, QTreeWidget):
            while self.tree.topLevelItemCount():
                item = self.tree.takeTopLevelItem(0)

                # Delete any widget set on this item
                widget = self.tree.itemWidget(item, 0)
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
                del item

    def get_entity(self, path: Path) -> dict:
        return {"name": path.parent.stem, "path": path.parent}

    def set_rows(self, rows: list[dict], entity: dict | None = None):
        self.clear_tree()
        # ---------- Data ----------
        self.entity = entity
        for row in rows:
            self.add_row(row)

        # ---------- UI Settings ----------
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )
        self.setMinimumWidth(self.sizeHint().width())

    def on_item_clicked(self, item: QTreeWidgetItem):
        # Get associated Row
        if (row := self.tree.itemWidget(item, 0)) and isinstance(row, Row):
            self.row_selected.emit(row.data)

    def on_item_double_clicked(self, item: QTreeWidgetItem):
        # Get associated Row
        if (row := self.tree.itemWidget(item, 0)) and isinstance(row, Row):
            self.row_clicked.emit(row.data)

    def show_context_menu(self, actions: dict, pos: QPoint):
        menu = QMenu(self)

        # Menu for item on the view
        if (item := self.tree.itemAt(pos)) and (row := self.tree.itemWidget(item, 0)):
            self.add_actions(menu, actions, data={**row.data, "is_element": True})
        else:
            # Menu for the view
            self.add_actions(menu, actions, data=self.entity)

        # Show menu at the global position
        menu.exec(self.tree.viewport().mapToGlobal(pos))


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    _data = [
        {
            "name": f"Clementine{i:02d}",
            "thumbnail": r"E:\Sammy\Clem.png",
        }
        for i in range(20)
    ]

    view = View(rows=_data)
    view.show()

    sys.exit(app.exec())
