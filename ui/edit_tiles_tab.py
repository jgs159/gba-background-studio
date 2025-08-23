# ui/edit_tiles_tab.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSplitter, 
                               QGraphicsView, QGraphicsScene)
from PySide6.QtGui import QFont, QPainter
from PySide6.QtCore import Qt


class EditTilesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        edit_tiles_header = self.create_header("Edit Tiles")
        self.layout.addWidget(edit_tiles_header)
        
        # Edit Tiles splitter: Tileset (left) and Tilemap (right)
        edit_tiles_splitter = QSplitter(Qt.Horizontal)
        edit_tiles_splitter.setChildrenCollapsible(False)
        edit_tiles_splitter.setHandleWidth(6)
        
        # Tileset section
        tileset_container = QWidget()
        tileset_container_layout = QVBoxLayout(tileset_container)
        tileset_container_layout.setContentsMargins(4, 4, 4, 4)
        tileset_container_layout.setSpacing(4)
        
        tileset_label = QLabel("Tileset")
        tileset_label.setFont(QFont("Arial", 9, QFont.Bold))
        tileset_label.setAlignment(Qt.AlignCenter)
        tileset_container_layout.addWidget(tileset_label)
        
        self.edit_tileset_view = QGraphicsView()
        self.edit_tileset_scene = QGraphicsScene()
        self.edit_tileset_view.setScene(self.edit_tileset_scene)
        self.edit_tileset_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tileset_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tileset_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.edit_tileset_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tileset_container_layout.addWidget(self.edit_tileset_view)
        
        edit_tiles_splitter.addWidget(tileset_container)
        
        # Tilemap section
        tilemap_container = QWidget()
        tilemap_container_layout = QVBoxLayout(tilemap_container)
        tilemap_container_layout.setContentsMargins(4, 4, 4, 4)
        tilemap_container_layout.setSpacing(4)
        
        tilemap_label = QLabel("Tilemap")
        tilemap_label.setFont(QFont("Arial", 9, QFont.Bold))
        tilemap_label.setAlignment(Qt.AlignCenter)
        tilemap_container_layout.addWidget(tilemap_label)
        
        self.edit_tilemap_view = QGraphicsView()
        self.edit_tilemap_scene = QGraphicsScene()
        self.edit_tilemap_view.setScene(self.edit_tilemap_scene)
        self.edit_tilemap_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tilemap_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tilemap_view.setStyleSheet("QGraphicsView { background: #e0e0e0; border: 1px solid #ccc; }")
        self.edit_tilemap_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tilemap_container_layout.addWidget(self.edit_tilemap_view)
        
        edit_tiles_splitter.addWidget(tilemap_container)
        edit_tiles_splitter.setSizes([500, 500])
        
        self.layout.addWidget(edit_tiles_splitter)

    def create_header(self, text):
        header = QLabel(text)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        return header
