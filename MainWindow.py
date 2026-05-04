from PySide6.QtWidgets import QMainWindow

from TrackerWidget import TrackerWidget
from StatusWidget import StatusWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.green = "#30C230"
        self.red = '#E60000'

        self.setWindowTitle("RLSessionTracker")
        self.setFixedSize(300, 150)

        self.tracker_widget = TrackerWidget(self)
        self.setCentralWidget(self.tracker_widget)

        self.status_widget = StatusWidget(self)
        self._position_dot()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        self._position_dot()

    def _position_dot(self):
        margin = 8
        x = self.width() - self.status_widget.width() - margin
        y = margin
        self.status_widget.move(x, y)
