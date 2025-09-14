# ui/edit_palettes_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QGraphicsView, QGraphicsScene,
    QHBoxLayout, QGraphicsPixmapItem
)
from PySide6.QtGui import QFont, QBrush, QPen, QColor, QPainter, QPixmap
from PySide6.QtCore import Qt

from PIL import Image as PilImage
from core.image_utils import pil_to_qimage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared


class PaletteGridView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QGraphicsView { border: none; background: transparent; }")
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene(0, 0, 32, 32)
        self.setScene(self.scene)
        self.colors = [
            QColor(238, 136, 116), QColor(248, 210, 144), QColor(160, 218, 228), QColor(244, 156, 178),
            QColor(190, 180, 223), QColor(164, 248, 140), QColor(224, 154, 102), QColor(246, 230, 175),
            QColor(190, 228, 226), QColor(232, 180, 190), QColor(220, 200, 240), QColor(134, 200, 120),
            QColor(246, 188, 104), QColor(148, 196, 218), QColor(248, 146, 198), QColor(180, 160, 200)
        ]
        
        self.selection_overlay = QWidget(self.viewport())
        self.selection_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.selection_overlay.hide()
        
        self.selection_pen = QPen(QColor(0, 0, 0), 1.0)
        self.selection_pen.setCosmetic(True)
        
        self.draw_grid()
        self.selected_palette_pos = (-1, -1)

        self.selection_overlay.paintEvent = self.paintSelectionOverlay

    def draw_grid(self):
        self.scene.clear()
        font = QFont("Arial", 5, QFont.Normal)
        for i in range(4):
            for j in range(4):
                idx = i * 4 + j
                x = j * 8
                y = i * 8
                self.scene.addRect(x, y, 8, 8, pen=QPen(Qt.NoPen), brush=QBrush(self.colors[idx]))
                
                text = self.scene.addText(f"{idx:X}")
                text.setDefaultTextColor(Qt.black)
                text.setFont(font)
                rect = text.boundingRect()
                cx = x + (8 - rect.width()) / 2
                cy = y + (8 - rect.height()) * 0.5
                text.setPos(cx, cy)

    def highlight_selected_palette(self, palette_x, palette_y):
        self.selected_palette_pos = (palette_x, palette_y)
        
        if palette_x == -1 or palette_y == -1:
            self.selection_overlay.hide()
            return
            
        zoom_factor = self.transform().m11()
        x = palette_x * 8 * zoom_factor
        y = palette_y * 8 * zoom_factor
        size = 8 * zoom_factor
        
        self.selection_overlay.setGeometry(int(x), int(y), int(size), int(size))
        self.selection_overlay.show()
        self.selection_overlay.update()

    def set_zoom_factor(self, factor):
        self.resetTransform()
        self.scale(factor, factor)
        self.setFixedSize(32 * factor, 32 * factor)
        
        if self.selected_palette_pos != (-1, -1):
            self.highlight_selected_palette(*self.selected_palette_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.selection_overlay.resize(self.viewport().size())
        
        if self.selected_palette_pos != (-1, -1):
            self.highlight_selected_palette(*self.selected_palette_pos)

    def paintSelectionOverlay(self, event):
        if self.selected_palette_pos == (-1, -1):
            return
            
        painter = QPainter(self.selection_overlay)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setPen(self.selection_pen)
        painter.setBrush(Qt.NoBrush)
        
        painter.drawRect(0.5, 0.5, self.selection_overlay.width() - 1, self.selection_overlay.height() - 1)


class EditPalettesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.selected_palette_id = 0
        self.last_palette_pos = (-1, -1)
        self.last_hover_pos = (-1, -1)
        self.tilemap_width = 0
        self.tilemap_height = 0
        self.tilemap_data = None
        self.overlay_items = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Header
        header = QLabel("Edit Palettes")
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)

        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)

        # === LEFT: Palettes ===
        palettes_container = QWidget()
        palettes_layout = QVBoxLayout(palettes_container)
        palettes_layout.setContentsMargins(4, 4, 4, 4)
        palettes_layout.setSpacing(4)

        palettes_label = QLabel("Palettes")
        palettes_label.setFont(QFont("Arial", 9, QFont.Bold))
        palettes_label.setAlignment(Qt.AlignCenter)
        palettes_layout.addWidget(palettes_label)

        # === Top Section: Fixed 256px height ===
        height_container = QWidget()
        height_container.setFixedHeight(256)
        top_layout = QHBoxLayout(height_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        self.grid_view = PaletteGridView()
        top_layout.addWidget(self.grid_view, 0, Qt.AlignLeft | Qt.AlignTop)
        top_layout.addStretch()

        self.grid_view.setMouseTracking(True)
        self.grid_view.mouseMoveEvent = self.on_palette_grid_hover
        self.grid_view.leaveEvent = self.on_palette_grid_leave
        self.grid_view.mousePressEvent = self.on_palette_grid_click

        palettes_layout.addWidget(height_container)

        # Bottom: Reserved
        self.edit_palettes_view = QGraphicsView()
        self.edit_palettes_scene = QGraphicsScene()
        self.edit_palettes_view.setScene(self.edit_palettes_scene)
        self.edit_palettes_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_palettes_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_palettes_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.edit_palettes_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        palettes_layout.addWidget(self.edit_palettes_view)

        main_splitter.addWidget(palettes_container)

        # === RIGHT: Tilemap Replica ===
        tilemap_container = QWidget()
        tilemap_layout = QVBoxLayout(tilemap_container)
        tilemap_layout.setContentsMargins(4, 4, 4, 4)
        tilemap_layout.setSpacing(4)

        tilemap_label = QLabel("Tilemap")
        tilemap_label.setFont(QFont("Arial", 9, QFont.Bold))
        tilemap_label.setAlignment(Qt.AlignCenter)
        tilemap_layout.addWidget(tilemap_label)

        self.edit_tilemap2_view = CustomGraphicsView()
        self.edit_tilemap2_scene = QGraphicsScene()
        self.edit_tilemap2_view.setScene(self.edit_tilemap2_scene)
        self.edit_tilemap2_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tilemap2_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tilemap2_view.setStyleSheet("QGraphicsView { background: #e0e0e0; border: 1px solid #ccc; }")
        self.edit_tilemap2_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.edit_tilemap2_view.setMouseTracking(True)
        tilemap_layout.addWidget(self.edit_tilemap2_view)

        main_splitter.addWidget(tilemap_container)
        main_splitter.setSizes([500, 500])
        self.layout.addWidget(main_splitter)

        self.colors = self.grid_view.colors
        self._pixmap_item = None

        self.setup_tilemap_interaction()
        self.highlight_selected_palette(0, 0)
      
        self.update_status_bar(-1, -1)

    def setup_tilemap_interaction(self):
        self.edit_tilemap2_view.on_tile_drawing = self.on_tilemap_drawing
        self.edit_tilemap2_view.on_tile_selected = self.on_tilemap_right_click
        self.edit_tilemap2_view.on_tile_hover = self.on_tilemap_hover
        self.edit_tilemap2_view.on_tile_leave = self.on_tilemap_leave

    def on_palette_grid_click(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.grid_view.mapToScene(event.pos())
            
            if not (0 <= pos.x() < 32 and 0 <= pos.y() < 32):
                return
            
            palette_x = max(0, min(int(pos.x()) // 8, 3))
            palette_y = max(0, min(int(pos.y()) // 8, 3))
            self.selected_palette_id = palette_y * 4 + palette_x
            self.highlight_selected_palette(palette_x, palette_y)
            self.update_status_bar(self.last_hover_pos[0], self.last_hover_pos[1], palette_id=self.selected_palette_id)

    def on_palette_grid_hover(self, event):
        super(QGraphicsView, self.grid_view).mouseMoveEvent(event)
        
        pos = self.grid_view.mapToScene(event.pos())
        
        if (0 <= pos.x() < 32 and 0 <= pos.y() < 32):
            palette_x = max(0, min(int(pos.x()) // 8, 3))
            palette_y = max(0, min(int(pos.y()) // 8, 3))
            palette_id = palette_y * 4 + palette_x
            self.update_status_bar(-1, -1, palette_id=palette_id)
        else:
            self.update_status_bar(-1, -1, palette_id=self.selected_palette_id)

    def on_palette_grid_leave(self, event):
        QGraphicsView.leaveEvent(self.grid_view, event)
        
        if hasattr(self, 'last_hover_pos') and self.last_hover_pos != (-1, -1):
            self.update_status_bar(*self.last_hover_pos)
        else:
            self.update_status_bar(-1, -1, palette_id=self.selected_palette_id)

    def highlight_selected_palette(self, palette_x, palette_y):
        self.grid_view.highlight_selected_palette(palette_x, palette_y)

    def on_tilemap_leave(self):
        self.main_window.hover_manager.hide_hover(self.edit_tilemap2_view)
        self.last_hover_pos = (-1, -1)
        self.update_status_bar(-1, -1)

    def on_tilemap_hover(self, tile_x, tile_y):
        scene_rect = self.edit_tilemap2_scene.sceneRect()
        max_tile_x = int(scene_rect.width()) // 8 - 1
        max_tile_y = int(scene_rect.height()) // 8 - 1
        
        if (0 <= tile_x <= max_tile_x and 0 <= tile_y <= max_tile_y):
            self.last_hover_pos = (tile_x, tile_y)
            self.main_window.hover_manager.update_hover(tile_x, tile_y, self.edit_tilemap2_view)
            self.update_status_bar(tile_x, tile_y)
        else:
            self.last_hover_pos = (-1, -1)
            self.main_window.hover_manager.hide_hover(self.edit_tilemap2_view)
            self.update_status_bar(-1, -1)

    def on_tilemap_drawing(self, tile_x, tile_y):
        if self.selected_palette_id is None or not self.tilemap_data:
            return
        self.on_tilemap_hover(tile_x, tile_y)
        self.edit_palette_at(tile_x, tile_y)

    def on_tilemap_right_click(self, tile_x, tile_y):
        if not self.tilemap_data:
            return
        tile_index = tile_y * self.tilemap_width + tile_x
        if 0 <= tile_index < len(self.tilemap_data) // 2:
            entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
            palette_id = (entry >> 12) & 0xF
            self.selected_palette_id = palette_id
            px = (palette_id % 4)
            py = (palette_id // 4)
            self.highlight_selected_palette(px, py)
        self.on_tilemap_hover(tile_x, tile_y)

    def edit_palette_at(self, tile_x, tile_y):
        if not self.tilemap_data:
            return

        tile_index = tile_y * self.tilemap_width + tile_x
        if tile_index >= len(self.tilemap_data) // 2:
            return

        current_entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
        current_palette_id = (current_entry >> 12) & 0xF

        if current_palette_id == self.selected_palette_id:
            return

        tile_id = current_entry & 0x3FF
        h_flip = bool(current_entry & (1 << 10))
        v_flip = bool(current_entry & (1 << 11))
        
        new_entry = tile_id
        if h_flip:
            new_entry |= (1 << 10)
        if v_flip:
            new_entry |= (1 << 11)
        new_entry |= (self.selected_palette_id << 12)

        tilemap_data = bytearray(self.tilemap_data)
        tilemap_data[tile_index * 2] = new_entry & 0xFF
        tilemap_data[tile_index * 2 + 1] = (new_entry >> 8) & 0xFF
        self.tilemap_data = bytes(tilemap_data)

        self.update_palette_overlay_for_tile(tile_x, tile_y, self.selected_palette_id)
        
        if self.main_window and hasattr(self.main_window, 'edit_tiles_tab'):
            self.main_window.edit_tiles_tab.tilemap_data = self.tilemap_data
            self.main_window.edit_tiles_tab.update_single_tile_visual(tile_x, tile_y)

    def update_palette_overlay_for_tile(self, tile_x, tile_y, palette_id):
        x = tile_x * 8
        y = tile_y * 8
        
        tile_key = (tile_x, tile_y)
        if tile_key in self.overlay_items:
            for item in self.overlay_items[tile_key]:
                if item in self.edit_tilemap2_scene.items():
                    self.edit_tilemap2_scene.removeItem(item)
            del self.overlay_items[tile_key]
        
        color = self.colors[palette_id]
        rect_item = self.edit_tilemap2_scene.addRect(x, y, 8, 8, QPen(Qt.NoPen), QBrush(color))
        rect_item.setZValue(1)
        rect_item.setOpacity(0.3)

        font = QFont("Arial", 5, QFont.Normal)
        text_item = self.edit_tilemap2_scene.addText(f"{palette_id:X}")
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor(0, 0, 0))
        
        rect = text_item.boundingRect()
        cx = x + (8 - rect.width()) / 2
        cy = y + (8 - rect.height()) * 0.5
        text_item.setPos(cx, cy)
        text_item.setZValue(2)

        self.overlay_items[tile_key] = [rect_item, text_item]

    def create_text_pixmap(self, text, font, color):
        scale_factor = 4
        pixmap = QPixmap(8 * scale_factor, 8 * scale_factor)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setFont(font)
        painter.setPen(color)
        
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        
        return pixmap.scaled(8, 8, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def display_tilemap_replica(self, source_scene):
        self.edit_tilemap2_scene.clear()
        self.overlay_items.clear()
        if source_scene.items():
            item = source_scene.items()[0]
            pixmap = item.pixmap()
            self._pixmap_item = self.edit_tilemap2_scene.addPixmap(pixmap)
            self.edit_tilemap2_scene.setSceneRect(pixmap.rect())
            
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_palettes")

    def update_palette_overlay(self, source_scene, tilemap_data, tile_width, tile_height):
        if not source_scene.items() or not tilemap_data:
            return

        self.tilemap_data = tilemap_data
        self.tilemap_width = tile_width
        self.tilemap_height = tile_height
        self.overlay_items.clear()

        self.edit_tilemap2_scene.clear()
        if source_scene.items():
            item = source_scene.items()[0]
            pixmap = item.pixmap()
            self._pixmap_item = self.edit_tilemap2_scene.addPixmap(pixmap)
            self.edit_tilemap2_scene.setSceneRect(pixmap.rect())
            self._pixmap_item.setZValue(0)

        for i in range(tile_height):
            for j in range(tile_width):
                idx = i * tile_width + j
                if idx >= len(tilemap_data) // 2:
                    continue

                entry = tilemap_data[idx * 2] | (tilemap_data[idx * 2 + 1] << 8)
                palette_id = (entry >> 12) & 0xF
                self.update_palette_overlay_for_tile(j, i, palette_id)

        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_palettes")

    def update_single_tile_replica(self, tile_x, tile_y):
        if not hasattr(self, 'main_window') or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
            
        source_scene = self.main_window.edit_tiles_tab.edit_tilemap_scene
        x_pos = tile_x * 8
        y_pos = tile_y * 8
        
        new_pixmap = None
        for item in source_scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                if int(item.x()) == x_pos and int(item.y()) == y_pos:
                    new_pixmap = item.pixmap()
                    break
        
        if not new_pixmap:
            return
        
        for item in self.edit_tilemap2_scene.items():
            if (isinstance(item, QGraphicsPixmapItem) and 
                int(item.x()) == x_pos and 
                int(item.y()) == y_pos and
                item.zValue() == 0):
                self.edit_tilemap2_scene.removeItem(item)
                break
        
        pixmap_item = self.edit_tilemap2_scene.addPixmap(new_pixmap)
        pixmap_item.setPos(x_pos, y_pos)
        pixmap_item.setZValue(0)

        if hasattr(self, 'tilemap_data') and self.tilemap_data:
            tile_index = tile_y * self.tilemap_width + tile_x
            if tile_index < len(self.tilemap_data) // 2:
                entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
                palette_id = (entry >> 12) & 0xF
                self.update_palette_overlay_for_tile(tile_x, tile_y, palette_id)

    def apply_zoom(self, factor):
        self.grid_view.set_zoom_factor(factor)
        self.edit_tilemap2_view.resetTransform()
        self.edit_tilemap2_view.scale(factor, factor)

    def display_palette_colors(self, colors):
        self.colors = colors
        self.grid_view.colors = colors
        self.grid_view.draw_grid()
        self.highlight_selected_palette(self.selected_palette_id % 4, self.selected_palette_id // 4)
        
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("palettes")

    def update_status_bar(self, tile_x, tile_y, tile_id=None, palette_id=None, flip_state=None):
        update_status_bar_shared(
            main_window=self.main_window,
            selection_type="Palette",
            selection_id=self.selected_palette_id,
            tile_x=tile_x,
            tile_y=tile_y,
            tilemap_data=self.tilemap_data if hasattr(self, 'tilemap_data') else None,
            tilemap_width=self.tilemap_width if hasattr(self, 'tilemap_width') else 0,
            tilemap_height=self.tilemap_height if hasattr(self, 'tilemap_height') else 0,
            tile_id=tile_id,
            palette_id=palette_id,
            flip_state=flip_state
        )
