# ui/main_window/file_ops.py
import os
import shutil
from PIL import Image as PilImage
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QSpinBox, QPushButton, 
                               QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap, QBrush, QColor
from core.image_utils import pil_to_qimage
from core.palette_utils import generate_grayscale_palette


class PaletteApplyDialog(QDialog):
    ADD     = "add"
    SYNC    = "sync"
    REPLACE = "replace"

    def __init__(self, parent=None, need_bpp=False):
        super().__init__(parent)
        self.setWindowTitle("Apply Palette")
        self.setModal(True)
        self.setFixedSize(400, 200 if need_bpp else 160)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(
            "How do you want to apply the loaded palette?"
        ))

        from PySide6.QtWidgets import QRadioButton, QButtonGroup, QComboBox
        self._add_radio     = QRadioButton("Add — write colors at the specified index (keep the rest)")
        self._sync_radio    = QRadioButton("Sync — remap tileset pixels to match new palette")
        self._replace_radio = QRadioButton("Replace — reset to black, then apply at specified index")
        self._add_radio.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self._add_radio)
        grp.addButton(self._sync_radio)
        grp.addButton(self._replace_radio)
        layout.addWidget(self._add_radio)
        layout.addWidget(self._sync_radio)
        layout.addWidget(self._replace_radio)

        self._bpp_combo = None
        if need_bpp:
            current_bpp = getattr(parent, 'current_bpp', 4) if parent else 4
            bpp_row = QHBoxLayout()
            bpp_row.addWidget(QLabel("Color depth:"))
            self._bpp_combo = QComboBox()
            self._bpp_combo.addItems(["4bpp", "8bpp"])
            if current_bpp == 8:
                self._bpp_combo.setCurrentIndex(1)
                self._bpp_combo.setEnabled(False)
            bpp_row.addWidget(self._bpp_combo)
            layout.addLayout(bpp_row)

        btn_row = QHBoxLayout()
        ok_btn     = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def get_values(self):
        mode = self.ADD if self._add_radio.isChecked() else (self.SYNC if self._sync_radio.isChecked() else self.REPLACE)
        bpp  = 8 if (self._bpp_combo and self._bpp_combo.currentIndex() == 1) else 4
        return mode, bpp


class PaletteLoadDialog(QDialog):
    def __init__(self, parent=None, palette_length=256):
        super().__init__(parent)
        self.setWindowTitle("Configure Palette Load")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        index_layout = QHBoxLayout()
        index_layout.addWidget(QLabel("Start Index (0-255):"))
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 255)
        self.index_spin.setValue(0)
        index_layout.addWidget(self.index_spin)
        layout.addLayout(index_layout)
        
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel(f"Length (1-{palette_length}):"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(1, palette_length)
        self.length_spin.setValue(palette_length)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.index_spin.valueChanged.connect(self._update_length_max)
        self.palette_length = palette_length
    
    def _update_length_max(self):
        max_length = min(self.palette_length, 256 - self.index_spin.value())
        self.length_spin.setMaximum(max_length)
        if self.length_spin.value() > max_length:
            self.length_spin.setValue(max_length)
    
    def get_values(self):
        return self.index_spin.value(), self.length_spin.value()
        
def load_last_output_files(main_window):
    tiles_path = "output/tiles.png"
    preview_path = "temp/preview/preview.png"
    palette_path = "temp/preview/palette.pal"
    tilemap_path = "output/map.bin"
    
    if not (os.path.exists(tiles_path) and os.path.exists(tilemap_path)):
        return False
    
    try:
        with PilImage.open(tiles_path) as f:
            tiles_img = f.copy()
        main_window.display_tileset(tiles_img)
        main_window.menu_bar.action_save_tileset.setEnabled(True)
        main_window.menu_bar.action_open_tilemap.setEnabled(True)
        main_window.menu_bar.action_new_tilemap.setEnabled(True)
        main_window.tileset_from_conversion = True
        selected = main_window.config_manager.get('CONVERSION', 'selected_palettes', '0')
        main_window.conversion_palette_count = len([p for p in selected.split(',') if p.strip()]) if main_window.current_bpp == 4 else 16
        is_8bpp = main_window.current_bpp == 8
        palette_count = len([p for p in selected.split(',') if p.strip()])
        
        with open(tilemap_path, 'rb') as f:
            tilemap_data = f.read()
        main_window.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path if os.path.exists(preview_path) else None)
        main_window.menu_bar.action_save_tilemap.setEnabled(True)
        main_window.menu_bar.action_save_selection.setEnabled(False)

        if hasattr(main_window, 'history_manager'):
            main_window.history_manager.clear()

        if os.path.exists(preview_path):
            with PilImage.open(preview_path) as f:
                preview_img = f.copy()
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            main_window.preview_tab.preview_image_scene.clear()
            main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
            
            if hasattr(main_window, 'edit_palettes_tab'):
                preview_scene = main_window.preview_tab.preview_image_scene
                if preview_scene.items():
                    main_window.edit_palettes_tab.display_tilemap_replica(preview_scene)
            
            from .view_ops import apply_zoom_to_view
            apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, main_window.zoom_level / 100.0)
            if main_window.preview_tab.preview_image_scene.items():
                main_window.preview_tab.preview_image_view.centerOn(main_window.preview_tab.preview_image_scene.items()[0])
        
        if os.path.exists(palette_path):
            palette_colors = [(0, 0, 0)] * 256
            try:
                with open(palette_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f 
                            if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
                if lines:
                    color_count = int(lines[0])
                    for i in range(1, min(1 + color_count, 257)):
                        r, g, b = map(int, lines[i].split())
                        palette_colors[i - 1] = (r, g, b)
                main_window.preview_tab.display_palette_colors(palette_colors)
                if hasattr(main_window, 'edit_palettes_tab'):
                    main_window.edit_palettes_tab.display_palette_colors(palette_colors)
            except Exception as e:
                print(f"Error loading palette: {e}")
                grayscale_colors = generate_grayscale_palette()
                main_window.preview_tab.display_palette_colors(grayscale_colors)
                if hasattr(main_window, 'edit_palettes_tab'):
                    main_window.edit_palettes_tab.display_palette_colors(grayscale_colors)

        main_window.menu_bar.action_save_palette.setEnabled(True)
        main_window.sync_palettes_tab()

        if hasattr(main_window, 'output_loaded_for_zoom'):
            main_window.output_loaded_for_zoom = True
            
        return True
        
    except Exception as e:
        print(f"Error loading last output: {e}")
        return False

def _apply_palette_colors(main_window, colors):
    if not hasattr(main_window, 'edit_palettes_tab'):
        QMessageBox.warning(main_window, "Error", "Palette editor not available.")
        return

    palette_tab = main_window.edit_palettes_tab
    has_tilemap = bool(getattr(palette_tab, 'tilemap_data', None))
    need_bpp    = not has_tilemap

    apply_dlg = PaletteApplyDialog(main_window, need_bpp=need_bpp)
    if apply_dlg.exec() != QDialog.Accepted:
        return
    mode, dlg_bpp = apply_dlg.get_values()

    bpp = getattr(main_window, 'current_bpp', 4) if has_tilemap else dlg_bpp

    load_dlg = PaletteLoadDialog(main_window, len(colors))
    if load_dlg.exec() != QDialog.Accepted:
        return
    index, length = load_dlg.get_values()

    if length > len(colors):
        QMessageBox.warning(
            main_window, "Invalid Length",
            f"Source only contains {len(colors)} colors, but requested length is {length}."
        )
        return

    if mode == PaletteApplyDialog.ADD:
        new_palette = list(palette_tab.palette_colors)
        for i in range(length):
            if index + i < 256:
                new_palette[index + i] = colors[i]
    else:
        new_palette = [(0, 0, 0)] * 256
        for i in range(length):
            if index + i < 256:
                new_palette[index + i] = colors[i]

    tiles_path = "output/tiles.png"
    if os.path.exists(tiles_path):
        try:
            with PilImage.open(tiles_path) as _t:
                can_update = _t.mode == 'P'
        except Exception:
            can_update = False
    else:
        can_update = False

    if can_update:
        if mode == PaletteApplyDialog.SYNC:
            _sync_tileset_to_palette(tiles_path, palette_tab.palette_colors, new_palette, bpp)
        elif mode in (PaletteApplyDialog.REPLACE, PaletteApplyDialog.ADD):
            _replace_tileset_palette(tiles_path, new_palette)

    for i in range(256):
        palette_tab.palette_colors[i] = new_palette[i]
        if i < len(palette_tab.palette_rects):
            r, g, b = new_palette[i]
            palette_tab.palette_rects[i].setBrush(QBrush(QColor(r, g, b)))

    palette_tab._save_and_update_all()
    palette_tab.color_editor.toggle_controls_enabled(True)
    idx = palette_tab.current_editing_index
    if 0 <= idx < len(palette_tab.palette_colors):
        r, g, b = palette_tab.palette_colors[idx]
        palette_tab.color_editor.set_color(idx, r, g, b)
    main_window.menu_bar.action_save_palette.setEnabled(True)

    QMessageBox.information(
        main_window, "Palette Loaded",
        f"Successfully loaded {length} colors starting at index {index}."
    )

def _sync_tileset_to_palette(tiles_path, old_palette, new_palette, bpp):
    import numpy as np
    try:
        with PilImage.open(tiles_path) as f:
            arr = np.array(f).copy()

        old_rgb = np.array(
            [old_palette[i] if i < len(old_palette) else (0, 0, 0) for i in range(256)],
            dtype=np.int32
        )
        new_rgb = np.array(
            [new_palette[i] if i < len(new_palette) else (0, 0, 0) for i in range(256)],
            dtype=np.int32
        )

        slot_size = 16 if bpp == 4 else 256
        remap = np.arange(256, dtype=np.uint8)

        for old_idx in range(256):
            oc = old_rgb[old_idx]
            slot_start = (old_idx // slot_size) * slot_size
            slot_end   = slot_start + slot_size
            candidates = np.arange(slot_start, slot_end)
            dists = np.sum((new_rgb[candidates] - oc) ** 2, axis=1)
            min_dist = dists.min()
            ties = candidates[dists == min_dist]
            remap[old_idx] = old_idx if old_idx in ties else ties[0]

        lut = remap
        remapped = lut[arr]

        out_img = PilImage.fromarray(remapped, mode='P')
        flat = [c for rgb in new_palette for c in (int(rgb[0]), int(rgb[1]), int(rgb[2]))]
        while len(flat) < 768:
            flat.append(0)
        out_img.putpalette(flat)
        out_img.save(tiles_path)
    except Exception as e:
        print(f"Error syncing tileset: {e}")

def _replace_tileset_palette(tiles_path, new_palette):
    try:
        with PilImage.open(tiles_path) as f:
            import numpy as np
            arr = np.array(f).copy()
            size = f.size
        out_img = PilImage.fromarray(arr, mode='P')
        flat = [c for rgb in new_palette for c in (int(rgb[0]), int(rgb[1]), int(rgb[2]))]
        while len(flat) < 768:
            flat.append(0)
        out_img.putpalette(flat)
        out_img.save(tiles_path)
    except Exception as e:
        print(f"Error replacing tileset palette: {e}")

def open_image_for_conversion(main_window):
    from ui.dialogs.conversion_dialog import ConversionDialog
    
    input_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.translator.tr("open_image"),
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
    )
    if not input_path:
        return

    dialog = ConversionDialog(image_path=input_path, parent=main_window)
    dialog.exec()

def _reset_tilemap(main_window):
    et = main_window.edit_tiles_tab
    ep = main_window.edit_palettes_tab

    for tab in (et, ep):
        tab.tilemap_data   = None
        tab.tilemap_width  = 0
        tab.tilemap_height = 0
        tab.tilemap_width_spin.setValue(32)
        tab.tilemap_height_spin.setValue(32)
        tab.edit_tilemap_scene.clear() if hasattr(tab, 'edit_tilemap_scene') else None
        tab._set_tilemap_controls_enabled(False)

    if hasattr(ep, 'edit_tilemap2_scene'):
        ep.edit_tilemap2_scene.clear()
        ep.overlay_items.clear()

    main_window.menu_bar.action_save_tilemap.setEnabled(False)
    main_window.menu_bar.action_open_tilemap.setEnabled(True)
    main_window.menu_bar.action_new_tilemap.setEnabled(True)

def _reset_palette(main_window):
    from core.palette_utils import generate_grayscale_palette
    grayscale = generate_grayscale_palette()

    ep = main_window.edit_palettes_tab
    ep.palette_colors = list(grayscale)
    ep.display_palette_colors(grayscale, enable_editor=False)

    if hasattr(main_window, 'preview_tab'):
        main_window.preview_tab.display_palette_colors(grayscale)

    main_window.menu_bar.action_save_palette.setEnabled(False)

def open_tileset(main_window):
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.translator.tr("open_tileset"),
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
    )
    if not file_path:
        return

    try:
        with PilImage.open(file_path) as f:
            if f.mode != 'P':
                QMessageBox.warning(
                    main_window,
                    main_window.translator.tr("error"),
                    "The image must be indexed (palette-based). Please convert it to indexed mode first."
                )
                return
            pil_img = f.copy()
            raw_palette = f.getpalette()
    except Exception as e:
        QMessageBox.warning(main_window, main_window.translator.tr("error"),
                            main_window.translator.tr("could_not_load_tileset").format(error=str(e)))
        return

    os.makedirs('output', exist_ok=True)

    for fname in os.listdir('output'):
        if fname != 'tiles.png':
            fpath = os.path.join('output', fname)
            try:
                os.remove(fpath)
            except Exception:
                pass

    for fpath in ('temp/preview/preview.png', 'temp/preview/palette.pal'):
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

    pil_img.save('output/tiles.png')

    from core.image_utils import analyze_tiles_bpp
    detected_bpp = analyze_tiles_bpp('output/tiles.png')
    if detected_bpp is None:
        QMessageBox.warning(
            main_window, main_window.translator.tr("error"),
            "The image must be indexed (4bpp or 8bpp). Please convert it to indexed mode first."
        )
        return
    main_window.current_bpp = detected_bpp
    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'bpp', '1' if detected_bpp == 8 else '0')

    _reset_tilemap(main_window)

    palette_colors = [(0, 0, 0)] * 256
    for i in range(min(256, len(raw_palette) // 3)):
        palette_colors[i] = (raw_palette[i * 3], raw_palette[i * 3 + 1], raw_palette[i * 3 + 2])

    ep = main_window.edit_palettes_tab
    ep.palette_colors = list(palette_colors)
    ep.display_palette_colors(palette_colors, enable_editor=True)
    if hasattr(main_window, 'preview_tab'):
        main_window.preview_tab.display_palette_colors(palette_colors)
    main_window.menu_bar.action_save_palette.setEnabled(True)

    main_window.display_tileset(pil_img)
    main_window.menu_bar.action_save_tileset.setEnabled(True)
    main_window.tileset_from_conversion = False
    main_window.conversion_palette_count = 0

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

    main_window.main_tabs.setCurrentIndex(1)

def save_tileset(main_window):
    source_path = os.path.join("output", "tiles.png")

    if not os.path.exists(source_path):
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_tileset"),
            main_window.translator.tr("no_tileset_to_save")
        )
        return

    target_path, selected_filter = QFileDialog.getSaveFileName(
        main_window,
        main_window.translator.tr("save_tileset"),
        "tiles",
        "PNG Images (*.png);;BMP Images (*.bmp);;All Files (*)"
    )

    if not target_path:
        return

    try:
        if "bmp" in selected_filter.lower() or target_path.lower().endswith(".bmp"):
            img = PilImage.open(source_path)
            img.save(target_path, format="BMP")
        else:
            shutil.copy2(source_path, target_path)

        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_tileset"),
            main_window.translator.tr("tileset_exported", path=target_path)
        )
    except Exception as e:
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("save_tileset"),
            main_window.translator.tr("error_saving_tileset", error=str(e))
        )

def open_tilemap(main_window):
    from ui.dialogs.open_tilemap_dialog import OpenTilemapDialog

    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Open Tilemap",
        "",
        "Binary Files (*.bin);;All Files (*)"
    )
    if not file_path:
        return

    try:
        with open(file_path, 'rb') as f:
            tilemap_data = f.read()
    except Exception as e:
        QMessageBox.warning(main_window, "Error", f"Could not read file:\n{e}")
        return

    if len(tilemap_data) < 2 or len(tilemap_data) % 2 != 0:
        QMessageBox.warning(main_window, "Invalid Tilemap",
                            "File size is not valid (must be a multiple of 2 bytes).")
        return

    total_tiles = len(tilemap_data) // 2

    dlg = OpenTilemapDialog(total_tiles, main_window)
    if dlg.exec() != QDialog.Accepted:
        return

    w, h, bpp = dlg.get_values()

    # Validate max tile index against loaded tileset
    tiles_path = "output/tiles.png"
    if os.path.exists(tiles_path):
        try:
            with PilImage.open(tiles_path) as img:
                tileset_tile_count = (img.width // 8) * (img.height // 8)
        except Exception:
            tileset_tile_count = None

        if tileset_tile_count is not None:
            max_tile_idx = 0
            for i in range(total_tiles):
                entry = tilemap_data[i * 2] | (tilemap_data[i * 2 + 1] << 8)
                tile_id = entry & 0x3FF
                if tile_id > max_tile_idx:
                    max_tile_idx = tile_id

            if max_tile_idx >= tileset_tile_count:
                QMessageBox.warning(
                    main_window, "Tilemap Incompatible",
                    f"The tilemap references tile index {max_tile_idx}, but the current "
                    f"tileset only has {tileset_tile_count} tiles (0–{tileset_tile_count - 1})."
                )
                return

    os.makedirs('output', exist_ok=True)
    shutil.copy2(file_path, 'output/map.bin')

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(w))
        main_window.config_manager.set('CONVERSION', 'tilemap_height', str(h))
        main_window.config_manager.set('CONVERSION', 'bpp', '1' if bpp == 8 else '0')

    main_window.current_bpp = bpp

    et = main_window.edit_tiles_tab
    et.tilemap_data   = tilemap_data
    et.tilemap_width  = w
    et.tilemap_height = h
    et.tilemap_width_spin.setValue(w)
    et.tilemap_height_spin.setValue(h)
    et.enable_tilemap_controls()

    from core.image_utils import create_gbagfx_preview
    from core.image_utils import pil_to_qimage as _pil_to_qimage
    from PySide6.QtGui import QPixmap as _QPixmap

    save_preview     = main_window.config_manager.getboolean('SETTINGS', 'save_preview_files',     False) if hasattr(main_window, 'config_manager') else False
    keep_transparent = main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(main_window, 'config_manager') else False
    create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)

    preview_path = 'temp/preview/preview.png'
    if os.path.exists(preview_path):
        with PilImage.open(preview_path) as _f:
            preview_img = _f.copy()
        preview_pixmap = _QPixmap.fromImage(_pil_to_qimage(preview_img))

        main_window.preview_tab.preview_image_scene.clear()
        main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
        main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())

        et.edit_tilemap_scene.clear()
        et.edit_tilemap_scene.addPixmap(preview_pixmap)
        et.edit_tilemap_scene.setSceneRect(preview_pixmap.rect())

        main_window.edit_palettes_tab.display_tilemap_replica(et.edit_tilemap_scene)
        main_window.edit_palettes_tab.update_palette_overlay(
            et.edit_tilemap_scene, tilemap_data, w, h
        )

        from .view_ops import apply_zoom_to_view
        apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, main_window.zoom_level / 100.0)

    main_window.menu_bar.action_save_tilemap.setEnabled(True)
    main_window.sync_palettes_tab()

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

def new_tilemap(main_window):
    from ui.dialogs.new_tilemap_dialog import NewTilemapDialog
    from ui.dialogs.gba_compatibility_dialog import GBACompatibilityDialog
    from core.final_assets import reorganize_tilemap_for_gba_bg
    from core.image_utils import create_gbagfx_preview

    dlg = NewTilemapDialog(main_window)
    if dlg.exec() != QDialog.Accepted:
        return

    w, h, bpp = dlg.get_values()

    requires_gba_adjustment = False
    adjusted_w, adjusted_h = w, h
    if w > 32:
        if w != 64:
            requires_gba_adjustment = True
            adjusted_w = 64
        if h % 32 != 0:
            requires_gba_adjustment = True
            adjusted_h = ((h + 31) // 32) * 32

    if requires_gba_adjustment:
        compat_dlg = GBACompatibilityDialog(w, h, adjusted_w, adjusted_h, main_window)
        if not compat_dlg.exec():
            return
        w, h = adjusted_w, adjusted_h

    raw_data = b'\x00\x00' * (w * h)

    if w > 32:
        tile_list = [(0, 0, 0, 0)] * (w * h)
        reorganized = reorganize_tilemap_for_gba_bg(tile_list, w * 8, h * 8)
        final_data = bytearray()
        for tile_id, hf, vf, pal in reorganized:
            entry = tile_id & 0x3FF
            if hf: entry |= (1 << 10)
            if vf: entry |= (1 << 11)
            entry |= (pal << 12)
            final_data.extend(entry.to_bytes(2, 'little'))
        tilemap_data = bytes(final_data)
    else:
        tilemap_data = raw_data

    import os
    os.makedirs('output', exist_ok=True)
    with open(os.path.join('output', 'map.bin'), 'wb') as f:
        f.write(tilemap_data)

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(w))
        main_window.config_manager.set('CONVERSION', 'tilemap_height', str(h))
        main_window.config_manager.set('CONVERSION', 'bpp', str(bpp))

    tiles_path   = 'output/tiles.png' if os.path.exists('output/tiles.png') else None
    preview_path = 'temp/preview/preview.png' if os.path.exists('temp/preview/preview.png') else None
    main_window.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path)
    main_window.edit_tiles_tab.tilemap_width  = w
    main_window.edit_tiles_tab.tilemap_height = h
    main_window.edit_tiles_tab.tilemap_width_spin.setValue(w)
    main_window.edit_tiles_tab.tilemap_height_spin.setValue(h)
    main_window.menu_bar.action_save_tilemap.setEnabled(True)

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

    save_preview    = main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False) if hasattr(main_window, 'config_manager') else False
    keep_transparent = main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(main_window, 'config_manager') else False
    palette_colors = main_window.edit_palettes_tab.palette_colors if hasattr(main_window, 'edit_palettes_tab') else None
    result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
    if result:
        main_window.refresh_preview_display()

def save_tilemap(main_window):
    pass

def save_selection(main_window):
    pass

def open_palette(main_window):
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    palette_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Open Palette File",
        "",
        "Palette / Image Files (*.pal *.png *.bmp);;Palette Files (*.pal);;Indexed Images (*.png *.bmp);;All Files (*)"
    )

    if not palette_path:
        return

    colors = []
    ext = os.path.splitext(palette_path)[1].lower()

    if ext in ('.png', '.bmp'):
        try:
            with PilImage.open(palette_path) as img:
                if img.mode != 'P':
                    QMessageBox.warning(
                        main_window,
                        "Not an Indexed Image",
                        f"The selected image is not indexed (mode: {img.mode}).\n"
                        "Only indexed (palette-based) PNG/BMP images are supported."
                    )
                    return
                raw = img.getpalette()
            for i in range(0, min(len(raw), 768), 3):
                colors.append((raw[i], raw[i+1], raw[i+2]))
        except Exception as e:
            QMessageBox.warning(main_window, "Error Loading Image",
                                f"Failed to read image palette:\n{e}")
            return
    else:
        try:
            with open(palette_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f
                         if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
            if not lines:
                raise ValueError("Invalid palette file format")
            color_count = int(lines[0])
            for i in range(1, min(1 + color_count, len(lines))):
                r, g, b = map(int, lines[i].split())
                colors.append((r, g, b))
        except Exception as e:
            QMessageBox.warning(main_window, "Error Loading Palette",
                                f"Failed to read palette file:\n{e}")
            return

    if not colors:
        QMessageBox.warning(main_window, "Empty Palette", "No colors found in the selected file.")
        return

    _apply_palette_colors(main_window, colors)

def save_palette(main_window):
    output_dir = "output"

    if not os.path.exists(output_dir):
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_palette"),
            main_window.translator.tr("no_palette_files_to_save")
        )
        return

    palette_files = sorted(
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.startswith("palette_") and f.endswith(".pal")
    )
    
    if not palette_files:
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_palette"),
            main_window.translator.tr("no_palette_files_to_save")
        )
        return
    
    target_dir = QFileDialog.getExistingDirectory(
        main_window,
        main_window.translator.tr("select_palette_save_directory"),
        "",
        QFileDialog.ShowDirsOnly
    )
    
    if not target_dir:
        return
    
    try:
        for source_path in palette_files:
            file_name = os.path.basename(source_path)
            target_path = os.path.join(target_dir, file_name)
            shutil.copy2(source_path, target_path)
        
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_palette_complete"),
            main_window.translator.tr(
                "palette_files_saved", 
                count=len(palette_files), 
                path=target_dir
            )
        )
        
    except Exception as e:
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("save_palette_error"),
            main_window.translator.tr("error_saving_palette", error=str(e))
        )
