import sys
from pathlib import Path

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor, QPixmap
from qtpy.QtWidgets import QApplication, QSplashScreen

from sbtw._version import __version__
from sbtw.core.constant import SPLASH_SCREEN
from sbtw.core.log import NAME, logger
from sbtw.ui.ui import MainWindow


def launch():
    logger.info("Launching %s v%s ...", NAME, __version__)
    app = QApplication(sys.argv)

    # Load dark stylesheet if available
    qss_path = Path(__file__).parent / "style" / "dark.qss"
    try:
        if qss_path.exists():
            app.setStyleSheet(qss_path.read_text(encoding="utf8"))
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Could not load stylesheet %s: %s", qss_path.as_posix(), e)

    # ------------- Splash Screen -------------
    splash_pix = QPixmap(SPLASH_SCREEN).scaled(
        720,
        720,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation,
    )
    splash = QSplashScreen(splash_pix)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    splash.show()
    splash.showMessage(
        f"Launching {NAME} v{__version__} ...", alignment=Qt.AlignBottom | Qt.AlignCenter, color=QColor("white")
    )
    app.processEvents()  # ← CRITICAL (forces immediate paint)

    # ------------- App -------------
    ui = MainWindow()
    splash.finish(ui)
    ui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
