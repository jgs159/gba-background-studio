# ui/edit_palettes_tab.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSplitter, 
                               QGraphicsView, QGraphicsScene)
from PySide6.QtGui import QFont, QPainter
from PySide6.QtCore import Qt


class EditPalettesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        edit_palettes_header = self.create_header("Edit Palettes")
        self.layout.addWidget(edit_palettes_header)
        
        # Edit Palettes splitter: Palettes (left) and Tilemap (right)
        edit_palettes_splitter = QSplitter(Qt.Horizontal)
        edit_palettes_splitter.setChildrenCollapsible(False)
        edit_palettes_splitter.setHandleWidth(6)
        
        # Palettes section
        palettes_container = QWidget()
        palettes_container_layout = QVBoxLayout(palettes_container)
        palettes_container_layout.setContentsMargins(4, 4, 4, 4)
        palettes_container_layout.setSpacing(4)
        
        palettes_label = QLabel("Palettes")
        palettes_label.setFont(QFont("Arial", 9, QFont.Bold))
        palettes_label.setAlignment(Qt.AlignCenter)
        palettes_container_layout.addWidget(palettes_label)
        
        self.edit_palettes_view = QGraphicsView()
        self.edit_palettes_scene = QGraphicsScene()
        self.edit_palettes_view.setScene(self.edit_palettes_scene)
        self.edit_palettes_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_palettes_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_palettes_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.edit_palettes_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        palettes_container_layout.addWidget(self.edit_palettes_view)
        
        edit_palettes_splitter.addWidget(palettes_container)
        
        # Tilemap section
        tilemap2_container = QWidget()
        tilemap2_container_layout = QVBoxLayout(tilemap2_container)
        tilemap2_container_layout.setContentsMargins(4, 4, 4, 4)
        tilemap2_container_layout.setSpacing(4)
        
        tilemap2_label = QLabel("Tilemap")
        tilemap2_label.setFont(QFont("Arial", 9, QFont.Bold))
        tilemap2_label.setAlignment(Qt.AlignCenter)
        tilemap2_container_layout.addWidget(tilemap2_label)
        
        self.edit_tilemap2_view = QGraphicsView()
        self.edit_tilemap2_scene = QGraphicsScene()
        self.edit_tilemap2_view.setScene(self.edit_tilemap2_scene)
        self.edit_tilemap2_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tilemap2_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tilemap2_view.setStyleSheet("QGraphicsView { background: #e0e0e0; border: 1px solid #ccc; }")
        self.edit_tilemap2_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tilemap2_container_layout.addWidget(self.edit_tilemap2_view)
        
        edit_palettes_splitter.addWidget(tilemap2_container)
        edit_palettes_splitter.setSizes([500, 500])
        
        self.layout.addWidget(edit_palettes_splitter)

    def create_header(self, text):
        header = QLabel(text)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        return header
