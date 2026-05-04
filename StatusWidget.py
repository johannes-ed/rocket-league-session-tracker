from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QPainter, QColor

class StatusWidget(QWidget):
    def __init__(self, green, red, parent=None):
        super().__init__(parent)

        self.green = green
        self.red = red

        self._color = QColor(red)
        self._diameter = 12
        self._text = "Connection:"

        self._padding = 6
        self._text_width = 65

        total_width = self._text_width + self._padding + self._diameter
        total_height = max(self._diameter, 16)

        self.setFixedSize(QSize(total_width, total_height))
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.connected = False

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # connection text
        text_rect = QRect(0, 0, self._text_width, self.height())
        painter.setPen(QColor(160, 160, 160))  # light gray pen to draw text
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self._text)

        # circle icon
        x = self._text_width + self._padding
        y = (self.height() - self._diameter) // 2 + 1.5

        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(x, y, self._diameter, self._diameter)

    def update_connection_status(self, connected: bool):
        self.connected = connected
        self.set_color(self.green if connected else self.red)
