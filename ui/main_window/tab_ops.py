# ui/main_window/tab_ops.py
import os
from PIL import Image as PilImage
from core.image_utils import pil_to_qimage
from core.palette_utils import generate_grayscale_palette
from PySide6.QtGui import QPixmap


def on_tab_changed(main_window, index):
    current_tab = main_window.main_tabs.widget(index)
    
    if hasattr(main_window, 'edit_tiles_tab') and hasattr(main_window.edit_tiles_tab, 'edit_tilemap_view'):
        main_window.hover_manager.hide_hover(main_window.edit_tiles_tab.edit_tilemap_view)
    if hasattr(main_window, 'edit_palettes_tab') and hasattr(main_window.edit_palettes_tab, 'edit_tilemap2_view'):
        main_window.hover_manager.hide_hover(main_window.edit_palettes_tab.edit_tilemap2_view)
    
    if current_tab == main_window.edit_tiles_tab:
        update_hover_from_current_cursor(main_window)
    elif current_tab == main_window.edit_palettes_tab:
        update_hover_from_current_cursor(main_window)
    if current_tab == main_window.edit_tiles_tab:
        main_window.edit_tiles_tab.update_status_bar(0, 0)
    elif current_tab == main_window.edit_palettes_tab:
        main_window.edit_palettes_tab.update_status_bar(0, 0)
    elif current_tab == main_window.preview_tab:
        main_window.custom_status_bar.update_status(
            selection_type="Tile",
            selection_id=0,
            tilemap_pos=(0, 0),
            tile_id=0,
            palette_id=0,
            flip_state="None",
            zoom_level=main_window.zoom_level
        )

def update_hover_from_current_cursor(main_window):
    current_tab = main_window.main_tabs.currentWidget()
    
    if current_tab == main_window.edit_tiles_tab:
        main_window.hover_manager.update_hover_from_cursor(main_window.edit_tiles_tab.edit_tilemap_view)
    elif current_tab == main_window.edit_palettes_tab:
        main_window.hover_manager.update_hover_from_cursor(main_window.edit_palettes_tab.edit_tilemap2_view)

def display_tileset(main_window, pil_img):
    main_window.edit_tiles_tab.display_tileset(pil_img)
    from .view_ops import apply_zoom_to_view
    apply_zoom_to_view(main_window, main_window.edit_tiles_tab.edit_tileset_view, main_window.zoom_level / 100.0)

def sync_palettes_tab(main_window):
    grid_was_visible = main_window.grid_manager.is_grid_visible()
    if grid_was_visible:
        main_window.grid_manager.set_grid_visible(False)
    
    try:
        if hasattr(main_window, 'preview_tab') and hasattr(main_window.preview_tab, 'palette_colors'):
            main_window.edit_palettes_tab.display_palette_colors(main_window.preview_tab.palette_colors)

        if hasattr(main_window, 'edit_tiles_tab') and hasattr(main_window.edit_tiles_tab, 'edit_tilemap_scene'):
            main_window.edit_palettes_tab.display_tilemap_replica(main_window.edit_tiles_tab.edit_tilemap_scene)
            main_window.edit_palettes_tab.update_palette_overlay(
                main_window.edit_tiles_tab.edit_tilemap_scene,
                main_window.edit_tiles_tab.tilemap_data,
                main_window.edit_tiles_tab.tilemap_width,
                main_window.edit_tiles_tab.tilemap_height
            )
            
            main_window.edit_palettes_tab.tilemap_data = main_window.edit_tiles_tab.tilemap_data
            main_window.edit_palettes_tab.tilemap_width = main_window.edit_tiles_tab.tilemap_width
            main_window.edit_palettes_tab.tilemap_height = main_window.edit_tiles_tab.tilemap_height
        
        if grid_was_visible:
            main_window.grid_manager.set_grid_visible(True)
            
    except Exception as e:
        print(f"Error syncing palettes tab: {e}")
        if grid_was_visible:
            main_window.grid_manager.set_grid_visible(True)

def load_conversion_results(main_window):    
    tiles_path = "output/tiles.png"
    preview_path = "temp/preview/preview.png"
    palette_path = "temp/preview/palette.pal"
    tilemap_path = "output/map.bin"

    if os.path.exists(tiles_path):
        tiles_img = PilImage.open(tiles_path)
        display_tileset(main_window, tiles_img)

    if os.path.exists(tilemap_path):
        with open(tilemap_path, 'rb') as f:
            tilemap_data = f.read()
        main_window.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path)
        
        main_window.edit_palettes_tab.tilemap_data = tilemap_data
        main_window.edit_palettes_tab.tilemap_width = main_window.edit_tiles_tab.tilemap_width
        main_window.edit_palettes_tab.tilemap_height = main_window.edit_tiles_tab.tilemap_height

    if os.path.exists(preview_path):
        preview_img = PilImage.open(preview_path)
        preview_qimg = pil_to_qimage(preview_img)
        preview_pixmap = QPixmap.fromImage(preview_qimg)
        
        main_window.preview_tab.preview_image_scene.clear()
        main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
        main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
        
        from .view_ops import apply_zoom_to_view
        apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, main_window.zoom_level / 100.0)
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
  
    main_window.menu_bar.action_save_tileset.setEnabled(True)
    main_window.menu_bar.action_append_tiles.setEnabled(True)
    main_window.menu_bar.action_open_tilemap.setEnabled(True)
    main_window.menu_bar.action_save_tilemap.setEnabled(True)
    main_window.menu_bar.action_save_selection.setEnabled(True)
    
    main_window.main_tabs.setCurrentIndex(1)
    sync_palettes_tab(main_window)
