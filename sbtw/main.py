import sys

from qtpy.QtWidgets import QApplication

from sbtw._version import __version__
from sbtw.core.log import NAME, logger
from sbtw.ui.ui import MainWindow


def launch():
    logger.info("Launching %s v%s ...", NAME, __version__)
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
