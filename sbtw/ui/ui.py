from qtpy.QtWidgets import QMainWindow, QTabWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Default Settings
        self.setWindowTitle("SBTW")
        self.setMinimumSize(500, 500)

        # Creating Main Widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()

    sys.exit(app.exec())
