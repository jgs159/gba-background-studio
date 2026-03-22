# ui/preview_tab.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSplitter, 
                               QGraphicsView, QGraphicsScene, QHBoxLayout, 
                               QPushButton, QSizePolicy)
from PySide6.QtGui import QFont, QPainter
from PySide6.QtCore import Qt
from core.palette_utils import generate_grayscale_palette
import os
import subprocess


class PreviewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.palette_colors = [(0, 0, 0)] * 256
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        preview_header = self.create_header("Preview")
        self.layout.addWidget(preview_header)
        
        main_container = QWidget()
        self.main_layout = QHBoxLayout(main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        image_container = QWidget()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(4, 4, 4, 4)
        image_container_layout.setSpacing(4)
        
        image_label = QLabel("Image")
        image_label.setFont(QFont("Arial", 9, QFont.Bold))
        image_label.setAlignment(Qt.AlignCenter)
        image_container_layout.addWidget(image_label)
        
        self.preview_image_view = QGraphicsView()
        self.preview_image_scene = QGraphicsScene()
        self.preview_image_view.setScene(self.preview_image_scene)
        self.preview_image_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.preview_image_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.preview_image_view.setAlignment(Qt.AlignCenter)
        image_container_layout.addWidget(self.preview_image_view)
        
        palette_container = QWidget()
        palette_container.setFixedWidth(204)
        palette_container_layout = QVBoxLayout(palette_container)
        palette_container_layout.setContentsMargins(4, 4, 4, 4)
        palette_container_layout.setSpacing(4)
        
        palette_label = QLabel("Palette")
        palette_label.setFont(QFont("Arial", 9, QFont.Bold))
        palette_label.setAlignment(Qt.AlignCenter)
        palette_container_layout.addWidget(palette_label)
        
        self.preview_palette_view = QGraphicsView()
        self.preview_palette_scene = QGraphicsScene()
        self.preview_palette_view.setScene(self.preview_palette_scene)
        self.preview_palette_view.setRenderHint(QPainter.Antialiasing, False)
        self.preview_palette_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.preview_palette_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.preview_palette_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        palette_container_layout.addWidget(self.preview_palette_view)
        
        open_output_btn = QPushButton("📁 Open Output Folder")
        open_output_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
        open_output_btn.clicked.connect(self.open_output_folder)
        open_output_btn.setFixedHeight(30)
        palette_container_layout.addWidget(open_output_btn)
        
        self.main_layout.addWidget(image_container, 1)
        self.main_layout.addWidget(palette_container, 0)
        
        self.layout.addWidget(main_container)
        
        self.init_palette_150()

    def create_header(self, text):
        header = QLabel(text)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        return header

    def open_output_folder(self):
        output_dir = "output"
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            if os.name == 'nt':
                os.startfile(output_dir)
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':
                    subprocess.run(['open', output_dir])
                else:
                    subprocess.run(['xdg-open', output_dir])

        except Exception as e:
            if self.parent:
                self.parent.current_status_message = f"Error opening output directory: {str(e)}"

    def init_palette_150(self):
        self.preview_palette_scene.clear()
        tile_size = 12
        
        colors = generate_grayscale_palette()
        
        for i, (r, g, b) in enumerate(colors):
            if i >= 256:
                break
                
            row = i // 16
            col = i % 16
            from PySide6.QtGui import QColor, QBrush, QPen
            color = QColor(r, g, b)
            brush = QBrush(color)
            
            rect = self.preview_palette_scene.addRect(
                col * tile_size, 
                row * tile_size, 
                tile_size, 
                tile_size, 
                QPen(Qt.gray), 
                brush
            )
            rect.setData(1, (r, g, b))

    def load_gba_palette(self, pal_path):
        if not os.path.exists(pal_path):
            print(f"Palette file not found: {pal_path}")
            return [(0, 0, 0)] * 256
        try:
            with open(pal_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
            count = int(lines[0])
            colors = []
            for line in lines[1:1 + count]:
                r, g, b = map(int, line.split())
                colors.append((r, g, b))
            while len(colors) < 256:
                colors.append((0, 0, 0))
            return colors[:256]
        except Exception as e:
            print(f"Error reading palette: {e}")
            return [(0, 0, 0)] * 256

    def display_palette_colors(self, colors):
        self.palette_colors = [(r, g, b) for r, g, b in colors]
        self.preview_palette_scene.clear()
        tile_size = 12
        
        for i, (r, g, b) in enumerate(self.palette_colors):
            if i >= 256:
                break

            row = i // 16
            col = i % 16
            from PySide6.QtGui import QColor, QBrush, QPen
            color = QColor(r, g, b)
            brush = QBrush(color)
            
            rect = self.preview_palette_scene.addRect(
                col * tile_size,
                row * tile_size,
                tile_size,
                tile_size,
                QPen(Qt.gray),
                brush
            )
            rect.setData(1, (r, g, b))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'main_layout'):
            self.main_layout.activate()
