from __future__ import annotations

from qtpy.QtCore import QEvent, QRect, Qt, Signal
from qtpy.QtGui import QCursor, QImage, QPixmap
from qtpy.QtWidgets import QDialog, QHBoxLayout, QLabel, QWidget


class Thumbnail(QLabel):
    size_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Thumbnail")
        self.setMouseTracking(True)
        self._image = None
        self.images = None
        self._filmstrip = None
        self.size_multiplier = 1

        self.popup = QDialog(self, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.popup.setAttribute(Qt.WA_TranslucentBackground)
        self.popup.setLayout(QHBoxLayout())
        self.popup_image = QLabel(self.popup)
        self.popup.layout().addWidget(self.popup_image)

    def set_image(self, pixmap: QPixmap | QImage):
        # Normalize to QPixmap
        if isinstance(pixmap, QImage):
            pixmap = QPixmap.fromImage(pixmap)

        self._image = pixmap
        base = int(50 * max(1, self.size_multiplier))
        self.setPixmap(pixmap.scaled(base, base, Qt.KeepAspectRatio))
        max_side = max(pixmap.width(), pixmap.height())
        size = int(min(max_side * max(1, self.size_multiplier), 256 * max(1, self.size_multiplier)))
        self.popup_image.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Notify listeners that the displayed thumbnail size changed
        self.adjustSize()
        try:
            height = self.size().height()
        except Exception:  # noqa: BLE001
            height = base
        self.size_changed.emit(int(height))

    def set_filmstrip(self, pixmap: QPixmap):
        self._filmstrip = pixmap
        if not self._image:
            return

        image_w = int(self._image.width())
        image_h = int(self._image.height())
        film_w = int(self._filmstrip.width())
        film_h = int(self._filmstrip.height())

        # Avoid division by zero; compute per-frame width as integer
        divisor = max(1, round(image_h / film_h))
        frame_width = max(1, int(image_w / divisor))
        image_count = int(film_w / frame_width) if frame_width > 0 else 0

        self.images = []
        for i in range(image_count):
            rect = QRect(int(frame_width * i), 0, frame_width, image_h)
            self.images.append(self._filmstrip.copy(rect))

        if self.images:
            # scale preview according to multiplier
            preview = self.images[0]
            if self.size_multiplier != 1:
                preview = preview.scaled(
                    int(preview.width() * self.size_multiplier),
                    int(preview.height() * self.size_multiplier),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            self.popup_image.setPixmap(preview)
            self.popup_image.adjustSize()

    def mouseMoveEvent(self, event: QEvent):
        if not self.images:
            return
        frame_count = len(self.images)
        index = int(event.pos().x() // (self.size().width() / frame_count))
        if index in range(len(self.images)):
            self.popup_image.setPixmap(self.images[index])

    def enterEvent(self, event: QEvent):
        if self._image:
            self.show_full_image()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        if self.popup:
            self.popup.close()
        super().leaveEvent(event)

    def show_full_image(self):
        self.popup.move(QCursor.pos())
        self.popup.show()

    def set_size_multiplier(self, size_multiplier: int):
        # Update multiplier and rescale current pixmap(s)
        self.size_multiplier = max(1, int(size_multiplier))
        self.resize(50 * self.size_multiplier, 50 * self.size_multiplier)
        if self._image:
            self.set_image(self._image)
        if getattr(self, "_filmstrip", None):
            self.set_filmstrip(self._filmstrip)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    thumbnail = Thumbnail()
    thumbnail.set_image(QPixmap(r"E:\Sammy\Clem.png"))
    thumbnail.show()

    sys.exit(app.exec())
