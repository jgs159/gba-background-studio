# ui/main_window/file_ops.py
import os
from PIL import Image as PilImage
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap
from core.image_utils import pil_to_qimage
from core.palette_utils import generate_grayscale_palette

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
        
        if os.path.exists(preview_path):
            preview_img = PilImage.open(preview_path)
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            main_window.preview_tab.preview_image_scene.clear()
            main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
            
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
            except Exception as e:
                print(f"Error loading palette: {e}")
                grayscale_colors = generate_grayscale_palette()
                main_window.preview_tab.display_palette_colors(grayscale_colors)
        
        main_window.sync_palettes_tab()
        
        main_window.menu_bar.action_save_tileset.setEnabled(True)
        main_window.menu_bar.action_append_tiles.setEnabled(True)
        main_window.menu_bar.action_open_tilemap.setEnabled(True)
        main_window.menu_bar.action_save_tilemap.setEnabled(True)
        main_window.menu_bar.action_save_selection.setEnabled(True)

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
        
        main_window.main_tabs.setCurrentIndex(1)

    except Exception as e:
        main_window.current_status_message = main_window.translator.tr("error_loading_tileset").format(error=str(e))
        QMessageBox.warning(main_window, main_window.translator.tr("error"), main_window.translator.tr("could_not_load_tileset").format(error=str(e)))

def save_tileset(main_window):
    pass

def append_tiles(main_window):
    pass

def open_tilemap(main_window):
    pass

def save_tilemap(main_window):
    pass

def save_selection(main_window):
    pass

def open_palette(main_window):
    pass

def save_palette(main_window):
    pass
