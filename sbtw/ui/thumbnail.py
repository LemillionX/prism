from __future__ import annotations

from qtpy.QtCore import QEvent, QRect, Qt
from qtpy.QtGui import QCursor, QImage, QPixmap
from qtpy.QtWidgets import QDialog, QHBoxLayout, QLabel, QWidget


class Thumbnail(QLabel):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Thumbnail")
        self.setMouseTracking(True)
        self._image = None
        self.images = None

        self.popup = QDialog(self, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.popup.setAttribute(Qt.WA_TranslucentBackground)
        self.popup.setLayout(QHBoxLayout())
        self.popup_image = QLabel(self.popup)
        self.popup.layout().addWidget(self.popup_image)

    def set_image(self, pixmap: QPixmap | QImage):
        self._image = pixmap
        self.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
        size = min(max(pixmap.width(), pixmap.height()), 256)
        self.popup_image.setPixmap(
            pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def set_filmstrip(self, pixmap: QPixmap):
        self._filmstrip = pixmap
        image_w = self._image.width()
        image_h = self._image.height()
        film_w = self._filmstrip.width()
        film_h = self._filmstrip.height()

        width = image_w / round(image_h / film_h)
        image_count = int(film_w / width)

        self.images = []
        for i in range(image_count):
            rect = QRect(width * i, 0, width, image_h)
            self.images.append(self._filmstrip.copy(rect))
        self.popup_image.setPixmap(self.images[0])
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


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    thumbnail = Thumbnail()
    thumbnail.set_image(QPixmap(r"E:\Sammy\Clem.png"))
    thumbnail.show()

    sys.exit(app.exec())
