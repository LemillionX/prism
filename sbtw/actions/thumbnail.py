from __future__ import annotations

import contextlib
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from qtpy.QtCore import QDir, QEventLoop, QPoint, QRect, Qt, Signal
from qtpy.QtGui import QColor, QGuiApplication, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPen
from qtpy.QtWidgets import QApplication, QFileDialog, QWidget

from sbtw.actions.base import ActionBase
from sbtw.core.log import logger
from sbtw.core.project import Project


class SetThumbnail(ActionBase):
    @staticmethod
    def name() -> str:
        return "Set Thumbnail"

    def get_thumbnail(self) -> Path | None:
        return QFileDialog.getOpenFileName(
            None,
            "Select Image to use as thumbnail",
            QDir.rootPath(),
            "Images (*.png *.xpm *.jpg)",
        )[0]

    def _execute(self, **kwargs: Any) -> None:
        path = Path(kwargs.get("path"))
        project = Project(path=path)
        dest = project.get_thumbnail_path(path)
        if src := self.get_thumbnail():
            # Copy thumbnail for project's element
            shutil.copy2(src, dest)

        # For project itself, need to update the config file
        if dest.parent.stem == ".project":
            project.save(thumbnail=dest.as_posix())

    def post_run(self, **kwargs: Any):
        if (view := (kwargs.get("view"))) and hasattr(view, "updated"):
            path = Path(kwargs.get("path"))
            if path.is_dir():
                path = path.parent.parent
            view.updated.emit(view, path)


def take_screenshot_area(output: Path) -> None:
    output = output.with_suffix(".png")
    system = platform.system()

    if system == "Windows":
        _screenshot_area_windows(output)
    elif system == "Darwin":
        _screenshot_area_macos(output)
    elif system == "Linux":
        _screenshot_area_linux(output)
    else:
        raise RuntimeError("Unsupported OS: %s", system)  # noqa: TRY003


def _screenshot_area_windows(output: Path) -> None:
    app = QApplication.instance()
    owns_app = app is None

    if owns_app:
        app = QApplication([])

    loop = QEventLoop()
    result: Path | None = None

    def _done() -> Path | None:
        nonlocal result
        result = overlay.output
        loop.quit()

    def _cancel() -> Path | None:
        nonlocal result
        result = None
        with contextlib.suppress(PermissionError):
            overlay.output.unlink(missing_ok=True)
        loop.quit()

    overlay = ScreenshotOverlay(output)
    overlay.finished.connect(_done)
    overlay.cancelled.connect(_cancel)
    overlay.show()

    loop.exec()

    if owns_app:
        app.quit()

    if not result:
        logger.warning("Screenshot cancelled")


def _screenshot_area_macos(output: Path) -> None:
    subprocess.run(
        ["screencapture", "-i", str(output)],  # noqa: S607
        check=True,
    )


def _screenshot_area_linux(output: Path) -> None:
    if subprocess.run(["which", "gnome-screenshot"], capture_output=True, check=False).returncode == 0:  # noqa: S607
        subprocess.run(
            ["gnome-screenshot", "-a", "-f", str(output)],  # noqa: S607
            check=True,
        )
    elif subprocess.run(["which", "scrot"], capture_output=True, check=False).returncode == 0:  # noqa: S607
        subprocess.run(
            ["scrot", "-s", str(output)],  # noqa: S607
            check=True,
        )
    else:
        raise RuntimeError("No screenshot tool found (install gnome-screenshot or scrot)")  # noqa: TRY003


class ScreenshotOverlay(QWidget):
    finished = Signal()
    cancelled = Signal()

    def __init__(self, output: Path):
        super().__init__()

        self.output = output.with_suffix(".png")
        self.start: QPoint | None = None
        self.end: QPoint | None = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        self.showFullScreen()

    def mousePressEvent(self, event: QMouseEvent):
        self.start = event.position().toPoint()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.end = event.position().toPoint()
        self.capture()
        self.finished.emit()
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent):  # noqa: ARG002
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.start and self.end:
            rect = QRect(self.start, self.end).normalized()

            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)

            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(rect)

    def capture(self):
        if not self.start or not self.end:
            return

        rect = QRect(self.start, self.end).normalized()
        screen = QGuiApplication.screenAt(rect.center())
        if not screen:
            return

        dpr = screen.devicePixelRatio()

        pixmap = screen.grabWindow(
            0,
            int(rect.x() * dpr),
            int(rect.y() * dpr),
            int(rect.width() * dpr),
            int(rect.height() * dpr),
        )
        pixmap.save(str(self.output))


class CaptureThumbnail(SetThumbnail):
    @staticmethod
    def name() -> str:
        return "Capture Thumbnail"

    def get_thumbnail(self) -> Path | None:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)  # noqa: SIM115
        output = Path(tmp.name)
        tmp.close()  # Close the file handle so it can be written to
        with contextlib.suppress(PermissionError):
            try:
                take_screenshot_area(output)
                if output.exists():
                    return output
            except Exception:  # noqa: BLE001
                # If something goes wrong, try to clean up
                output.unlink(missing_ok=True)

        return None
