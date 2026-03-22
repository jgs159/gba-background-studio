# ui/dialogs/open_tilemap_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton
)


def _get_possible_dimensions(total_tiles):
    priority_w = [20, 32, 64]
    priority = []
    others = []

    for w in range(1, total_tiles + 1):
        if total_tiles % w == 0:
            h = total_tiles // w
            if 1 <= h <= 512:
                if w == 20 or w == 32:
                    priority.append((w, h))
                elif w == 64 and h % 32 == 0:
                    priority.append((w, h))
                elif w < 32 and w != 20:
                    others.append((w, h))

    order = {20: 0, 32: 1, 64: 2}
    priority.sort(key=lambda p: (order.get(p[0], 99), p[1]))
    others.sort(key=lambda p: p[0])

    return priority + others


class OpenTilemapDialog(QDialog):
    def __init__(self, total_tiles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Tilemap")
        self.setModal(True)
        self.setFixedSize(280, 160)

        layout = QVBoxLayout(self)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Text Mode")
        self.mode_combo.setEnabled(False)
        mode_row.addWidget(self.mode_combo)
        layout.addLayout(mode_row)

        current_bpp = getattr(parent, 'current_bpp', 4) if parent else 4
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

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size (tiles):"))
        self.size_combo = QComboBox()
        self._dims = _get_possible_dimensions(total_tiles)
        if self._dims:
            for w, h in self._dims:
                self.size_combo.addItem(f"{w} × {h}  ({w*8}×{h*8} px)", (w, h))
        else:
            self.size_combo.addItem(f"{total_tiles} × 1", (total_tiles, 1))
        size_row.addWidget(self.size_combo)
        layout.addLayout(size_row)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("Open")
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
        w, h = self.size_combo.currentData()
        return w, h, bpp
