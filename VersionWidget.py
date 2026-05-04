from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

class VersionWidget(QWidget):
    def __init__(self, current_version, latest_version, parent=None):
        super().__init__(parent)

        self.label_link = QLabel('<a href="https://github.com/johannes-ed/rocket-league-session-tracker">GitHub link</a>')
        self.label_link.setStyleSheet("color: #A0A0A0; font-size: 8pt;")
        self.label_link.setOpenExternalLinks(True)
        
        self.label_current = QLabel(f"Current: {current_version}")
        self.label_current.setStyleSheet("color: #A0A0A0; font-size: 8pt;")

        self.label_latest = QLabel(f"Latest: {latest_version}")
        self.label_latest.setStyleSheet("color: #A0A0A0; font-size: 8pt;")

        layout = QVBoxLayout()
        layout.addWidget(self.label_link)
        layout.addWidget(self.label_current)
        layout.addWidget(self.label_latest)
        self.setLayout(layout)
