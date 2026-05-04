import sys

from PySide6.QtWidgets import QApplication

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
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
