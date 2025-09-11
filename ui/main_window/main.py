# ui/main_window/main.py
import os
from PIL import Image as PilImage
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtGui import QPixmap
from ..custom_status_bar import CustomStatusBar
from ..preview_tab import PreviewTab
from ..edit_tiles_tab import EditTilesTab
from ..edit_palettes_tab import EditPalettesTab
from ..menu_bar import MenuBar
from utils.translator import Translator
from core.config_manager import ConfigManager
from ..hover_manager import HoverManager
from ..grid_manager import GridManager

class GBABackgroundStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        
        from .config import load_configuration
        load_configuration(self)
        
        self.translator = Translator(lang_dir="lang", default_lang=self.config_manager.get('SETTINGS', 'language', 'english'))

        self.setWindowTitle("GBA Background Studio")
        self.resize(754, 644)

        self.tile_size = 8
        self.zoom_level = 100
        self.zoom_levels = [100, 200, 300, 400, 500, 600, 700, 800]
        self.current_zoom_index = 0
        self.selected_tile_id = 0
        self.selected_tile_image = None
        self.tileset_columns = 0
        self.tileset_rows = 0
        self.tileset_tiles = []
        self.tileset_ids = {}
        self.tilemap_ids = []
        self.tilemap_tiles = []
        self.tilemap_columns = 0
        self.tilemap_rows = 0
        self.current_tileset = None
        self.is_drawing = False
        self.current_status_message = self.translator.tr("ready_status")
        self.last_tile_pos = (-1, -1)

        self.hover_manager = HoverManager()
        self.grid_manager = GridManager()

        self.setup_ui()

        self.main_tabs.currentChanged.connect(self.on_tab_changed)

        from .config import setup_grids
        setup_grids(self)

        if self.load_last_output:
            from .file_ops import load_last_output_files
            load_last_output_files(self)

    def setup_ui(self):
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.main_tabs)

        self.preview_tab = PreviewTab(self)
        self.edit_tiles_tab = EditTilesTab(self)
        self.edit_palettes_tab = EditPalettesTab(self)
        
        self.main_tabs.addTab(self.preview_tab, self.translator.tr("preview_tab"))
        self.main_tabs.addTab(self.edit_tiles_tab, self.translator.tr("edit_tiles_tab"))
        self.main_tabs.addTab(self.edit_palettes_tab, self.translator.tr("edit_palettes_tab"))

        self.custom_status_bar = CustomStatusBar()
        self.custom_status_bar.show_message(self.current_status_message)
        main_layout.addWidget(self.custom_status_bar)

        self.menu_bar = MenuBar(self)
        
        from .config import apply_configuration_to_menu
        apply_configuration_to_menu(self)
        
        from .view_ops import setup_wheel_events
        setup_wheel_events(self)

        self.hover_manager.register_view(self.edit_tiles_tab.edit_tilemap_view)
        self.hover_manager.register_view(self.edit_palettes_tab.edit_tilemap2_view)

    def load_configuration(self):
        from .config import load_configuration
        load_configuration(self)
    
    def apply_configuration_to_menu(self):
        from .config import apply_configuration_to_menu
        apply_configuration_to_menu(self)
    
    def toggle_show_success_dialog(self, checked):
        from .config import toggle_show_success_dialog
        toggle_show_success_dialog(self, checked)
    
    def toggle_load_last_output(self, checked):
        from .config import toggle_load_last_output
        toggle_load_last_output(self, checked)
    
    def toggle_save_conversion_params(self, checked):
        from .config import toggle_save_conversion_params
        toggle_save_conversion_params(self, checked)
    
    def on_tab_changed(self, index):
        from .tab_ops import on_tab_changed
        on_tab_changed(self, index)
    
    def setup_wheel_events(self):
        from .view_ops import setup_wheel_events
        setup_wheel_events(self)
    
    def open_image_for_conversion(self):
        from .file_ops import open_image_for_conversion
        open_image_for_conversion(self)
    
    def open_tileset(self):
        from .file_ops import open_tileset
        open_tileset(self)
    
    def save_tileset(self):
        from .file_ops import save_tileset
        save_tileset(self)
    
    def append_tiles(self):
        from .file_ops import append_tiles
        append_tiles(self)
    
    def open_tilemap(self):
        from .file_ops import open_tilemap
        open_tilemap(self)
    
    def save_tilemap(self):
        from .file_ops import save_tilemap
        save_tilemap(self)
    
    def save_selection(self):
        from .file_ops import save_selection
        save_selection(self)
    
    def open_palette(self):
        from .file_ops import open_palette
        open_palette(self)
    
    def save_palette(self):
        from .file_ops import save_palette
        save_palette(self)
    
    def toggle_save_preview(self, checked):
        from .config import toggle_save_preview
        toggle_save_preview(self, checked)
    
    def toggle_keep_transparent(self, checked):
        from .config import toggle_keep_transparent
        toggle_keep_transparent(self, checked)
    
    def toggle_keep_temp(self, checked):
        from .config import toggle_keep_temp
        toggle_keep_temp(self, checked)
    
    def reset_zoom(self):
        from .view_ops import reset_zoom
        reset_zoom(self)
    
    def zoom_in(self):
        from .view_ops import zoom_in
        zoom_in(self)
    
    def zoom_out(self):
        from .view_ops import zoom_out
        zoom_out(self)
    
    def apply_zoom_to_all(self):
        from .view_ops import apply_zoom_to_all
        apply_zoom_to_all(self)
    
    def apply_zoom_to_view(self, view, zoom_factor):
        from .view_ops import apply_zoom_to_view
        apply_zoom_to_view(self, view, zoom_factor)
    
    def update_hover_from_current_cursor(self):
        from .tab_ops import update_hover_from_current_cursor
        update_hover_from_current_cursor(self)
    
    def apply_zoom_to_new_content(self, view):
        from .view_ops import apply_zoom_to_new_content
        apply_zoom_to_new_content(self, view)
    
    def toggle_grid(self, checked):
        from .config import toggle_grid
        toggle_grid(self, checked)
    
    def toggle_status_bar(self, checked):
        from .config import toggle_status_bar
        toggle_status_bar(self, checked)
    
    def change_language(self, language_code):
        from .utils import change_language
        change_language(self, language_code)
    
    def change_theme(self, theme_code):
        from .utils import change_theme
        change_theme(self, theme_code)
    
    def retranslate_ui(self):
        from .utils import retranslate_ui
        retranslate_ui(self)
    
    def recreate_menu(self):
        from .utils import recreate_menu
        recreate_menu(self)
    
    def show_contribute(self):
        from .dialogs import show_contribute
        show_contribute(self)
    
    def show_about(self):
        from .dialogs import show_about
        show_about(self)
    
    def display_tileset(self, pil_img):
        from .tab_ops import display_tileset
        display_tileset(self, pil_img)
    
    def sync_palettes_tab(self):
        from .tab_ops import sync_palettes_tab
        sync_palettes_tab(self)
    
    def load_conversion_results(self):
        from .tab_ops import load_conversion_results
        load_conversion_results(self)
    
    def load_last_output_files(self):
        from .file_ops import load_last_output_files
        load_last_output_files(self)
