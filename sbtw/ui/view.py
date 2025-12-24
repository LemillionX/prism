from __future__ import annotations

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

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

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        # Get associated Row
        if (row := self.tree.itemWidget(item, 0)) and isinstance(row, Row):
            self.row_selected.emit(row.data)


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
