# ui/edit_palettes_tab.py
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QGraphicsView, QGraphicsScene,
    QHBoxLayout, QGraphicsPixmapItem, QFrame, QSlider, QSizePolicy, QGridLayout,
    QGraphicsRectItem, QLineEdit, QSpinBox, QPushButton, QCheckBox
)
from PySide6.QtGui import QFont, QBrush, QPen, QColor, QPainter, QPixmap, QIntValidator
from PySide6.QtCore import Qt, Signal, QTimer

from PIL import Image as PilImage
from core.image_utils import pil_to_qimage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared
from ui.palette_grid_view import PaletteGridView
from ui.color_editor import ColorEditor
from ui.tilemap_utils import TilemapUtils
from utils.translator import Translator
translator = Translator()

EMPTY_TILE_ENTRY = b'\x00\x00'

class EditPalettesTab(TilemapUtils, QWidget):
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
        self.palette_colors = [(0, 0, 0)] * 256
        self.selection_rect = None
        self.palette_rects = []

        self.last_edited_index = -1
        self.last_edited_color = (0, 0, 0)
        self.current_editing_index = -1

        self.setup_ui()
        self.setup_tilemap_interaction()
        self.highlight_selected_palette(0, 0)
      
        QTimer.singleShot(100, lambda: self.draw_selection_rectangle(0))
        QTimer.singleShot(100, self.connect_tab_signals)
        QTimer.singleShot(100, self.initialize_color_editor)
        QTimer.singleShot(0, self._init_grayscale_palette)

        self.update_status_bar(-1, -1)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        header = QLabel("Edit Palettes")
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)

        palettes_container = self.create_palettes_container()
        main_splitter.addWidget(palettes_container)

        tilemap_container = self.create_tilemap_container()
        main_splitter.addWidget(tilemap_container)
        
        main_splitter.setSizes([500, 500])
        self.layout.addWidget(main_splitter)

        self.colors = self.grid_view.colors
        self._pixmap_item = None

    def create_palettes_container(self):
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #f0f0f0; }")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        palettes_label = QLabel("Palettes")
        palettes_label.setFont(QFont("Arial", 9, QFont.Bold))
        palettes_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(palettes_label)

        bordered_frame = QFrame()
        bordered_frame.setFrameShape(QFrame.StyledPanel)
        bordered_frame.setFrameShadow(QFrame.Raised)
        bordered_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
        """)
        bordered_frame.setFixedHeight(271)

        inner_layout = QHBoxLayout(bordered_frame)
        inner_layout.setContentsMargins(4, 4, 4, 4)
        inner_layout.setSpacing(4)

        left_container = self.create_left_palette_container()
        inner_layout.addWidget(left_container)

        right_container = self.create_right_palette_container()
        inner_layout.addWidget(right_container)

        layout.addWidget(bordered_frame)

        self.edit_palettes_view = QGraphicsView()
        self.edit_palettes_scene = QGraphicsScene()
        self.edit_palettes_view.setScene(self.edit_palettes_scene)
        self.edit_palettes_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_palettes_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_palettes_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.edit_palettes_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.edit_palettes_view)

        return container

    def create_left_palette_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.grid_view = PaletteGridView()
        self.grid_view.setMouseTracking(True)
        self.grid_view.mouseMoveEvent = self.on_palette_grid_hover
        self.grid_view.leaveEvent = self.on_palette_grid_leave
        self.grid_view.mousePressEvent = self.on_palette_grid_click
        self.grid_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: none; }")
        layout.addWidget(self.grid_view)
        
        return container

    def on_palette_grid_click(self, event):
        if event.button() != Qt.LeftButton:
            return
        super(QGraphicsView, self.grid_view).mousePressEvent(event)
        pos = self.grid_view.mapToScene(event.pos())
        if not (0 <= pos.x() < 32 and 0 <= pos.y() < 32):
            return
        palette_x = max(0, min(int(pos.x()) // 8, 3))
        palette_y = max(0, min(int(pos.y()) // 8, 3))
        self.selected_palette_id = palette_y * 4 + palette_x
        self.highlight_selected_palette(palette_x, palette_y)
        self.update_status_bar(self.last_hover_pos[0], self.last_hover_pos[1], palette_id=self.selected_palette_id)

    def create_right_palette_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        self.full_palette_view = QGraphicsView()
        self.full_palette_scene = QGraphicsScene()
        self.full_palette_view.setScene(self.full_palette_scene)
        self.full_palette_view.setRenderHint(QPainter.Antialiasing, False)
        self.full_palette_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.full_palette_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: none; }")
        self.full_palette_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.full_palette_view.setFixedSize(195, 195)
        layout.addWidget(self.full_palette_view)
        
        editor_container = QWidget()
        editor_container.setFixedSize(195, 65)
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        self.color_editor = ColorEditor(self)
        editor_layout.addWidget(self.color_editor)
        self.color_editor.color_updated.connect(lambda index, r, g, b, record: self.update_selected_color(index, r, g, b, record))

        layout.addWidget(editor_container)
        
        return container

    def create_tilemap_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        tilemap_label = QLabel("Tilemap")
        tilemap_label.setFont(QFont("Arial", 9, QFont.Bold))
        tilemap_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tilemap_label)

        tilemap_toolbar = self.create_tilemap_toolbar()
        layout.addWidget(tilemap_toolbar)

        self.edit_tilemap2_view = CustomGraphicsView()
        self.edit_tilemap2_scene = QGraphicsScene()
        self.edit_tilemap2_view.setScene(self.edit_tilemap2_scene)
        self.edit_tilemap2_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tilemap2_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tilemap2_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.edit_tilemap2_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.edit_tilemap2_view.setMouseTracking(True)
        layout.addWidget(self.edit_tilemap2_view)
        self.tilemap_view  = self.edit_tilemap2_view
        self.tilemap_scene = self.edit_tilemap2_scene

        return container

    def create_tilemap_toolbar(self):
        return self.build_tilemap_toolbar()

    def initialize_color_editor(self):
        if (hasattr(self, 'palette_colors') and 
            len(self.palette_colors) > 0 and
            hasattr(self, 'color_editor')):
            
            r, g, b = self.palette_colors[0]
            self.color_editor.set_color(0, r, g, b)
            self.draw_selection_rectangle(0)
            
            self.current_editing_index = 0
            self.last_edited_index = -1
            self.last_edited_color = (r, g, b)

    def _init_grayscale_palette(self):
        from core.palette_utils import generate_grayscale_palette
        self.display_palette_colors(generate_grayscale_palette(), enable_editor=False)

    def setup_tilemap_interaction(self):
        super().setup_tilemap_interaction()

    def on_tilemap_leave(self):
        super().on_tilemap_leave()

    def on_tilemap_hover(self, tile_x, tile_y):
        super().on_tilemap_hover(tile_x, tile_y)

    def on_tilemap_drawing(self, tile_x, tile_y):
        self.finalize_color_editing()
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
        self.finalize_color_editing()
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
        self.finalize_color_editing()
        if self.selected_palette_id is None or not self.tilemap_data:
            return
        self.on_tilemap_hover(tile_x, tile_y)
        self.edit_palette_at(tile_x, tile_y)

    def on_tilemap_release(self):
        if not self.tilemap_data:
            return
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(self.tilemap_data)
        if self.main_window:
            if hasattr(self.main_window, 'edit_tiles_tab'):
                self.main_window.edit_tiles_tab.tilemap_data = self.tilemap_data
            if hasattr(self.main_window, '_save_map_and_refresh'):
                self.main_window._save_map_and_refresh()

    def on_tilemap_right_click(self, tile_x, tile_y):
        self.finalize_color_editing()
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

    def focusOutEvent(self, event):
        self.finalize_color_editing()
        super().focusOutEvent(event)

    def connect_tab_signals(self):
        if self.main_window and hasattr(self.main_window, 'main_tabs'):
            self.main_window.main_tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        current_tab = self.main_window.main_tabs.widget(index)
        if current_tab != self:
            self.finalize_color_editing()

    def edit_palette_at(self, tile_x, tile_y):
        if not self.tilemap_data:
            return

        tile_index = tile_y * self.tilemap_width + tile_x
        if tile_index >= len(self.tilemap_data) // 2:
            return

        current_entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
        old_palette_id = (current_entry >> 12) & 0xF
        old_state = {
            'tile_x': tile_x,
            'tile_y': tile_y,
            'old_palette_id': old_palette_id,
            'new_palette_id': self.selected_palette_id,
            'tile_id': current_entry & 0x3FF,
            'h_flip': bool(current_entry & (1 << 10)),
            'v_flip': bool(current_entry & (1 << 11))
        }

        if old_palette_id == self.selected_palette_id:
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

        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='palette_change',
                editor_type='palettes',
                data=old_state,
                description=f"Palette changed at ({tile_x}, {tile_y})"
            )

        self.update_palette_overlay_for_tile(tile_x, tile_y, self.selected_palette_id)
        self._repaint_tile_in_scene(tile_x, tile_y, self.selected_palette_id)

        if self.main_window and hasattr(self.main_window, 'edit_tiles_tab'):
            self.main_window.edit_tiles_tab.tilemap_data = self.tilemap_data

    def _repaint_tile_in_scene(self, tile_x, tile_y, palette_id):
        if not self._pixmap_item:
            return
        et = getattr(self.main_window, 'edit_tiles_tab', None)
        if not et or not et.tileset_img or not et.tilemap_data:
            return

        tile_index = tile_y * self.tilemap_width + tile_x
        if tile_index >= len(et.tilemap_data) // 2:
            return

        entry = et.tilemap_data[tile_index * 2] | (et.tilemap_data[tile_index * 2 + 1] << 8)
        tile_id  = entry & 0x3FF
        h_flip   = bool(entry & (1 << 10))
        v_flip   = bool(entry & (1 << 11))

        import numpy as np
        ts = et.tileset_img
        tx = (tile_id % et.tiles_per_row) * 8
        ty = (tile_id // et.tiles_per_row) * 8
        if tx + 8 > ts.width or ty + 8 > ts.height:
            return

        tile_arr = np.array(ts)[ty:ty+8, tx:tx+8].copy()
        if h_flip:
            tile_arr = np.fliplr(tile_arr)
        if v_flip:
            tile_arr = np.flipud(tile_arr)

        slot_start = palette_id * 16
        slot_colors = self.palette_colors[slot_start:slot_start + 16]

        from PySide6.QtGui import QImage, QPainter as _QPainter, QColor as _QColor
        tile_img = QImage(8, 8, QImage.Format_RGB32)
        for py in range(8):
            for px in range(8):
                idx = int(tile_arr[py, px]) % 16
                r, g, b = slot_colors[idx]
                tile_img.setPixel(px, py, _QColor(r, g, b).rgb())

        tile_pixmap = QPixmap.fromImage(tile_img)

        scene_pixmap = self._pixmap_item.pixmap()
        painter = _QPainter(scene_pixmap)
        painter.drawPixmap(tile_x * 8, tile_y * 8, tile_pixmap)
        painter.end()
        self._pixmap_item.setPixmap(scene_pixmap)

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

    def display_tilemap_replica(self, source_scene):
        self.edit_tilemap2_scene.clear()
        self.overlay_items.clear()
        self._tilemap_items = {}
        
        if source_scene.items():
            item = source_scene.items()[0]
            pixmap = item.pixmap()
            
            self._pixmap_item = self.edit_tilemap2_scene.addPixmap(pixmap)
            self.edit_tilemap2_scene.setSceneRect(pixmap.rect())
            
            if hasattr(self.main_window, 'edit_tiles_tab'):
                tiles_tab = self.main_window.edit_tiles_tab
                tiles_tab.edit_tilemap_scene.clear()
                tiles_tab.edit_tilemap_scene.addPixmap(pixmap)
                tiles_tab.edit_tilemap_scene.setSceneRect(pixmap.rect())
                
                if self.main_window and hasattr(self.main_window, 'grid_manager'):
                    if self.main_window.grid_manager.is_grid_visible():
                        self.main_window.grid_manager.update_grid_for_view("tilemap_edit")
        
        if (hasattr(self, 'tilemap_data') and self.tilemap_data and 
            hasattr(self, 'tilemap_width') and self.tilemap_width > 0 and
            hasattr(self, 'tilemap_height') and self.tilemap_height > 0):
            
            for y in range(self.tilemap_height):
                for x in range(self.tilemap_width):
                    idx = y * self.tilemap_width + x
                    if idx >= len(self.tilemap_data) // 2:
                        continue
                    
                    entry = self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8)
                    palette_id = (entry >> 12) & 0xF
                    self.update_palette_overlay_for_tile(x, y, palette_id)
        
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_palettes")

    def toggle_tilemap_controls_enabled(self, enabled):
        self._set_tilemap_controls_enabled(enabled)

    def update_palette_overlay(self, source_scene, tilemap_data, tile_width, tile_height):
        if not tilemap_data:
            return

        self.tilemap_data = tilemap_data
        self.tilemap_width = tile_width
        self.tilemap_height = tile_height
        self.overlay_items.clear()
        self.tilemap_width_spin.setValue(tile_width)
        self.tilemap_height_spin.setValue(tile_height)

        self.enable_tilemap_controls()

        if not source_scene.items():
            return

        self.overlay_items.clear()
        self.edit_tilemap2_scene.clear()
        self._tilemap_items = {}

        pixmap_item = None
        if source_scene.items():
            for item in source_scene.items():
                if isinstance(item, QGraphicsPixmapItem):
                    pixmap_item = item
                    break
        
        if pixmap_item:
            pixmap = pixmap_item.pixmap()
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

        self.enable_tilemap_controls()

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

    def display_palette_colors(self, colors, enable_editor=True):
        self.palette_colors = [(r, g, b) for r, g, b in colors]
        self.draw_full_palette(self.palette_colors)
        
        self.current_editing_index = 0
        if len(self.palette_colors) > 0:
            r, g, b = self.palette_colors[0]
            self.color_editor.set_color(0, r, g, b)
            self.draw_selection_rectangle(0)
            
            self.color_editor.toggle_controls_enabled(enable_editor)
            
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("palettes")

    def draw_full_palette(self, colors):
        self.full_palette_scene.clear()
        tile_size = 12
        self.palette_rects = []
        self.selection_rect = None
        
        for i, (r, g, b) in enumerate(colors):
            if i >= 256:
                break
                
            row = i // 16
            col = i % 16
            
            rect = QGraphicsRectItem(col * tile_size, row * tile_size, tile_size, tile_size)
            rect.setPen(QPen(Qt.gray, 0.5))
            rect.setBrush(QBrush(QColor(r, g, b)))
            
            rect.setAcceptHoverEvents(True)
            rect.setAcceptedMouseButtons(Qt.LeftButton)
            
            def make_handler(idx, red, green, blue):
                def handler(event):
                    self.on_palette_color_clicked(idx, red, green, blue)
                    if idx < len(self.palette_rects):
                        QGraphicsRectItem.mousePressEvent(self.palette_rects[idx], event)
                    event.accept()
                return handler
            rect.mousePressEvent = make_handler(i, r, g, b)
            
            self.full_palette_scene.addItem(rect)
            self.palette_rects.append(rect)
            
            def make_click_handler(idx, red, green, blue):
                def handler(event):
                    self.on_palette_color_clicked(idx, red, green, blue)
                return handler
            
            rect.mousePressEvent = make_click_handler(i, r, g, b)

    def on_palette_color_clicked(self, index, r, g, b):
        self.finalize_color_editing()
        
        current_r, current_g, current_b = self.palette_colors[index]
        
        self.current_editing_index = index
        self.color_editor.set_color(index, current_r, current_g, current_b)
        self.draw_selection_rectangle(index)

    def _regenerate_preview(self):
        if not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        tiles_tab = self.main_window.edit_tiles_tab
        if not getattr(tiles_tab, 'tileset_img', None) or not getattr(tiles_tab, 'tilemap_data', None):
            return
        try:
            if hasattr(self.main_window, 'config_manager') and tiles_tab.tilemap_width > 0:
                self.main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(tiles_tab.tilemap_width))
                self.main_window.config_manager.set('CONVERSION', 'tilemap_height', str(tiles_tab.tilemap_height))

            preview_path = "temp/preview/preview.png"
            if os.path.exists(preview_path):
                from PIL import Image as PilImage
                with PilImage.open(preview_path) as f:
                    preview_img = f.copy()
                if preview_img.mode == 'P':
                    flat = []
                    for r, g, b in self.palette_colors:
                        flat.extend([int(r), int(g), int(b)])
                    while len(flat) < 768:
                        flat.append(0)
                    preview_img.putpalette(flat)
                    preview_img.save(preview_path)
                    if hasattr(self.main_window, 'refresh_preview_display'):
                        self.main_window.refresh_preview_display()
                    return

            from core.image_utils import create_gbagfx_preview
            save_preview     = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files',      False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)
            result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
            if result and hasattr(self.main_window, 'refresh_preview_display'):
                self.main_window.refresh_preview_display()
        except Exception as e:
            print(translator.tr("error_regenerating_preview").format(e=e))
    
    def _update_all_tiles(self):
        if not self.tilemap_data or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        
        tiles_tab = self.main_window.edit_tiles_tab
        
        for y in range(self.tilemap_height):
            for x in range(self.tilemap_width):
                tile_idx = y * self.tilemap_width + x
                if tile_idx >= len(self.tilemap_data) // 2:
                    continue
                
                tiles_tab.update_single_tile_visual(x, y)
                self.update_single_tile_replica(x, y)

    def _save_output_palette(self):
        import os
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        if self.main_window.current_bpp == 4:
            self._save_output_palette_4bpp(output_dir)
        else:
            self._save_output_palette_8bpp(output_dir)

    def _reload_tileset(self):
        if not self.main_window or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        
        tiles_tab = self.main_window.edit_tiles_tab
        
        if hasattr(tiles_tab, 'tileset_img') and tiles_tab.tileset_img:
            tiles_path = "output/tiles.png"
            if os.path.exists(tiles_path):
                try:
                    from PIL import Image as PilImage
                    with PilImage.open(tiles_path) as f:
                        new_tileset_img = f.copy()
                    tiles_tab.display_tileset(new_tileset_img)
                    
                except Exception as e:
                     print(translator.tr("error_reloading_tileset").format(e=e))

    def _save_output_palette_4bpp(self, output_dir):
            import os

            for slot_idx in range(16):
                start_idx = slot_idx * 16
                end_idx = start_idx + 16
                
                slot_colors = self.palette_colors[start_idx:end_idx]
                
                is_used = any(color != (0, 0, 0) for color in slot_colors)
                
                filename = f"palette_{slot_idx:02d}.pal"
                filepath = os.path.join(output_dir, filename)
                
                if is_used:
                    with open(filepath, "w", encoding='utf-8') as f:
                        f.write("JASC-PAL\n0100\n16\n")
                        for r, g, b in slot_colors:
                            f.write(f"{int(r)} {int(g)} {int(b)}\n")
                else:
                    if os.path.exists(filepath):
                        os.remove(filepath)
    
    def _save_output_palette_8bpp(self, output_dir):
        start_idx = 0
        for i in range(1, len(self.palette_colors)):
            if self.palette_colors[i] != (0, 0, 0):
                start_idx = i
                break

        last_idx = start_idx
        for i in range(start_idx, len(self.palette_colors)):
            if self.palette_colors[i] != (0, 0, 0):
                last_idx = i

        colors_to_save = self.palette_colors[start_idx:last_idx + 1]

        for f in os.listdir(output_dir):
            if f.startswith("palette_") and f.endswith(".pal"):
                os.remove(os.path.join(output_dir, f))

        filename = f"palette_{start_idx:03d}.pal"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding='utf-8') as f:
            f.write("JASC-PAL\n0100\n")
            f.write(f"{len(colors_to_save)}\n")
            for r, g, b in colors_to_save:
                f.write(f"{r} {g} {b}\n")

    def _save_and_update_all(self):       
            preview_palette_path = "temp/preview/palette.pal"
            os.makedirs(os.path.dirname(preview_palette_path), exist_ok=True)
            
            try:
                with open(preview_palette_path, 'w', encoding='utf-8') as f:
                    f.write("JASC-PAL\n0100\n256\n")
                    for r, g, b in self.palette_colors:
                        f.write(f"{r} {g} {b}\n")
            except Exception as e:
                 print(translator.tr("error_saving_preview_palette").format(e=e))
            
            self._save_output_palette()
            self._update_output_tiles()
            
            if (self.main_window and hasattr(self.main_window, 'preview_tab')):
                self.main_window.preview_tab.palette_colors = self.palette_colors.copy()
                self.main_window.preview_tab.display_palette_colors(self.palette_colors)
            
            self._regenerate_preview()
    
    def _update_output_tiles(self):
        from PIL import Image

        mw = self.main_window
        tiles_path = "output/tiles.png"
        if not os.path.exists(tiles_path):
            return

        try:
            with Image.open(tiles_path) as f:
                tiles_img = f.copy()
            if tiles_img.mode != 'P':
                return

            is_8bpp = getattr(mw, 'current_bpp', 4) == 8
            if is_8bpp:
                src_colors = self.palette_colors
            else:
                selected_str = mw.config_manager.get('CONVERSION', 'selected_palettes', '0')
                selected_slots = [s.strip() for s in selected_str.split(',') if s.strip()]
                if len(selected_slots) > 1:
                    return
                slot = int(selected_slots[0]) if selected_slots else 0
                src_colors = self.palette_colors[slot * 16 : slot * 16 + 16]
                src_colors = list(src_colors) + [(0, 0, 0)] * (256 - len(src_colors))

            flat_palette = []
            for r, g, b in src_colors:
                flat_palette.extend([int(r), int(g), int(b)])
            while len(flat_palette) < 768:
                flat_palette.extend([0, 0, 0])

            tiles_img.putpalette(flat_palette[:768])
            tiles_img.save(tiles_path)

            if hasattr(mw, 'edit_tiles_tab'):
                with Image.open(tiles_path) as f:
                    updated = f.copy()
                et = mw.edit_tiles_tab
                et.tileset_img = updated
                et.tileset_img_original = updated
                total_tiles = (updated.width // 8) * (updated.height // 8)
                w = et.tiles_per_row if et.tiles_per_row > 0 else updated.width // 8
                h = (total_tiles + w - 1) // w
                et.render_tileset_with_padding(w, h, total_tiles)

        except Exception as e:
            print(translator.tr("error_updating_output_tiles").format(e=e))
        
    def finalize_color_editing(self):
        if (self.color_editor.has_changes() and 
            self.current_editing_index >= 0 and
            self.current_editing_index < len(self.palette_colors)):
            
            current_color = self.color_editor.get_current_color()
            original_color = self.color_editor.original_color
            
            if self.main_window and hasattr(self.main_window, 'history_manager'):
                self.main_window.history_manager.record_state(
                    state_type='color_edit',
                    editor_type='palettes',
                    data={
                        'index': self.current_editing_index,
                        'old_color': original_color,
                        'new_color': current_color
                    },
                    description=f"Color {self.current_editing_index} edited: RGB{original_color} → RGB{current_color}"
                )
            
            self.color_editor.original_color = current_color
            self.palette_colors[self.current_editing_index] = current_color
            
            rect = self.palette_rects[self.current_editing_index]
            rect.setBrush(QBrush(QColor(*current_color)))
            
            self._save_and_update_all()
            
    def draw_selection_rectangle(self, index):
        if self.selection_rect:
            self.full_palette_scene.removeItem(self.selection_rect)
        
        if index < 0 or index >= len(self.palette_rects):
            return
            
        rect = self.palette_rects[index]
        
        self.selection_rect = self.full_palette_scene.addRect(
            rect.rect().x(),
            rect.rect().y(),
            rect.rect().width(),
            rect.rect().height(),
            QPen(QColor(255, 255, 0), 1),
            Qt.NoBrush
        )
        self.selection_rect.setZValue(1)

    def update_selected_color(self, index, r, g, b, record_history=False):
        if index < 0 or index >= len(self.palette_rects):
            return
        
        rect = self.palette_rects[index]
        rect.setBrush(QBrush(QColor(r, g, b)))
        
        self.palette_colors[index] = (r, g, b)
        
        if (self.main_window and hasattr(self.main_window, 'preview_tab')):
            if hasattr(self.main_window.preview_tab, 'palette_colors'):
                self.main_window.preview_tab.palette_colors[index] = (r, g, b)
            
            self.main_window.preview_tab.display_palette_colors(self.main_window.preview_tab.palette_colors)

    def apply_color_change(self, index, r, g, b):
        if index < 0 or index >= len(self.palette_rects):
            return
        
        rect = self.palette_rects[index]
        rect.setBrush(QBrush(QColor(r, g, b)))
        
        self.palette_colors[index] = (r, g, b)
        
        if index == self.current_editing_index:
            self.color_editor.set_color(index, r, g, b)
        
        self._save_and_update_all()

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
