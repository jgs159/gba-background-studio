# ui/shared_utils.py
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._is_drawing = False
        self._had_drawing = False
        self.on_tile_drawing = None
        self.on_tile_selected = None
        self.on_tile_hover = None
        self.on_tile_leave = None
        self.on_tile_release = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_drawing = True
            pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                scene_rect = self.scene().sceneRect()
                if (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
                    tile_x = max(0, min(int(pos.x()) // 8, int(scene_rect.width()) // 8 - 1))
                    tile_y = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))
                    if self.on_tile_drawing:
                        self.on_tile_drawing(tile_x, tile_y)
                        self._had_drawing = True
            event.accept()
        elif event.button() == Qt.RightButton:
            pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                scene_rect = self.scene().sceneRect()
                if (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
                    tile_x = max(0, min(int(pos.x()) // 8, int(scene_rect.width()) // 8 - 1))
                    tile_y = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))
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

        scene_rect = self.scene().sceneRect()
        if not (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
            if self.on_tile_leave:
                self.on_tile_leave()
            super().mouseMoveEvent(event)
            return

        tile_x = max(0, min(int(pos.x()) // 8, int(scene_rect.width()) // 8 - 1))
        tile_y = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))

        if self.on_tile_hover:
            self.on_tile_hover(tile_x, tile_y)

        if self._is_drawing and (event.buttons() & Qt.LeftButton) and self.on_tile_drawing:
            self.on_tile_drawing(tile_x, tile_y)
            self._had_drawing = True
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
            if self._had_drawing and self.on_tile_release:
                self.on_tile_release()
            self._had_drawing = False
        super().mouseReleaseEvent(event)


def update_status_bar_shared(main_window, selection_type, selection_id, tile_x, tile_y, 
                           tilemap_data=None, tilemap_width=0, tilemap_height=0, 
                           tile_id=None, palette_id=None, flip_state=None):
    if not main_window or not hasattr(main_window, 'custom_status_bar'):
        return
    
    if (tile_x, tile_y) == (-1, -1):
        tilemap_display = "(-, -)"
        flip_state_display = "None"
    else:
        if tile_id is None and tilemap_data:
            tile_index = tile_y * tilemap_width + tile_x
            if 0 <= tile_index < len(tilemap_data) // 2:
                entry = tilemap_data[tile_index * 2] | (tilemap_data[tile_index * 2 + 1] << 8)
                tile_id = entry & 0x3FF
        
        if palette_id is None and tilemap_data:
            tile_index = tile_y * tilemap_width + tile_x
            if 0 <= tile_index < len(tilemap_data) // 2:
                entry = tilemap_data[tile_index * 2] | (tilemap_data[tile_index * 2 + 1] << 8)
                palette_id = (entry >> 12) & 0xF
                h_flip = bool(entry & (1 << 10))
                v_flip = bool(entry & (1 << 11))
                if h_flip and v_flip:
                    flip_state = "XY"
                elif h_flip:
                    flip_state = "X"
                elif v_flip:
                    flip_state = "Y"
                else:
                    flip_state = "None"
        
        tilemap_display = f"({tile_x}, {tile_y})"
        flip_state_display = flip_state if flip_state is not None else "None"
    
    tile_display = str(tile_id) if tile_id is not None else "-"
    palette_display = f"{palette_id:X}" if palette_id is not None else "-"
    selection_display = str(selection_id) if selection_id is not None else "-"
    
    zoom_level = int(main_window.zoom_level) if hasattr(main_window, 'zoom_level') else 100
    
    main_window.custom_status_bar.update_status(
        selection_type=selection_type,
        selection_id=selection_display,
        tilemap_pos=(tile_x, tile_y),
        tile_id=tile_display,
        palette_id=palette_display,
        flip_state=flip_state if flip_state is not None else "None",
        zoom_level=zoom_level
    )
