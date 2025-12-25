from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from sbtw.ui.browser import Browser
from sbtw.ui.header import Header


class MainWindow(QMainWindow):
    def __init__(self, data: dict):
        super().__init__()
        # Default Settings
        self.setWindowTitle("SBTW")
        self.setMinimumSize(800, 500)
        self.resize(1200,500)

        # ------------- Layout -------------
        widget = QWidget(self)
        self.setCentralWidget(widget)

        main_layout = QVBoxLayout(widget)

        # ------------- Header -------------
        header = Header(name="Larsene", parent=self)
        main_layout.addWidget(header, stretch=1)

        # ------------- Browser -------------
        browser = Browser(data=data, parent=self)
        main_layout.addWidget(browser, stretch=19)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    _data = [
        {
            "name": f"Clementine{i:02d}",
            "thumbnail": r"E:\Sammy\Clem.png",
            "tasks": [
                {
                    "name": task,
                    "path": Path(f"Clementine{i:02d}", task).as_posix(),
                    "files": [
                        {
                            "name": f"Clementine{i:02d}_{task}_v{idx:03d}",
                        }
                        for idx in range(32, 0, -1)
                    ],
                }
                for task in ["Design", "Modeling", "Texture", "Rig"]
            ],
        }
        for i in range(20)
    ]

    ui = MainWindow(data=_data)
    ui.show()

    sys.exit(app.exec())
