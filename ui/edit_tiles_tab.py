# ui/edit_tiles_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QGraphicsPixmapItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem
)
from PySide6.QtGui import QFont, QPainter, QPixmap, QPen, QColor
from PySide6.QtCore import Qt

from PIL import Image as PilImage
from core.image_utils import pil_to_qimage


class CustomGraphicsView(QGraphicsView):
    """Vista personalizada para habilitar dibujo continuo en el tilemap"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._is_drawing = False
        self.on_tile_drawing = None
        self.on_tile_selected = None
        self.on_tile_hover = None
        self.on_tile_leave = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_drawing = True
            pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                tile_x = max(0, min(int(pos.x()) // 8, int(self.sceneRect().width()) // 8 - 1))
                tile_y = max(0, min(int(pos.y()) // 8, int(self.sceneRect().height()) // 8 - 1))
                if self.on_tile_drawing:
                    self.on_tile_drawing(tile_x, tile_y)
            event.accept()
        elif event.button() == Qt.RightButton:
            pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                tile_x = max(0, min(int(pos.x()) // 8, int(self.sceneRect().width()) // 8 - 1))
                tile_y = max(0, min(int(pos.y()) // 8, int(self.sceneRect().height()) // 8 - 1))
                if self.on_tile_selected:
                    self.on_tile_selected(tile_x, tile_y)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        if not self.scene() or not pos or not self.scene().sceneRect().isValid():
            if self.on_tile_leave:
                self.on_tile_leave()
            super().mouseMoveEvent(event)
            return

        tile_x = max(0, min(int(pos.x()) // 8, int(self.sceneRect().width()) // 8 - 1))
        tile_y = max(0, min(int(pos.y()) // 8, int(self.sceneRect().height()) // 8 - 1))

        scene_rect = self.scene().sceneRect()
        if (tile_x < 0 or tile_y < 0 or 
            tile_x >= scene_rect.width() // 8 or 
            tile_y >= scene_rect.height() // 8):
            if self.on_tile_leave:
                self.on_tile_leave()
            super().mouseMoveEvent(event)
            return

        if self.on_tile_hover:
            self.on_tile_hover(tile_x, tile_y)

        if self._is_drawing and (event.buttons() & Qt.LeftButton) and self.on_tile_drawing:
            self.on_tile_drawing(tile_x, tile_y)
            event.accept()
        else:
            event.accept()
            super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.on_tile_leave:
            self.on_tile_leave()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_drawing = False
        super().mouseReleaseEvent(event)


class EditTilesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.selected_tile_id = 0
        self.last_tile_pos = (-1, -1)
        self.last_hover_pos = (-1, -1)
        self.tileset_img = None
        self.tiles_per_row = 0
        self.tilemap_width = 0
        self.tilemap_height = 0
        self.tilemap_data = None
        self.selected_tile_pos = (-1, -1)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Header
        header = self.create_header("Edit Tiles")
        self.layout.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(6)

        # === Tileset ===
        tileset_container = self.create_section("Tileset")
        self.edit_tileset_view = QGraphicsView()
        self.edit_tileset_scene = QGraphicsScene()
        self.edit_tileset_view.setScene(self.edit_tileset_scene)
        self.setup_view(self.edit_tileset_view)
        tileset_container.layout().addWidget(self.edit_tileset_view)
        splitter.addWidget(tileset_container)

        # === Tilemap ===
        tilemap_container = self.create_section("Tilemap")
        self.edit_tilemap_view = CustomGraphicsView()
        self.edit_tilemap_scene = QGraphicsScene()
        self.edit_tilemap_view.setScene(self.edit_tilemap_scene)
        self.setup_view(self.edit_tilemap_view)
        tilemap_container.layout().addWidget(self.edit_tilemap_view)
        splitter.addWidget(tilemap_container)

        splitter.setSizes([500, 500])
        self.layout.addWidget(splitter)

        self.setup_tileset_interaction()
        self.setup_tilemap_interaction()
        self.last_scene_pos = None

    def create_header(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 10, QFont.Bold))
        label.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        label.setFixedHeight(30)
        label.setAlignment(Qt.AlignCenter)
        return label

    def create_section(self, title):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        label = QLabel(title)
        label.setFont(QFont("Arial", 9, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return container

    def setup_view(self, view):
        view.setRenderHint(QPainter.Antialiasing, False)
        view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        view.setMouseTracking(True)

    def setup_tileset_interaction(self):
        self.edit_tileset_view.setInteractive(True)
        self.edit_tileset_view.mousePressEvent = self.on_tileset_click

    def on_tileset_click(self, event):
        if event.button() != Qt.LeftButton or not self.tileset_img:
            return
        pos = self.edit_tileset_view.mapToScene(event.pos())
        tile_x = max(0, min(int(pos.x()) // 8, self.tiles_per_row - 1))
        max_tile_y = (self.tileset_img.height // 8) - 1
        tile_y = max(0, min(int(pos.y()) // 8, max_tile_y))
        self.selected_tile_id = tile_y * self.tiles_per_row + tile_x
        self.highlight_selected_tile(tile_x, tile_y)
        self.main_window.custom_status_bar.show_message(f"Tile selected: {self.selected_tile_id}")

    def highlight_selected_tile(self, tile_x, tile_y):
        self.selected_tile_pos = (tile_x, tile_y)
        
        for item in self.edit_tileset_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.edit_tileset_scene.removeItem(item)
        
        zoom_factor = self.edit_tileset_view.transform().m11()
        pen = QPen(QColor(255, 255, 0), 1.0)
        pen.setCosmetic(True)
        
        scene_size = 8 - (1 / zoom_factor)
        
        rect_item = self.edit_tileset_scene.addRect(
            tile_x * 8,
            tile_y * 8,
            scene_size,
            scene_size,
            pen
        )
        rect_item.setZValue(100)

    def setup_tilemap_interaction(self):
        self.edit_tilemap_view.on_tile_drawing = self.on_tilemap_drawing
        self.edit_tilemap_view.on_tile_selected = self.on_tilemap_right_click
        self.edit_tilemap_view.on_tile_hover = self.on_tilemap_hover
        self.edit_tilemap_view.on_tile_leave = self.on_tilemap_leave

    def on_tilemap_leave(self):
        self.main_window.hover_manager.hide_hover(self.edit_tilemap_view)
        self.last_hover_pos = (-1, -1)

    def on_tilemap_hover(self, tile_x, tile_y):
        if (tile_x, tile_y) == self.last_hover_pos:
            return
        self.last_hover_pos = (tile_x, tile_y)
        self.main_window.hover_manager.update_hover(tile_x, tile_y, self.edit_tilemap_view)

    def on_tilemap_drawing(self, tile_x, tile_y):
        if self.selected_tile_id is None or not self.tilemap_data:
            return
        self.on_tilemap_hover(tile_x, tile_y)
        self.edit_tile_at(tile_x, tile_y)

    def on_tilemap_right_click(self, tile_x, tile_y):
        if not self.tilemap_data:
            return
        tile_index = tile_y * self.tilemap_width + tile_x
        if 0 <= tile_index < len(self.tilemap_data) // 2:
            entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
            tile_id = entry & 0x3FF
            self.selected_tile_id = tile_id
            tx = (tile_id % self.tiles_per_row)
            ty = (tile_id // self.tiles_per_row)
            self.highlight_selected_tile(tx, ty)
            self.main_window.custom_status_bar.show_message(f"Tile selected from map: {tile_id}")
        self.on_tilemap_hover(tile_x, tile_y)

    def edit_tile_at(self, tile_x, tile_y):
        if not self.tilemap_data:
            return

        tile_index = tile_y * self.tilemap_width + tile_x
        if tile_index >= len(self.tilemap_data) // 2:
            return

        current_entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
        current_tile_id = current_entry & 0x3FF

        if current_tile_id == self.selected_tile_id:
            return

        flags = current_entry & 0xFC00
        new_entry = (self.selected_tile_id & 0x3FF) | flags

        tilemap_data = bytearray(self.tilemap_data)
        tilemap_data[tile_index * 2] = new_entry & 0xFF
        tilemap_data[tile_index * 2 + 1] = (new_entry >> 8) & 0xFF
        self.tilemap_data = bytes(tilemap_data)

        self.update_single_tile_visual(tile_x, tile_y)
        self.main_window.custom_status_bar.show_message(f"Tile {tile_index} updated with ID {self.selected_tile_id}")

    def update_single_tile_visual(self, tile_x, tile_y):
        if not self.tileset_img or not self.tilemap_data:
            return

        tile_index = tile_y * self.tilemap_width + tile_x
        if tile_index >= len(self.tilemap_data) // 2:
            return

        entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
        tile_id = entry & 0x3FF
        h_flip = bool(entry & (1 << 10))
        v_flip = bool(entry & (1 << 11))

        tx = (tile_id % self.tiles_per_row) * 8
        ty = (tile_id // self.tiles_per_row) * 8
        tile = self.tileset_img.crop((tx, ty, tx + 8, ty + 8))
        if h_flip:
            tile = tile.transpose(PilImage.FLIP_LEFT_RIGHT)
        if v_flip:
            tile = tile.transpose(PilImage.FLIP_TOP_BOTTOM)

        qimg = pil_to_qimage(tile)
        pixmap = QPixmap.fromImage(qimg)

        x = tile_x * 8
        y = tile_y * 8

        items = self.edit_tilemap_scene.items()
        for item in items:
            if isinstance(item, QGraphicsPixmapItem):
                if int(item.x()) == x and int(item.y()) == y:
                    self.edit_tilemap_scene.removeItem(item)
                    break

        tile_item = self.edit_tilemap_scene.addPixmap(pixmap)
        tile_item.setPos(x, y)
        tile_item.setZValue(0)

        if hasattr(self.main_window, 'edit_palettes_tab'):
            self.main_window.edit_palettes_tab.update_single_tile_replica(tile_x, tile_y)

        self.on_tilemap_hover(tile_x, tile_y)

    def display_tileset(self, pil_img):
        self.edit_tileset_scene.clear()
        self.tileset_img = pil_img
        self.tiles_per_row = pil_img.width // 8
        qimg = pil_to_qimage(pil_img)
        pixmap = QPixmap.fromImage(qimg)
        self.edit_tileset_scene.addPixmap(pixmap)
        self.edit_tileset_scene.setSceneRect(0, 0, pil_img.width, pil_img.height)
        self.highlight_selected_tile(0, 0)
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tileset")

    def load_tilemap(self, tilemap_data, tileset_path, preview_path=None):
        self.tilemap_data = tilemap_data
        self.tileset_img = PilImage.open(tileset_path)
        self.tiles_per_row = self.tileset_img.width // 8
        if preview_path:
            try:
                preview_img = PilImage.open(preview_path)
                self.tilemap_width = preview_img.width // 8
                self.tilemap_height = preview_img.height // 8
            except:
                total_tiles = len(tilemap_data) // 2
                if total_tiles == 256:
                    self.tilemap_width = 16
                    self.tilemap_height = 16
                elif total_tiles == 1024:
                    self.tilemap_width = 32
                    self.tilemap_height = 32
                else:
                    self.tilemap_width = 32
                    self.tilemap_height = (total_tiles + 31) // 32
        else:
            total_tiles = len(tilemap_data) // 2
            
            if total_tiles == 256:
                self.tilemap_width = 16
                self.tilemap_height = 16
            elif total_tiles == 1024:
                self.tilemap_width = 32
                self.tilemap_height = 32
            else:
                self.tilemap_width = 32
                self.tilemap_height = (total_tiles + 31) // 32

        w = self.tilemap_width * 8
        h = self.tilemap_height * 8
        img = PilImage.new('RGBA', (w, h), (0, 0, 0, 0))
        for i in range(min(self.tilemap_width * self.tilemap_height, len(self.tilemap_data) // 2)):
            entry = self.tilemap_data[i * 2] | (self.tilemap_data[i * 2 + 1] << 8)
            tile_id = entry & 0x3FF
            h_flip = bool(entry & (1 << 10))
            v_flip = bool(entry & (1 << 11))
            tx = (tile_id % self.tiles_per_row) * 8
            ty = (tile_id // self.tiles_per_row) * 8
            tile = self.tileset_img.crop((tx, ty, tx + 8, ty + 8))
            if h_flip:
                tile = tile.transpose(PilImage.FLIP_LEFT_RIGHT)
            if v_flip:
                tile = tile.transpose(PilImage.FLIP_TOP_BOTTOM)
            x = (i % self.tilemap_width) * 8
            y = (i // self.tilemap_width) * 8
            img.paste(tile, (x, y))
        qimg = pil_to_qimage(img)
        pixmap = QPixmap.fromImage(qimg)
        self.edit_tilemap_scene.clear()
        self.edit_tilemap_scene.addPixmap(pixmap)
        self.edit_tilemap_scene.setSceneRect(0, 0, w, h)

        if self.last_hover_pos != (-1, -1):
            x, y = self.last_hover_pos
            if 0 <= x < self.tilemap_width and 0 <= y < self.tilemap_height:
                self.on_tilemap_hover(x, y)

        if hasattr(self.main_window, 'sync_palettes_tab'):
            self.main_window.sync_palettes_tab()

        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_edit")

    def apply_zoom(self, factor):
        self.edit_tileset_view.resetTransform()
        self.edit_tileset_view.scale(factor, factor)
        
        if self.selected_tile_pos != (-1, -1):
            self.highlight_selected_tile(*self.selected_tile_pos)