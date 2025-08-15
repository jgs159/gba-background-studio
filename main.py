# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import GBABackgroundStudio


def main():
    app = QApplication(sys.argv)
    window = GBABackgroundStudio(language="english")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()