# main.py
import os
os.environ['JOBLIB_WORKER_COUNT'] = '4'
os.environ['JOBLIB_MULTIPROCESSING'] = '0'
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import GBABackgroundStudio


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    app = QApplication(sys.argv)
    window = GBABackgroundStudio()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
