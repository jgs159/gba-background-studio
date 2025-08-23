# ui/custom_status_bar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class CustomStatusBar(QWidget):
    """Custom status bar widget that displays at the bottom of the main window"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(20)
        self.setStyleSheet("background: #f0f0f0; border-top: 1px solid #ccc;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #333; font-size: 11px;")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        
    def show_message(self, message):
        self.status_label.setText(message)
