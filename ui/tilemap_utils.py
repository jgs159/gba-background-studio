# ui/tilemap_utils.py
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt
from core.config import ROT_SIZES, ROT_SIZES_SET


class TilemapUtils:
    def setup_tilemap_interaction(self):
        self.tilemap_view.on_tile_drawing  = self.on_tilemap_drawing
        self.tilemap_view.on_tile_selected = self.on_tilemap_right_click
        self.tilemap_view.on_tile_hover    = self.on_tilemap_hover
        self.tilemap_view.on_tile_leave    = self.on_tilemap_leave
        self.tilemap_view.on_tile_release  = self.on_tilemap_release

    def on_tilemap_release(self):
        pass

    def on_tilemap_hover(self, tile_x, tile_y):
        scene_rect  = self.tilemap_scene.sceneRect()
        max_tile_x  = int(scene_rect.width())  // 8 - 1
        max_tile_y  = int(scene_rect.height()) // 8 - 1

        if 0 <= tile_x <= max_tile_x and 0 <= tile_y <= max_tile_y:
            self.last_hover_pos = (tile_x, tile_y)
            self.main_window.hover_manager.update_hover(tile_x, tile_y, self.tilemap_view)
            self.update_status_bar(tile_x, tile_y)
        else:
            self.last_hover_pos = (-1, -1)
            self.main_window.hover_manager.hide_hover(self.tilemap_view)
            self.update_status_bar(-1, -1)

    def on_tilemap_leave(self):
        self.main_window.hover_manager.hide_hover(self.tilemap_view)
        self.last_hover_pos = (-1, -1)
        self.update_status_bar(-1, -1)

    def on_tilemap_shift(self, direction):
        if not self.tilemap_data:
            return

        w = self.tilemap_width
        h = self.tilemap_height
        is_cyclic = self.cyclic_checkbox.isChecked()
        EMPTY = b'\x00\x00'
        old_data = self.tilemap_data

        if w > 32:
            from core.final_assets import revert_gba_tilemap_reorganization
            linear = bytearray(revert_gba_tilemap_reorganization(self.tilemap_data, w, h, w, h))
        else:
            linear = bytearray(self.tilemap_data)

        def get(x, y):  return linear[(y * w + x) * 2 : (y * w + x) * 2 + 2]
        def set_(x, y, v): linear[(y * w + x) * 2 : (y * w + x) * 2 + 2] = v

        if direction == 'up':
            first_row = [bytes(get(x, 0)) for x in range(w)]
            for y in range(h - 1):
                for x in range(w):
                    set_(x, y, get(x, y + 1))
            for x in range(w):
                set_(x, h - 1, first_row[x] if is_cyclic else EMPTY)

        elif direction == 'down':
            last_row = [bytes(get(x, h - 1)) for x in range(w)]
            for y in range(h - 1, 0, -1):
                for x in range(w):
                    set_(x, y, get(x, y - 1))
            for x in range(w):
                set_(x, 0, last_row[x] if is_cyclic else EMPTY)

        elif direction == 'left':
            first_col = [bytes(get(0, y)) for y in range(h)]
            for x in range(w - 1):
                for y in range(h):
                    set_(x, y, get(x + 1, y))
            for y in range(h):
                set_(w - 1, y, first_col[y] if is_cyclic else EMPTY)

        elif direction == 'right':
            last_col = [bytes(get(w - 1, y)) for y in range(h)]
            for x in range(w - 1, 0, -1):
                for y in range(h):
                    set_(x, y, get(x - 1, y))
            for y in range(h):
                set_(0, y, last_col[y] if is_cyclic else EMPTY)

        if w > 32:
            from core.final_assets import reorganize_tilemap_for_gba_bg
            tile_list = []
            for i in range(w * h):
                entry = int.from_bytes(linear[i*2:i*2+2], 'little')
                tile_list.append((entry & 0x3FF, (entry >> 10) & 1, (entry >> 11) & 1, (entry >> 12) & 0xF))
            reorganized = reorganize_tilemap_for_gba_bg(tile_list, w * 8, h * 8)
            final = bytearray()
            for tile_id, hf, vf, pal in reorganized:
                e = (tile_id & 0x3FF) | (hf << 10) | (vf << 11) | (pal << 12)
                final.extend(e.to_bytes(2, 'little'))
            new_data = bytes(final)
        else:
            new_data = bytes(linear)

        self.tilemap_data = new_data

        if hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tilemap_shift',
                editor_type='tiles',
                data={'old_data': old_data, 'new_data': new_data, 'w': w, 'h': h},
                description=f"Tilemap shifted {direction}"
            )

        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(new_data)

        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            other = getattr(self.main_window, attr, None)
            if other and other is not self:
                other.tilemap_data = new_data

        save_preview = keep_transparent = False
        if hasattr(self.main_window, 'config_manager'):
            save_preview     = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)

        from core.image_utils import create_gbagfx_preview
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()

    def on_tilemap_resize(self):
        new_w = self.tilemap_width_spin.value()
        new_h = self.tilemap_height_spin.value()

        if not self.tilemap_data or (new_w == self.tilemap_width and new_h == self.tilemap_height):
            return

        is_rot = getattr(self.main_window, 'current_rotation_mode', False) if self.main_window else False
        if is_rot:
            if (new_w, new_h) not in ROT_SIZES_SET:
                chosen = self._ask_rotation_size(new_w, new_h)
                self.tilemap_width_spin.setValue(self.tilemap_width)
                self.tilemap_height_spin.setValue(self.tilemap_height)
                if chosen is None:
                    return
                new_w, new_h = chosen
                self.tilemap_width_spin.setValue(new_w)
                self.tilemap_height_spin.setValue(new_h)
            self._resize_rotation_tilemap(new_w, new_h)
            return

        old_w = self.tilemap_width
        old_h = self.tilemap_height
        old_data = self.tilemap_data

        save_preview = False
        keep_transparent = False
        if hasattr(self.main_window, 'config_manager'):
            save_preview    = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)

        resize_performed = False
        final_new_w = new_w
        final_new_h = new_h
        final_new_data = None

        requires_gba_adjustment = False
        adjusted_w = new_w
        adjusted_h = new_h

        if new_w > 32:
            if new_w != 64:
                requires_gba_adjustment = True
                adjusted_w = 64
            if new_h % 32 != 0:
                requires_gba_adjustment = True
                adjusted_h = ((new_h + 31) // 32) * 32

        if requires_gba_adjustment:
            from ui.dialogs.gba_compatibility_dialog import GBACompatibilityDialog
            dlg = GBACompatibilityDialog(new_w, new_h, adjusted_w, adjusted_h, self)
            if dlg.exec():
                final_new_w = adjusted_w
                final_new_h = adjusted_h
                self.tilemap_width_spin.setValue(final_new_w)
                self.tilemap_height_spin.setValue(final_new_h)

                # Adjusted dimensions equal current ones — nothing to change
                if final_new_w == old_w and final_new_h == old_h:
                    return

                # old_data may be GBA-reorganized if old_w > 32 — revert to linear first
                if old_w > 32:
                    from core.final_assets import revert_gba_tilemap_reorganization
                    linear_old = revert_gba_tilemap_reorganization(old_data, old_w, old_h, old_w, old_h)
                else:
                    linear_old = old_data

                new_data = bytearray(b'\x00\x00' * (final_new_w * final_new_h))
                for y in range(min(old_h, final_new_h)):
                    for x in range(min(old_w, final_new_w)):
                        old_idx = y * old_w + x
                        new_idx = y * final_new_w + x
                        if old_idx < len(linear_old) // 2:
                            new_data[new_idx*2:new_idx*2+2] = linear_old[old_idx*2:old_idx*2+2]

                from core.final_assets import reorganize_tilemap_for_gba_bg
                tile_list = []
                for i in range(final_new_w * final_new_h):
                    entry  = int.from_bytes(new_data[i*2:i*2+2], 'little')
                    tile_list.append((entry & 0x3FF, (entry >> 10) & 1, (entry >> 11) & 1, (entry >> 12) & 0xF))

                reorganized = reorganize_tilemap_for_gba_bg(tile_list, final_new_w * 8, final_new_h * 8)

                final_data = bytearray()
                for tile_id, h_flip, v_flip, pal in reorganized:
                    entry = tile_id & 0x3FF
                    if h_flip: entry |= (1 << 10)
                    if v_flip: entry |= (1 << 11)
                    entry |= (pal << 12)
                    final_data.extend(entry.to_bytes(2, 'little'))

                final_new_data = bytes(final_data)
                resize_performed = True
            else:
                self.tilemap_width_spin.setValue(self.tilemap_width)
                self.tilemap_height_spin.setValue(self.tilemap_height)
                return

        elif self.tilemap_width > 32 and new_w <= 32:
            from core.final_assets import revert_gba_tilemap_reorganization
            final_new_data = revert_gba_tilemap_reorganization(
                self.tilemap_data, self.tilemap_width, self.tilemap_height, new_w, new_h
            )
            final_new_w = new_w
            final_new_h = new_h
            resize_performed = True

        else:
            min_w = min(new_w, old_w)
            min_h = min(new_h, old_h)
            new_data = bytearray()

            for y in range(min_h):
                start = y * old_w * 2
                new_data.extend(old_data[start : start + min_w * 2])
                if new_w > old_w:
                    new_data.extend(b'\x00\x00' * (new_w - old_w))

            if new_h > old_h:
                new_data.extend(b'\x00\x00' * new_w * (new_h - old_h))

            final_new_data = bytes(new_data)
            final_new_w = new_w
            final_new_h = new_h
            resize_performed = True

        if resize_performed and final_new_w > 32 and old_w <= 32 and not requires_gba_adjustment:
            min_w = min(old_w, final_new_w)
            min_h = min(old_h, final_new_h)
            linear_data = bytearray(b'\x00\x00' * (final_new_w * final_new_h))
            for y in range(min_h):
                for x in range(min_w):
                    old_idx = y * old_w + x
                    new_idx = y * final_new_w + x
                    if old_idx < len(old_data) // 2:
                        linear_data[new_idx*2:new_idx*2+2] = old_data[old_idx*2:old_idx*2+2]

            from core.final_assets import reorganize_tilemap_for_gba_bg
            tile_list = []
            for i in range(final_new_w * final_new_h):
                entry = int.from_bytes(linear_data[i*2:i*2+2], 'little')
                tile_list.append((entry & 0x3FF, (entry >> 10) & 1, (entry >> 11) & 1, (entry >> 12) & 0xF))

            reorganized = reorganize_tilemap_for_gba_bg(tile_list, final_new_w * 8, final_new_h * 8)

            final_data = bytearray()
            for tile_id, h_flip, v_flip, pal in reorganized:
                entry = tile_id & 0x3FF
                if h_flip: entry |= (1 << 10)
                if v_flip: entry |= (1 << 11)
                entry |= (pal << 12)
                final_data.extend(entry.to_bytes(2, 'little'))
            final_new_data = bytes(final_data)

        if not resize_performed:
            return

        self.tilemap_data   = final_new_data
        self.tilemap_width  = final_new_w
        self.tilemap_height = final_new_h
        self.tilemap_width_spin.setValue(final_new_w)
        self.tilemap_height_spin.setValue(final_new_h)

        import os
        os.makedirs('output', exist_ok=True)
        with open(os.path.join('output', 'map.bin'), 'wb') as f:
            f.write(final_new_data)

        if hasattr(self.main_window, 'config_manager'):
            self.main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(final_new_w))
            self.main_window.config_manager.set('CONVERSION', 'tilemap_height', str(final_new_h))

        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            other = getattr(self.main_window, attr, None)
            if other and other is not self:
                other.tilemap_data   = final_new_data
                other.tilemap_width  = final_new_w
                other.tilemap_height = final_new_h
                other.tilemap_width_spin.setValue(final_new_w)
                other.tilemap_height_spin.setValue(final_new_h)

        if hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tilemap_resize',
                editor_type='palettes',
                data={
                    'old_w': old_w, 'old_h': old_h,
                    'new_w': final_new_w, 'new_h': final_new_h,
                    'old_data': old_data, 'new_data': final_new_data
                },
                description=f"Tilemap resized from {old_w}x{old_h} to {final_new_w}x{final_new_h}"
            )

        from core.image_utils import create_gbagfx_preview
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)

        if result and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()

    def build_tilemap_toolbar(self):
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_frame.setStyleSheet(
            "QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }"
        )
        controls_frame.setFixedHeight(28)

        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(1)
        controls_layout.setContentsMargins(3, 3, 3, 3)

        row = QHBoxLayout()
        row.setSpacing(3)
        row.setContentsMargins(0, 0, 0, 0)
        row.setAlignment(Qt.AlignLeft)

        def _label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("QLabel { border: none; }")
            return lbl

        row.addWidget(_label("Width:"))
        self.tilemap_width_spin = QSpinBox()
        self.tilemap_width_spin.setRange(1, 999)
        self.tilemap_width_spin.setValue(32)
        self.tilemap_width_spin.setFixedWidth(45)
        self.tilemap_width_spin.setFixedHeight(18)
        self.tilemap_width_spin.setStyleSheet("QSpinBox { font-size: 8pt; }")
        row.addWidget(self.tilemap_width_spin)

        row.addWidget(_label("Height:"))
        self.tilemap_height_spin = QSpinBox()
        self.tilemap_height_spin.setRange(1, 999)
        self.tilemap_height_spin.setValue(32)
        self.tilemap_height_spin.setFixedWidth(45)
        self.tilemap_height_spin.setFixedHeight(18)
        self.tilemap_height_spin.setStyleSheet("QSpinBox { font-size: 8pt; }")
        row.addWidget(self.tilemap_height_spin)

        self.resize_button = QPushButton("Resize")
        self.resize_button.setFixedWidth(50)
        self.resize_button.setFixedHeight(20)
        self.resize_button.setStyleSheet("QPushButton { font-size: 8pt; padding: 0px; }")
        self.resize_button.clicked.connect(self.on_tilemap_resize)
        row.addWidget(self.resize_button)

        btn_style = "QPushButton { font-weight: bold; padding: 0px; font-size: 7pt; }"
        self.btn_up    = QPushButton("↑")
        self.btn_left  = QPushButton("←")
        self.btn_right = QPushButton("→")
        self.btn_down  = QPushButton("↓")
        for btn in (self.btn_up, self.btn_left, self.btn_right, self.btn_down):
            btn.setFixedSize(20, 20)
            btn.setStyleSheet(btn_style)

        self.btn_up.clicked.connect(lambda: self.on_tilemap_shift("up"))
        self.btn_down.clicked.connect(lambda: self.on_tilemap_shift("down"))
        self.btn_left.clicked.connect(lambda: self.on_tilemap_shift("left"))
        self.btn_right.clicked.connect(lambda: self.on_tilemap_shift("right"))

        self.move_label = QLabel("Move")
        self.move_label.setStyleSheet("QLabel { border: none; }")

        row.addWidget(self.btn_left)
        row.addWidget(self.btn_up)
        row.addWidget(self.move_label)
        row.addWidget(self.btn_down)
        row.addWidget(self.btn_right)

        self.cyclic_checkbox = QCheckBox("Cyclic Shift")
        self.cyclic_checkbox.setStyleSheet("QCheckBox { font-size: 8pt; }")
        self.cyclic_checkbox.setFixedHeight(18)
        row.addWidget(self.cyclic_checkbox)

        controls_layout.addLayout(row)

        self._set_tilemap_controls_enabled(False)
        return controls_frame

    def _set_tilemap_controls_enabled(self, enabled: bool):
        for widget in (
            self.tilemap_width_spin, self.tilemap_height_spin,
            self.resize_button,
            self.btn_up, self.btn_down, self.btn_left, self.btn_right,
            self.cyclic_checkbox,
        ):
            widget.setEnabled(enabled)

    def enable_tilemap_controls(self):
        self._set_tilemap_controls_enabled(True)

    def _ask_rotation_size(self, attempted_w, attempted_h):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QDialogButtonBox
        dlg = QDialog(self.main_window if self.main_window else None)
        dlg.setWindowTitle("Invalid Rotation Mode Size")
        dlg.setFixedWidth(320)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(
            f"<b>{attempted_w}×{attempted_h}</b> is not a valid Rotation/Scaling mode size.<br>"
            "Please choose one of the valid sizes:"
        ))
        lst = QListWidget()
        labels = ["16×16 (128×128 px)", "32×32 (256×256 px)",
                  "64×64 (512×512 px)", "128×128 (1024×1024 px)"]
        for lbl in labels:
            lst.addItem(lbl)
        lst.setCurrentRow(0)
        layout.addWidget(lst)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        if dlg.exec() != QDialog.Accepted:
            return None
        return ROT_SIZES[lst.currentRow()]

    def _resize_rotation_tilemap(self, new_w, new_h):
        old_w, old_h = self.tilemap_width, self.tilemap_height
        old_data = self.tilemap_data

        new_data = bytearray(new_w * new_h)
        for y in range(min(old_h, new_h)):
            for x in range(min(old_w, new_w)):
                new_data[y * new_w + x] = old_data[y * old_w + x]

        new_data = bytes(new_data)
        self.tilemap_data  = new_data
        self.tilemap_width  = new_w
        self.tilemap_height = new_h
        self.tilemap_width_spin.setValue(new_w)
        self.tilemap_height_spin.setValue(new_h)

        import os
        os.makedirs('output', exist_ok=True)
        with open(os.path.join('output', 'map.bin'), 'wb') as f:
            f.write(new_data)

        if hasattr(self.main_window, 'config_manager'):
            self.main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(new_w))
            self.main_window.config_manager.set('CONVERSION', 'tilemap_height', str(new_h))

        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            other = getattr(self.main_window, attr, None)
            if other and other is not self:
                other.tilemap_data   = new_data
                other.tilemap_width  = new_w
                other.tilemap_height = new_h
                other.tilemap_width_spin.setValue(new_w)
                other.tilemap_height_spin.setValue(new_h)

        if hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tilemap_resize', editor_type='tiles',
                data={'old_w': old_w, 'old_h': old_h,
                      'new_w': new_w, 'new_h': new_h,
                      'old_data': old_data, 'new_data': new_data},
                description=f"Tilemap resized from {old_w}x{old_h} to {new_w}x{new_h}"
            )

        save_preview = keep_transparent = False
        if hasattr(self.main_window, 'config_manager'):
            save_preview     = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)

        from core.image_utils import create_gbagfx_preview
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()
