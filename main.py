import sys

from PySide6.QtWidgets import QApplication

from JSONObjectTCPReader import JSONObjectTCPReader
from RLSessionTracker import RLSessionTracker
from MainWindow import MainWindow

def main():
    app = QApplication(sys.argv)

    # this is not a great method to force dark background and white text but it works
    app.setStyleSheet("""
        QWidget {
            background-color: #252525;
            color: white;
        }
    """)
    
    tcp = JSONObjectTCPReader()
    rl_tracker = RLSessionTracker()
    window = MainWindow()

    tcp.message_received.connect(rl_tracker.handle_message)
    
    tcp.tcp_stream_connected.connect(window.status_widget.update_connection_status)
    rl_tracker.session_stats_updated.connect(window.tracker_widget.update_tracker_stats)
    
    tcp.start()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
