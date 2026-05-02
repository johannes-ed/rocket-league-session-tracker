from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

class TrackerWidget(QWidget):
    """Qt window that displays the current RL session statistics in a (hopefully) nice way."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rocket League Session Tracker")
        self.setMinimumWidth(350)

        self.label_connected = QLabel("Connected to game API: -")
        self.label_playlist = QLabel("Current playlist: -")
        self.label_wins = QLabel("Wins: -")
        self.label_losses = QLabel("Losses: -")

        layout = QVBoxLayout()
        layout.addWidget(self.label_connected)
        layout.addWidget(self.label_playlist)
        layout.addWidget(self.label_wins)
        layout.addWidget(self.label_losses)
        self.setLayout(layout)

        self.connected = False
        self.current_playlist = '-'
        self.session_stats = None

    def update_connection_status(self, connected: bool):
        self.connected = connected
        self.update_ui()

    def update_current_playlist(self, playlist: str):
        self.current_playlist = playlist
        self.update_ui()

    def update_tracker_stats(self, data: dict):
        self.session_stats = data
        self.update_ui()

    def update_ui(self):
        self.label_connected.setText(f"Connected to game API: {self.connected}")
        self.label_playlist.setText(f"Current playlist: {self.current_playlist}")
        
        if self.session_stats != None:
            playlist_stats = self.session_stats.get(self.current_playlist)
            
            self.label_wins.setText(f"Wins: {playlist_stats.get('Wins')}")
            self.label_losses.setText(f"Losses: {playlist_stats.get('Losses')}")
