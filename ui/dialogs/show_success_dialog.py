# ui/dialogs/show_success_dialog.py
import os
import sys
import subprocess
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

def show_success_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("✅ Conversion Completed")
    dialog.resize(400, 300)

    layout = QVBoxLayout()

    title = QLabel("The conversion was completed successfully!")
    title.setStyleSheet("font-weight: bold; font-size: 14px; color: #006600;")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    layout.addWidget(QLabel("Generated files:"))

    list_widget = QListWidget()
    output_dir = "output"
    if os.path.exists(output_dir):
        for file in sorted(os.listdir(output_dir)):
            list_widget.addItem(file)
    else:
        list_widget.addItem("(No output folder)")
    layout.addWidget(list_widget)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    
    open_btn = QPushButton("📁 Open Output Folder")

    def open_folder():
        path = os.path.abspath(output_dir)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

    open_btn.clicked.connect(open_folder)
    btn_layout.addWidget(open_btn)
    
    close_btn = QPushButton("Close")
    close_btn.setDefault(True)
    close_btn.clicked.connect(dialog.accept)
    btn_layout.addWidget(close_btn)

    layout.addLayout(btn_layout)

    dialog.setLayout(layout)
    dialog.exec()
