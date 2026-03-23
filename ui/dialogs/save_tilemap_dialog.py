# ui/dialogs/save_tilemap_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
)


class SaveTilemapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Tilemap")
        self.setModal(True)
        self.setFixedSize(260, 130)

        current_bpp = getattr(parent, 'current_bpp', 4) if parent else 4

        layout = QVBoxLayout(self)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Text Mode")
        self.mode_combo.setEnabled(False)
        mode_row.addWidget(self.mode_combo)
        layout.addLayout(mode_row)

        bpp_row = QHBoxLayout()
        bpp_row.addWidget(QLabel("Bit Depth:"))
        self.bpp_combo = QComboBox()
        self.bpp_combo.addItems(["4bpp", "8bpp"])
        if current_bpp == 8:
            self.bpp_combo.setCurrentIndex(1)
            self.bpp_combo.setEnabled(False)
        else:
            self.bpp_combo.setCurrentIndex(0)
        bpp_row.addWidget(self.bpp_combo)
        layout.addLayout(bpp_row)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def get_values(self):
        bpp = 4 if self.bpp_combo.currentIndex() == 0 else 8
        return bpp
