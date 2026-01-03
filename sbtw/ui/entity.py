from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QLineEdit, QTreeWidgetItem, QWidget

from sbtw.ui.view import View

if TYPE_CHECKING:
    from sbtw.ui.row import Row


class EntitiesView(View):
    def __init__(
        self,
        rows: list[dict] | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(rows=rows, actions=actions, parent=parent)
        main_layout = self.layout()

        # ---------- Search bar ----------
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search…")
        self.search_bar.setContentsMargins(10, 10, 10, 10)
        main_layout.insertWidget(0, self.search_bar)

        # ---------- Connections ----------
        self.search_bar.textChanged.connect(self._filter_items)

    def _filter_items(self, text: str) -> None:
        text = text.lower()

        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self._filter_item_recursive(item, text)

    def _filter_item_recursive(self, item: QTreeWidgetItem, text: str) -> bool:
        row: Row | None = self.tree.itemWidget(item, 0)

        # Match this item
        match = text in row.name.lower() if row else False

        # Check children
        child_match = False
        for i in range(item.childCount()):
            if self._filter_item_recursive(item.child(i), text):
                child_match = True

        visible = match or child_match
        item.setHidden(not visible)

        # Expand parents when matching
        if visible and text:
            item.setExpanded(True)

        return visible


class AssetsView(EntitiesView):
    def __init__(
        self,
        rows: list[dict] | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(rows=rows, actions=actions, parent=parent)


class ShotsView(EntitiesView):
    def __init__(
        self,
        rows: list[dict] | None = None,
        actions: dict | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(rows=rows, actions=actions, parent=parent)


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

    view = EntitiesView(rows=_data)
    view.show()

    sys.exit(app.exec())
