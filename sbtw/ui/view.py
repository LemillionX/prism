from __future__ import annotations

import re
from collections import OrderedDict
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qtpy.QtCore import QObject, QPoint, QSize, Qt, Signal
from qtpy.QtWidgets import QAction, QMenu, QSizePolicy, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from sbtw.actions.base import MenuBase
from sbtw.core.log import logger
from sbtw.core.manager import ProjectManager
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
        self.group_regex = re.compile(r"^(?P<group>.+_v\d+)")

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

        # Ensure the column is reasonably wide so the widget can layout
        padding = 6
        try:
            vw = max(120, self.tree.viewport().width())
            self.tree.setColumnWidth(0, vw)
        except Exception as e:  # noqa: BLE001
            logger.exception("Failed to set column width: %s", e)

        # Set an initial height for the item based on the thumbnail widget
        try:
            thumb_h = row.thumbnail.size().height()
        except Exception:  # noqa: BLE001
            thumb_h = 50
        try:
            item.setSizeHint(0, QSize(0, max(24, int(thumb_h) + padding)))
        except Exception as e:  # noqa: BLE001
            logger.exception("Failed to set item size hint: %s", e)

        # Update item height when the thumbnail changes size; update tree layout
        try:

            def _update_item_height(h: int, it: QTreeWidgetItem = item) -> None:
                try:
                    it.setSizeHint(0, QSize(0, max(24, int(h) + padding)))
                    # Recompute layout so the tree reflects new sizes
                    self.tree.doItemsLayout()
                    self.tree.updateGeometries()
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to update item height")

            if hasattr(row, "thumbnail") and hasattr(row.thumbnail, "size_changed"):
                row.thumbnail.size_changed.connect(_update_item_height)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to connect thumbnail size change signal")

        return item

    def clear_tree(self):
        if isinstance(self.tree, QTreeWidget):

            def _delete_item_widgets(item: QTreeWidgetItem) -> None:
                # Recursively clear child widgets
                for i in range(item.childCount() - 1, -1, -1):
                    child = item.child(i)
                    _delete_item_widgets(child)
                widget = self.tree.itemWidget(item, 0)
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

            while self.tree.topLevelItemCount():
                item = self.tree.takeTopLevelItem(0)
                _delete_item_widgets(item)
                del item

    def get_entity(self, path: Path) -> dict:
        return {"name": path.parent.stem, "path": path.parent}

    def set_rows(self, rows: list[dict]):
        self.clear_tree()

        groups: OrderedDict[str, list[dict]] = OrderedDict()
        unmatched: list[dict] = []
        for row in rows:
            name = row.get("name", "")
            # Use stem to strip extensions like .png/.mp4
            try:
                base = Path(name).stem
            except Exception:  # noqa: BLE001
                base = name
            m = self.group_regex.match(base)
            if m:
                group_name = (m.groupdict().get("group") if m.groupdict() else None) or (
                    m.group(1) if m.groups() else base
                )
                groups.setdefault(group_name, []).append(row)
            else:
                # Keep non-matching rows ungrouped (top-level)
                unmatched.append(row)

        for group_name, items in groups.items():
            # If a group only contains a single item, add it as a top-level
            # item instead of creating an unnecessary header.
            if len(items) == 1:
                self.add_row(items[0])
                continue

            header = QTreeWidgetItem([group_name])
            # Make header non-selectable
            header.setFlags(header.flags() & ~Qt.ItemIsSelectable)
            self.tree.addTopLevelItem(header)
            header.setExpanded(False)
            for row in items:
                self.add_row(row, parent_item=header)

        # Add rows that didn't match the regex as top-level items
        for row in unmatched:
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
            manager = ProjectManager()
            self.add_actions(menu, actions, data=manager.get_current_element())

        # Show menu at the global position
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def set_thumbnail_size(self, size_multiplier: int):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self._set_thumbnail_size_recursive(item, size_multiplier)

    def _set_thumbnail_size_recursive(self, item: QTreeWidgetItem, size_multiplier: int) -> None:
        row: Row | None = self.tree.itemWidget(item, 0)

        if row:
            row.thumbnail.set_size_multiplier(size_multiplier)

        # Check children
        for i in range(item.childCount()):
            self._set_thumbnail_size_recursive(item.child(i), size_multiplier)


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
