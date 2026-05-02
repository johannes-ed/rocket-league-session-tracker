import sys

from PySide6.QtWidgets import QApplication

from JSONObjectTCPReader import JSONObjectTCPReader
from RLSessionTracker import RLSessionTracker
from TrackerWidget import TrackerWidget

def main():
    app = QApplication(sys.argv)
    
    tcp = JSONObjectTCPReader()
    rl_tracker = RLSessionTracker()
    window = TrackerWidget()

    tcp.message_received.connect(rl_tracker.handle_message)
    
    tcp.tcp_stream_connected.connect(window.update_connection_status)
    rl_tracker.current_playlist_updated.connect(window.update_current_playlist)
    rl_tracker.session_stats_updated.connect(window.update_tracker_stats)
    
    tcp.start()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
