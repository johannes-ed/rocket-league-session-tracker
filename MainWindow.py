import os, sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon

from TrackerWidget import TrackerWidget
from StatusWidget import StatusWidget
from VersionWidget import VersionWidget

from JSONObjectTCPReader import JSONObjectTCPReader
from RLSessionTracker import RLSessionTracker

class MainWindow(QMainWindow):
    def __init__(self, current_version, latest_version):
        super().__init__()

        self.green = "#30C230"
        self.red = '#E60000'



        self.setWindowTitle("RLSessionTracker")
        self.setFixedSize(260, 130)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        def resource_path(filename):
            base = getattr(sys, "_MEIPASS", os.path.abspath("."))
            return os.path.join(base, filename)

        self.setWindowIcon(QIcon(resource_path("window_icon.png")))



        container = QWidget()
        main_layout = QHBoxLayout(container)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.tcp = JSONObjectTCPReader(self)
        self.rl_tracker = RLSessionTracker(self)

        self.version_widget = VersionWidget(current_version, latest_version, parent=container)
        self.tracker_widget = TrackerWidget(self.green, self.red, parent=container)
        self.button_widget = QPushButton("Next Playlist", parent=container)
        self.button_widget.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                border-radius: 4px;
                padding: 6px 10px;
            }
            QPushButton:pressed {
                background-color: #575757;
                padding-left: 8px;
                padding-top: 8px;
            }
        """)
        self.status_widget = StatusWidget(self.green, self.red, parent=container)
        
        self.tcp.message_received.connect(self.rl_tracker.handle_message)
        self.rl_tracker.session_stats_updated.connect(self.tracker_widget.update_tracker_stats)
        self.button_widget.clicked.connect(self.tracker_widget.button_toggle_playlist)
        self.tcp.tcp_stream_connected.connect(self.status_widget.update_connection_status)
        
        self.tcp.start()



        self.setCentralWidget(container)

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        main_layout.addLayout(left_layout)
        main_layout.addStretch()
        main_layout.addLayout(right_layout)

        left_layout.addWidget(self.tracker_widget)

        right_layout.setSpacing(1)
        right_layout.addWidget(self.status_widget, alignment=Qt.AlignRight)
        right_layout.addStretch()
        right_layout.addWidget(self.version_widget, alignment=Qt.AlignRight)
        right_layout.addStretch()
        right_layout.addWidget(self.button_widget, alignment=Qt.AlignRight)
