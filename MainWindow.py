import os, sys

from PySide6.QtWidgets import QMainWindow, QPushButton
from PySide6.QtGui import QIcon

from TrackerWidget import TrackerWidget
from StatusWidget import StatusWidget

from JSONObjectTCPReader import JSONObjectTCPReader
from RLSessionTracker import RLSessionTracker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.green = "#30C230"
        self.red = '#E60000'

        self.setWindowTitle("RLSessionTracker")
        self.setFixedSize(300, 150)

        import os, sys

        def resource_path(filename):
            base = getattr(sys, "_MEIPASS", os.path.abspath("."))
            return os.path.join(base, filename)

        self.setWindowIcon(QIcon(resource_path("window_icon.png")))

        tcp = JSONObjectTCPReader(self)
        rl_tracker = RLSessionTracker(self)
        
        self.tracker_widget = TrackerWidget(self)
        self.button_widget = QPushButton("Toggle Playlist", self)
        self.status_widget = StatusWidget(self)
        
        tcp.message_received.connect(rl_tracker.handle_message)
        rl_tracker.session_stats_updated.connect(self.tracker_widget.update_tracker_stats)
        self.button_widget.clicked.connect(self.tracker_widget.button_toggle_playlist)
        tcp.tcp_stream_connected.connect(self.status_widget.update_connection_status)
        
        tcp.start()



        self.button_widget.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                border-radius: 4px;
                padding: 6px 10px;
            }
            QPushButton:pressed {
                background-color: #686868;
                padding-left: 8px;
                padding-top: 8px;
            }
        """)

        self.setCentralWidget(self.tracker_widget)
        self._position_button()
        self._position_dot()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        self._position_button()
        self._position_dot()

    def _position_dot(self):
        margin = 8
        x = self.width() - self.status_widget.width() - margin
        y = margin
        self.status_widget.move(x, y)

    def _position_button(self):
        margin = 8
        x = self.width() - self.button_widget.width() - margin
        y = self.height() - self.button_widget.height() - margin
        self.button_widget.move(x, y)
