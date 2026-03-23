# ui/custom_status_bar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class CustomStatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setStyleSheet("""
            background: #f0f0f0; 
            border-top: 1px solid #ccc;
            font-size: 11px;
            color: #333;
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(12)
        
        self.selection_label = QLabel("Tile Selected: 0")
        self.tilemap_label = QLabel("Tilemap: (0, 0)")
        self.tile_label = QLabel("Tile: 0")
        self.palette_label = QLabel("Palette: 0")
        self.flip_label = QLabel("Flip: None")
        self.zoom_label = QLabel("Zoom: 100%")
        
        layout.addWidget(self.selection_label)
        layout.addWidget(self.tilemap_label)
        layout.addWidget(self.tile_label)
        layout.addWidget(self.palette_label)
        layout.addWidget(self.flip_label)
        layout.addWidget(self.zoom_label)
        layout.addStretch()
        
    def update_status(self, selection_type="Tile", selection_id="-", tilemap_pos=(-1, -1), 
                     tile_id="-", palette_id="-", flip_state="None", zoom_level=100):
        self.selection_label.setText(f"{selection_type} Selected: {selection_id}")
        
        tilemap_display = f"({tilemap_pos[0]}, {tilemap_pos[1]})" if tilemap_pos != (-1, -1) else "(-, -)"
        self.tilemap_label.setText(f"Tilemap: {tilemap_display}")
        
        self.tile_label.setText(f"Tile: {tile_id}")
        self.palette_label.setText(f"Palette: {palette_id}")
        self.flip_label.setText(f"Flip: {flip_state}")
        self.zoom_label.setText(f"Zoom: {zoom_level}%")

    def update_selection_status(self, x1, y1, x2, y2, zoom_level=None):
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        self.selection_label.setText(f"Origin: ({x1}, {y1})")
        self.tilemap_label.setText(f"End: ({x2}, {y2})")
        self.tile_label.setText(f"Width: {w} tiles")
        self.palette_label.setText(f"Height: {h} tiles")
        self.flip_label.setText(f"Size: {w*8}×{h*8} px")
        if zoom_level is not None:
            self.zoom_label.setText(f"Zoom: {zoom_level}%")

    def restore_default_status(self, zoom_level=100):
        self.selection_label.setText("Tile Selected: -")
        self.tilemap_label.setText("Tilemap: (-, -)")
        self.tile_label.setText("Tile: -")
        self.palette_label.setText("Palette: -")
        self.flip_label.setText("Flip: None")
        self.zoom_label.setText(f"Zoom: {zoom_level}%")
