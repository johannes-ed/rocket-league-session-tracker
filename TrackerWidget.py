from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

class TrackerWidget(QWidget):
    """Qt window that displays the current RL session statistics in a (hopefully) nice way."""

    def __init__(self, green, red, parent=None):
        super().__init__(parent)

        self.green = green
        self.red = red

        self.indent = 15

        self.label_playlist = QLabel("Stats will show after\nfirst match")
        self.label_playlist.setStyleSheet("margin: 0px; padding: 0px; font-size: 12pt;")

        self.label_wins = QLabel("Wins: -")
        self.label_wins.setStyleSheet(f"color: {green}; font-size: 11pt;")
        self.label_wins.setIndent(self.indent)

        self.label_losses = QLabel("Losses: -")
        self.label_losses.setStyleSheet(f"color: {red}; font-size: 11pt;")
        self.label_losses.setIndent(self.indent)

        self.label_streak = QLabel("Streak: -")
        self.label_streak.setStyleSheet(f"color: {green}; font-size: 11pt;")
        self.label_streak.setIndent(self.indent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(self.label_playlist)
        layout.addStretch()
        layout.addWidget(self.label_wins)
        layout.addStretch()
        layout.addWidget(self.label_losses)
        layout.addStretch()
        layout.addWidget(self.label_streak)
        self.setLayout(layout)

        self.current_playlist = '-'
        self.session_stats = None



    def button_toggle_playlist(self):
        if self.current_playlist != '-' and self.session_stats != None:
            keys = list(self.session_stats.keys())

            idx = keys.index(self.current_playlist)
            next_key = keys[(idx + 1) % len(keys)]

            self.update_tracker_stats(next_key, self.session_stats)

    def update_tracker_stats(self, playlist: str, data: dict):
        self.current_playlist = playlist
        self.session_stats = data
        self.update_ui(playlist, data)

    def update_ui(self, playlist: str, session_stats: dict):
        self.label_playlist.setText(f"Stats: {playlist}")
        
        playlist_stats = session_stats.get(playlist)
        
        self.label_wins.setText(f"Wins: {playlist_stats.get('Wins')}")
        self.label_losses.setText(f"Losses: {playlist_stats.get('Losses')}")
        self._update_streak_label(playlist_stats)

    def _update_streak_label(self, stats):
        streak = stats.get('Streak')
        if streak >= 0: 
            text = f'+{streak}'
            color = self.green
        else: 
            text = f'{streak}'
            color = self.red
        self.label_streak.setStyleSheet(f"color: {color}; font-size: 11pt;")
        self.label_streak.setText(f"Streak: {text}")
