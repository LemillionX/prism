from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QWidget

from sbtw.ui.label import ProjectsLabel, RefreshLabel, UserLabel


class Header(QWidget):
    def __init__(self, name: str, parent: QWidget | None = None):
        super().__init__(parent=parent)
        # ------------- Variables -------------
        self.name = name

        # ------------- Layout -------------
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(30)

        # ------------- User -------------
        main_layout.addStretch()
        user_label = UserLabel(name=self.name, parent=self)
        main_layout.addWidget(user_label, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Projects -------------
        projects_label = ProjectsLabel(parent=self)
        main_layout.addWidget(projects_label, alignment=Qt.AlignmentFlag.AlignRight)
        # ------------- Projects -------------
        refresh_icon = RefreshLabel()
        main_layout.addWidget(refresh_icon, alignment=Qt.AlignmentFlag.AlignRight)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    view = Header(name="Larsene")
    view.show()

    sys.exit(app.exec())
