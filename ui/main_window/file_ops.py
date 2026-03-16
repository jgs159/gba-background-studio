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
        tiles_img = PilImage.open(tiles_path)
        main_window.display_tileset(tiles_img)
        
        with open(tilemap_path, 'rb') as f:
            tilemap_data = f.read()
        main_window.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path if os.path.exists(preview_path) else None)

        if hasattr(main_window, 'history_manager'):
            main_window.history_manager.clear()

        if os.path.exists(preview_path):
            preview_img = PilImage.open(preview_path)
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
        
        main_window.sync_palettes_tab()
        
        main_window.menu_bar.action_save_tileset.setEnabled(True)
        main_window.menu_bar.action_open_tilemap.setEnabled(True)
        main_window.menu_bar.action_new_tilemap.setEnabled(True)
        main_window.menu_bar.action_save_tilemap.setEnabled(True)
        main_window.menu_bar.action_save_selection.setEnabled(False)

        if hasattr(main_window, 'output_loaded_for_zoom'):
            main_window.output_loaded_for_zoom = True
            
        return True
        
    except Exception as e:
        print(f"Error loading last output: {e}")
        return False

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
        pil_img = PilImage.open(file_path)
        main_window.display_tileset(pil_img)
        
        if hasattr(main_window, 'history_manager'):
            main_window.history_manager.clear()
        
        main_window.main_tabs.setCurrentIndex(1)

    except Exception as e:
        main_window.current_status_message = main_window.translator.tr("error_loading_tileset").format(error=str(e))
        QMessageBox.warning(main_window, main_window.translator.tr("error"), main_window.translator.tr("could_not_load_tileset").format(error=str(e)))

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
    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

def new_tilemap(main_window):
    pass

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
        "Palette Files (*.pal);;All Files (*)"
    )
    
    if not palette_path:
        return
    
    colors = []
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
        QMessageBox.warning(
            main_window,
            "Error Loading Palette",
            f"Failed to read palette file:\n{e}"
        )
        return
    
    dialog = PaletteLoadDialog(main_window, len(colors))
    if dialog.exec() != QDialog.Accepted:
        return
    
    index, length = dialog.get_values()
    
    if length > len(colors):
        QMessageBox.warning(
            main_window,
            "Invalid Length",
            f"Palette file only contains {len(colors)} colors, "
            f"but requested length is {length}"
        )
        return
    
    if hasattr(main_window, 'edit_palettes_tab'):
        palette_tab = main_window.edit_palettes_tab
        
        for i in range(length):
            if index + i < 256:
                palette_tab.palette_colors[index + i] = colors[i]
                
                if index + i < len(palette_tab.palette_rects):
                    r, g, b = colors[i]
                    palette_tab.palette_rects[index + i].setBrush(
                        QBrush(QColor(r, g, b))
                    )
        
        palette_tab._save_and_update_all()
        
        QMessageBox.information(
            main_window,
            "Palette Loaded",
            f"Successfully loaded {length} colors starting at index {index}"
        )
    else:
        QMessageBox.warning(
            main_window,
            "Error",
            "Palette editor not available"
        )

def save_palette(main_window):
    output_dir = "output"
    
    palette_files = []
    if main_window.current_bpp == 4:
        for i in range(16):
            palette_path = os.path.join(output_dir, f"palette_{i:02d}.pal")
            if os.path.exists(palette_path):
                palette_files.append(palette_path)
    else:
        for file in os.listdir(output_dir):
            if file.startswith("palette_") and file.endswith(".pal"):
                palette_path = os.path.join(output_dir, file)
                if len(file) == 13:
                    palette_files.append(palette_path)
    
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
