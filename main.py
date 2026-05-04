import sys
import requests

from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow

app_version = 'v1.0.0'

def get_latest_version():
    try:
        url = "https://api.github.com/repos/johannes-ed/rocket-league-session-tracker/releases/latest"
        response = requests.get(url, timeout=0.5)
        response.raise_for_status()
        data = response.json()
        latest_version = data["tag_name"]
        return latest_version
    except:
        return '-'

def main():
    app = QApplication(sys.argv)

    # this is not a great method to force dark background and white text but it works
    app.setStyleSheet("""
        QWidget {
            background-color: #252525;
            color: white;
        }
    """)
    
    window = MainWindow(app_version, get_latest_version())
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
