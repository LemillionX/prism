from __future__ import annotations

from functools import partial

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

from sbtw.actions.base import ActionBase
from sbtw.core.config import ACTIONS
from sbtw.core.log import logger
from sbtw.ui.row import Row


class View(QWidget):
    row_selected = Signal(dict)  # emits data of clicked row

    def __init__(
        self,
        rows: list[dict] | None = None,
        keys: set | None = None,
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
            partial(self.show_context_menu, ACTIONS)
        )
        main_layout.addWidget(self.tree)

        # ---------- Init Data ----------
        self.tree.itemClicked.connect(self.on_item_clicked)
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

    def show_context_menu(self, actions: dict, pos: QPoint):
        # Map from the click position to a tree item
        if not (item := self.tree.itemAt(pos)):
            return

        if not (row := self.tree.itemWidget(item, 0)):
            return

        menu = QMenu(self)
        self.add_actions(menu, actions, row)
        # # Example actions
        # action_view = QAction("View Details", self)
        # action_edit = QAction("Edit", self)
        # action_delete = QAction("Delete", self)

        # menu.addAction(action_view)
        # menu.addAction(action_edit)
        # menu.addAction(action_delete)

        # # Connect actions
        # action_view.triggered.connect(partial(self.on_view, row))
        # action_edit.triggered.connect(partial(self.on_edit, row))
        # action_delete.triggered.connect(partial(self.on_delete, row))

        # Show menu at the global position
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def add_actions(self, menu: QMenu, actions: list, row: Row):
        for key, _actions in actions.items():
            for action in _actions:
                self.add_action(menu, key, action, row)

    def add_action(self, menu: QMenu, key: str, action: ActionBase, row: Row):
        qaction = QAction(action.name(), self)
        menu.addAction(qaction)
        qaction.triggered.connect(partial(action.execute, **row.data))

    def on_view(self, row: Row):
        logger.info("Viewing %s ...", row.data.get("name"))

    def on_edit(self, row: Row):
        logger.info("Editing %s ...", row.data.get("name"))

    def on_delete(self, row: Row):
        logger.info("Deleting %s ...", row.data.get("name"))


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
