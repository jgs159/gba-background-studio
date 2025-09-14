# ui/edit_tiles_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QGraphicsPixmapItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem
)
from PySide6.QtGui import QFont, QPainter, QPixmap, QPen, QColor
from PySide6.QtCore import Qt

from PIL import Image as PilImage
from core.image_utils import pil_to_qimage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared


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

        self.edit_tileset_view.setMouseTracking(True)
        self.edit_tileset_view.mouseMoveEvent = self.on_tileset_hover
        self.edit_tileset_view.leaveEvent = self.on_tileset_leave
        self.edit_tileset_view.mousePressEvent = self.on_tileset_click

        self.setup_tileset_interaction()
        self.setup_tilemap_interaction()
        self.last_scene_pos = None
        
        self.update_status_bar(-1, -1)

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

    def on_tileset_click(self, event):
        if event.button() != Qt.LeftButton or not self.tileset_img:
            return
        pos = self.edit_tileset_view.mapToScene(event.pos())
        
        scene_rect = self.edit_tileset_scene.sceneRect()
        if not (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
            return
        
        tile_x = max(0, min(int(pos.x()) // 8, self.tiles_per_row - 1))
        max_tile_y = (self.tileset_img.height // 8) - 1
        tile_y = max(0, min(int(pos.y()) // 8, max_tile_y))
        self.selected_tile_id = tile_y * self.tiles_per_row + tile_x
        self.highlight_selected_tile(tile_x, tile_y)
        self.update_status_bar(self.last_hover_pos[0], self.last_hover_pos[1], tile_id=self.selected_tile_id)

    def setup_tileset_interaction(self):
        self.edit_tileset_view.setMouseTracking(True)
        self.edit_tileset_view.mouseMoveEvent = self.on_tileset_hover
        self.edit_tileset_view.leaveEvent = self.on_tileset_leave

    def on_tileset_hover(self, event):
        super(QGraphicsView, self.edit_tileset_view).mouseMoveEvent(event)
        
        if not self.tileset_img:
            return
            
        pos = self.edit_tileset_view.mapToScene(event.pos())
        scene_rect = self.edit_tileset_scene.sceneRect()
        
        if (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
            tile_x = max(0, min(int(pos.x()) // 8, self.tiles_per_row - 1))
            max_tile_y = (self.tileset_img.height // 8) - 1
            tile_y = max(0, min(int(pos.y()) // 8, max_tile_y))
            
            tile_id = tile_y * self.tiles_per_row + tile_x
            self.update_status_bar(-1, -1, tile_id=tile_id)
        else:
            self.update_status_bar(-1, -1, tile_id=self.selected_tile_id)

    def on_tileset_leave(self, event):
        super(QGraphicsView, self.edit_tileset_view).leaveEvent(event)
        
        if hasattr(self, 'last_hover_pos') and self.last_hover_pos != (-1, -1):
            self.update_status_bar(*self.last_hover_pos)
        else:
            self.update_status_bar(-1, -1, tile_id=self.selected_tile_id)

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
        self.update_status_bar(-1, -1)

    def on_tilemap_hover(self, tile_x, tile_y):
        scene_rect = self.edit_tilemap_scene.sceneRect()
        max_tile_x = int(scene_rect.width()) // 8 - 1
        max_tile_y = int(scene_rect.height()) // 8 - 1
        
        if (0 <= tile_x <= max_tile_x and 0 <= tile_y <= max_tile_y):
            self.last_hover_pos = (tile_x, tile_y)
            self.main_window.hover_manager.update_hover(tile_x, tile_y, self.edit_tilemap_view)
            self.update_status_bar(tile_x, tile_y)
        else:
            self.last_hover_pos = (-1, -1)
            self.main_window.hover_manager.hide_hover(self.edit_tilemap_view)
            self.update_status_bar(-1, -1)

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
        
        if self.main_window and hasattr(self.main_window, 'edit_palettes_tab'):
            self.main_window.edit_palettes_tab.tilemap_data = self.tilemap_data
            self.main_window.edit_palettes_tab.update_single_tile_replica(tile_x, tile_y)

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
        
        if tx + 8 > self.tileset_img.width or ty + 8 > self.tileset_img.height:
            return
            
        tile = self.tileset_img.crop((tx, ty, tx + 8, ty + 8))
        if h_flip:
            tile = tile.transpose(PilImage.FLIP_LEFT_RIGHT)
        if v_flip:
            tile = tile.transpose(PilImage.FLIP_TOP_BOTTOM)

        qimg = pil_to_qimage(tile)
        pixmap = QPixmap.fromImage(qimg)

        x = tile_x * 8
        y = tile_y * 8

        for item in self.edit_tilemap_scene.items():
            if isinstance(item, QGraphicsPixmapItem) and int(item.x()) == x and int(item.y()) == y:
                self.edit_tilemap_scene.removeItem(item)
                break

        tile_item = self.edit_tilemap_scene.addPixmap(pixmap)
        tile_item.setPos(x, y)
        tile_item.setZValue(0)

        if hasattr(self.main_window, 'edit_palettes_tab'):
            self.main_window.edit_palettes_tab.tilemap_data = self.tilemap_data
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
                if preview_img.size == (240, 160):
                    self.tilemap_width = 30
                    self.tilemap_height = 20
                else:
                    self.tilemap_width = 32
                    self.tilemap_height = (len(tilemap_data) // 2 + 31) // 32
            except:
                self.tilemap_width = 32
                self.tilemap_height = (len(tilemap_data) // 2 + 31) // 32
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

    def update_status_bar(self, tile_x, tile_y, tile_id=None, palette_id=None, flip_state=None):
        update_status_bar_shared(
            main_window=self.main_window,
            selection_type="Tile",
            selection_id=self.selected_tile_id,
            tile_x=tile_x,
            tile_y=tile_y,
            tilemap_data=self.tilemap_data if hasattr(self, 'tilemap_data') else None,
            tilemap_width=self.tilemap_width if hasattr(self, 'tilemap_width') else 0,
            tilemap_height=self.tilemap_height if hasattr(self, 'tilemap_height') else 0,
            tile_id=tile_id,
            palette_id=palette_id,
            flip_state=flip_state
        )
