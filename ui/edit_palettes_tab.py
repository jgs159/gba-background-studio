# ui/edit_palettes_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QGraphicsView, QGraphicsScene,
    QHBoxLayout, QGraphicsPixmapItem, QFrame, QSlider, QSizePolicy, QGridLayout,
    QGraphicsRectItem, QLineEdit
)
from PySide6.QtGui import QFont, QBrush, QPen, QColor, QPainter, QPixmap, QIntValidator
from PySide6.QtCore import Qt, Signal, QTimer

from PIL import Image as PilImage
from core.image_utils import pil_to_qimage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared
from ui.palette_grid_view import PaletteGridView
from ui.color_editor import ColorEditor


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
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        palettes_label = QLabel("Palettes")
        palettes_label.setFont(QFont("Arial", 9, QFont.Bold))
        palettes_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(palettes_label)

        height_container = QWidget()
        height_container.setFixedHeight(260)
        top_layout = QHBoxLayout(height_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        left_container = self.create_left_palette_container()
        top_layout.addWidget(left_container)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background: #ccc;")
        separator.setFixedWidth(1)
        top_layout.addWidget(separator)
        
        right_container = self.create_right_palette_container()
        top_layout.addWidget(right_container)

        layout.addWidget(height_container)

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
        layout.addWidget(self.grid_view)
        
        return container

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
        self.full_palette_view.setStyleSheet("QGraphicsView { background: #f9f9f9; border: 1px solid #ccc; }")
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

        self.edit_tilemap2_view = CustomGraphicsView()
        self.edit_tilemap2_scene = QGraphicsScene()
        self.edit_tilemap2_view.setScene(self.edit_tilemap2_scene)
        self.edit_tilemap2_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tilemap2_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tilemap2_view.setStyleSheet("QGraphicsView { background: #e0e0e0; border: 1px solid #ccc; }")
        self.edit_tilemap2_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.edit_tilemap2_view.setMouseTracking(True)
        layout.addWidget(self.edit_tilemap2_view)

        return container

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

    def setup_tilemap_interaction(self):
        self.edit_tilemap2_view.on_tile_drawing = self.on_tilemap_drawing
        self.edit_tilemap2_view.on_tile_selected = self.on_tilemap_right_click
        self.edit_tilemap2_view.on_tile_hover = self.on_tilemap_hover
        self.edit_tilemap2_view.on_tile_leave = self.on_tilemap_leave

    def on_palette_grid_click(self, event):
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
        self.palette_colors = [(r, g, b) for r, g, b in colors]
        self.draw_full_palette(self.palette_colors)
        
        self.current_editing_index = 0
        if len(self.palette_colors) > 0:
            r, g, b = self.palette_colors[0]
            self.color_editor.set_color(0, r, g, b)
            self.draw_selection_rectangle(0)
        
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
            
            if (self.main_window and hasattr(self.main_window, 'preview_tab')):
                if hasattr(self.main_window.preview_tab, 'palette_colors'):
                    self.main_window.preview_tab.palette_colors[self.current_editing_index] = current_color
                
                self.main_window.preview_tab.display_palette_colors(self.main_window.preview_tab.palette_colors)

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
        
        if (self.main_window and hasattr(self.main_window, 'preview_tab')):
            if hasattr(self.main_window.preview_tab, 'palette_colors'):
                self.main_window.preview_tab.palette_colors[index] = (r, g, b)
            
            self.main_window.preview_tab.display_palette_colors(self.main_window.preview_tab.palette_colors)

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
