# ui/custom_status_bar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class CustomStatusBar(QWidget):
    """Custom status bar widget that displays at the bottom of the main window"""
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
        
        # Campos de información
        self.selection_label = QLabel("Tile Selected: 0")
        self.tilemap_label = QLabel("Tilemap: (0, 0)")
        self.tile_label = QLabel("Tile: 0")
        self.palette_label = QLabel("Palette: 0")
        self.flip_label = QLabel("Flip: None")
        self.zoom_label = QLabel("Zoom: 100%")
        
        # Añadir todos los labels al layout
        layout.addWidget(self.selection_label)
        layout.addWidget(self.tilemap_label)
        layout.addWidget(self.tile_label)
        layout.addWidget(self.palette_label)
        layout.addWidget(self.flip_label)
        layout.addWidget(self.zoom_label)
        layout.addStretch()
        
    def update_status(self, selection_type="Tile", selection_id=0, tilemap_pos=(0, 0), 
                     tile_id=0, palette_id=0, flip_state="None", zoom_level=100):
        """Actualiza toda la información de la status bar"""
        # Convertir palette_id a hexadecimal
        palette_hex = f"{palette_id:X}"  # Convierte a hexadecimal en mayúsculas
        
        # Convertir selection_id a hexadecimal si es una paleta
        if selection_type == "Palette":
            selection_display = f"{selection_id:X}"  # Hexadecimal para paletas
        else:
            selection_display = str(selection_id)    # Decimal para tiles
        
        self.selection_label.setText(f"{selection_type} Selected: {selection_display}")
        self.tilemap_label.setText(f"Tilemap: ({tilemap_pos[0]}, {tilemap_pos[1]})")
        self.tile_label.setText(f"Tile: {tile_id}")
        self.palette_label.setText(f"Palette: {palette_hex}")
        self.flip_label.setText(f"Flip: {flip_state}")
        self.zoom_label.setText(f"Zoom: {zoom_level}%")
