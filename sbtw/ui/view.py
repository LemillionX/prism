from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from qtpy.QtCore import QPoint, Qt, Signal
from qtpy.QtWidgets import (
    QAction,
    QMenu,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sbtw.ui.row import Row

if TYPE_CHECKING:
    from sbtw.actions.base import ActionBase


class View(QWidget):
    row_selected = Signal(dict)
    row_clicked = Signal(dict)

    def __init__(
        self,
        rows: list[dict] | None = None,
        keys: set | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        # ---------- Variables ----------
        self.keys = {"name"}
        self.keys.update(keys or {})

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
        self.tree.customContextMenuRequested.connect(
            partial(self.show_context_menu, actions or {})
        )
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

    def set_rows(self, rows: list[dict]):
        self.clear_tree()
        # ---------- Data ----------
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
        # Map from the click position to a tree item
        if not (item := self.tree.itemAt(pos)):
            return

        if not (row := self.tree.itemWidget(item, 0)):
            return

        menu = QMenu(self)
        self.add_actions(menu, actions, row)

        # Show menu at the global position
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def is_action_valid(self, **kwargs):
        return kwargs.get("key") == "Base"

    def add_actions(self, menu: QMenu, actions: list, row: Row):
        for key, _actions in actions.items():
            for action in _actions:
                if self.is_action_valid(action=action, row=row, key=key):
                    self.add_action(menu, action, row)

    def add_action(self, menu: QMenu, action: ActionBase, row: Row):
        qaction = QAction(action.name(), self)
        menu.addAction(qaction)
        qaction.triggered.connect(partial(action.execute, **row.data, view=self))


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
