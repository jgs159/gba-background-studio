# ui/main_window.py
import os
from PIL import Image as PilImage
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox, QFileDialog, QGraphicsView
from PySide6.QtGui import QPixmap, QPen, QColor, QImage, QCursor
from .custom_status_bar import CustomStatusBar
from .preview_tab import PreviewTab
from .edit_tiles_tab import EditTilesTab
from .edit_palettes_tab import EditPalettesTab
from .menu_bar import MenuBar
from utils.translator import Translator
from ui.dialogs.conversion_dialog import ConversionDialog
from core.image_utils import pil_to_qimage
from core.palette_utils import generate_grayscale_palette
from core.config_manager import ConfigManager
from ui.hover_manager import HoverManager
from ui.grid_manager import GridManager


class GBABackgroundStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        
        self.load_configuration()
        
        self.translator = Translator(lang_dir="lang", default_lang=self.config_manager.get('SETTINGS', 'language', 'english'))

        self.setWindowTitle("GBA Background Studio")
        self.resize(754, 644)

        # === TILES CONFIGURATION ===
        self.tile_size = 8

        # === ZOOM CONFIGURATION ===
        self.zoom_level = 100  # 100% por defecto
        self.zoom_levels = [100, 200, 300, 400, 500, 600, 700, 800]
        self.current_zoom_index = 0
        
        # === TILE SELECTION SYSTEM ===
        self.selected_tile_id = 0
        self.selected_tile_image = None
        self.tileset_columns = 0
        self.tileset_rows = 0
        self.tileset_tiles = []
        self.tileset_ids = {}
        
        # === TILEMAP SYSTEM ===  
        self.tilemap_ids = []
        self.tilemap_tiles = []
        self.tilemap_columns = 0
        self.tilemap_rows = 0
        
        # === TEMPORARY VARIABLES ===
        self.current_tileset = None
        self.is_drawing = False
        self.current_status_message = self.translator.tr("ready_status")
        self.last_tile_pos = (-1, -1)

        # Main container widget
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main tab widget for the three main sections
        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.main_tabs)

        # === HOVER MANAGER ===
        self.hover_manager = HoverManager()

        # === GRID MANAGER ===
        self.grid_manager = GridManager()

        # Create tabs
        self.preview_tab = PreviewTab(self)
        self.edit_tiles_tab = EditTilesTab(self)
        self.edit_palettes_tab = EditPalettesTab(self)
        
        self.main_tabs.addTab(self.preview_tab, self.translator.tr("preview_tab"))
        self.main_tabs.addTab(self.edit_tiles_tab, self.translator.tr("edit_tiles_tab"))
        self.main_tabs.addTab(self.edit_palettes_tab, self.translator.tr("edit_palettes_tab"))

        # Custom status bar at the bottom
        self.custom_status_bar = CustomStatusBar()
        self.custom_status_bar.show_message(self.current_status_message)
        main_layout.addWidget(self.custom_status_bar)

        # Menu bar
        self.menu_bar = MenuBar(self)
        
        self.apply_configuration_to_menu()
        self.setup_wheel_events()

        self.hover_manager.register_view(self.edit_tiles_tab.edit_tilemap_view)
        self.hover_manager.register_view(self.edit_palettes_tab.edit_tilemap2_view)

        self.main_tabs.currentChanged.connect(self.on_tab_changed)

        self.setup_grids()

        if self.load_last_output:
            self.load_last_output_files()

    def load_configuration(self):
        self.save_preview_files = self.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
        self.keep_transparent_color = self.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)
        self.keep_temp_files = self.config_manager.getboolean('SETTINGS', 'keep_temp_files', False)
        self.load_last_output = self.config_manager.getboolean('SETTINGS', 'load_last_output', True)
        self.save_conversion_params = self.config_manager.getboolean('SETTINGS', 'save_conversion_params', True)

    def load_last_output_files(self):
        tiles_path = "output/tiles.png"
        preview_path = "temp/preview/preview.png"
        palette_path = "temp/preview/palette.pal"
        tilemap_path = "output/map.bin"
        
        if not (os.path.exists(tiles_path) and os.path.exists(tilemap_path)):
            return False
        
        try:
            tiles_img = PilImage.open(tiles_path)
            self.display_tileset(tiles_img)
            
            with open(tilemap_path, 'rb') as f:
                tilemap_data = f.read()
            self.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path if os.path.exists(preview_path) else None)
            
            if os.path.exists(preview_path):
                preview_img = PilImage.open(preview_path)
                preview_qimg = pil_to_qimage(preview_img)
                preview_pixmap = QPixmap.fromImage(preview_qimg)
                
                self.preview_tab.preview_image_scene.clear()
                self.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
                self.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
                
                self.apply_zoom_to_view(self.preview_tab.preview_image_view, self.zoom_level / 100.0)
                if self.preview_tab.preview_image_scene.items():
                    self.preview_tab.preview_image_view.centerOn(self.preview_tab.preview_image_scene.items()[0])
            
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
                            
                    self.preview_tab.display_palette_colors(palette_colors)
                except Exception as e:
                    print(f"Error loading palette: {e}")
                    grayscale_colors = generate_grayscale_palette()
                    self.preview_tab.display_palette_colors(grayscale_colors)
            
            self.sync_palettes_tab()
            
            self.menu_bar.action_save_tileset.setEnabled(True)
            self.menu_bar.action_append_tiles.setEnabled(True)
            self.menu_bar.action_open_tilemap.setEnabled(True)
            self.menu_bar.action_save_tilemap.setEnabled(True)
            self.menu_bar.action_save_selection.setEnabled(True)
            
            self.current_status_message = self.translator.tr("last_output_loaded")
            self.custom_status_bar.show_message(self.current_status_message)
            
            return True
            
        except Exception as e:
            print(f"Error loading last output: {e}")
            return False

    def toggle_load_last_output(self, checked):
        self.load_last_output = checked
        self.config_manager.set('SETTINGS', 'load_last_output', checked)
        status = 'Enabled' if checked else 'Disabled'
        self.current_status_message = self.translator.tr("load_last_output_status").format(status=status)
        self.custom_status_bar.show_message(self.current_status_message)

    def toggle_save_conversion_params(self, checked):
        self.save_conversion_params = checked
        self.config_manager.set('SETTINGS', 'save_conversion_params', checked)
        status = 'Enabled' if checked else 'Disabled'
        self.current_status_message = self.translator.tr("save_conversion_params_status").format(status=status)
        self.custom_status_bar.show_message(self.current_status_message)

    def on_tab_changed(self, index):
        current_tab = self.main_tabs.widget(index)
        
        if hasattr(self, 'edit_tiles_tab') and hasattr(self.edit_tiles_tab, 'edit_tilemap_view'):
            self.hover_manager.hide_hover(self.edit_tiles_tab.edit_tilemap_view)
        if hasattr(self, 'edit_palettes_tab') and hasattr(self.edit_palettes_tab, 'edit_tilemap2_view'):
            self.hover_manager.hide_hover(self.edit_palettes_tab.edit_tilemap2_view)
        
        if current_tab == self.edit_tiles_tab:
            self.update_hover_from_current_cursor()
        elif current_tab == self.edit_palettes_tab:
            self.update_hover_from_current_cursor()

    def setup_wheel_events(self):
        self.preview_tab.preview_image_view.wheelEvent = lambda event: self.zoom_wheel_event(self.preview_tab.preview_image_view, event)
        self.edit_tiles_tab.edit_tileset_view.wheelEvent = lambda event: self.zoom_wheel_event(self.edit_tiles_tab.edit_tileset_view, event)
        self.edit_tiles_tab.edit_tilemap_view.wheelEvent = lambda event: self.zoom_wheel_event(self.edit_tiles_tab.edit_tilemap_view, event)
        self.edit_palettes_tab.edit_palettes_view.wheelEvent = lambda event: self.zoom_wheel_event(self.edit_palettes_tab.edit_palettes_view, event)
        self.edit_palettes_tab.edit_tilemap2_view.wheelEvent = lambda event: self.zoom_wheel_event(self.edit_palettes_tab.edit_tilemap2_view, event)

    def zoom_wheel_event(self, view, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            
            self.update_hover_from_current_cursor()
        else:
            QGraphicsView.wheelEvent(view, event)

    def load_configuration(self):
        self.save_preview_files = self.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
        self.keep_transparent_color = self.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)
        self.keep_temp_files = self.config_manager.getboolean('SETTINGS', 'keep_temp_files', False)
        self.load_last_output = self.config_manager.getboolean('SETTINGS', 'load_last_output', False)
        self.save_conversion_params = self.config_manager.getboolean('SETTINGS', 'save_conversion_params', False)
    
    def apply_configuration_to_menu(self):
        if hasattr(self, 'menu_bar'):
            self.menu_bar.action_save_preview.setChecked(self.save_preview_files)
            self.menu_bar.action_keep_transparent.setChecked(self.keep_transparent_color)
            self.menu_bar.action_keep_temp.setChecked(self.keep_temp_files)
            self.menu_bar.action_load_last_output.setChecked(self.load_last_output)
            self.menu_bar.action_save_conversion_params.setChecked(self.save_conversion_params)
            
            theme = self.config_manager.get('SETTINGS', 'theme', 'light')
            for theme_code, action in self.menu_bar.theme_actions.items():
                action.setChecked(theme_code == theme)
            
            language = self.config_manager.get('SETTINGS', 'language', 'english')
            for lang_code, action in self.menu_bar.language_actions.items():
                action.setChecked(lang_code == language)

    def show_color_rgb(self, r, g, b):
        self.current_status_message = self.translator.tr("rgb_values").format(r=r, g=g, b=b)
        self.custom_status_bar.show_message(self.current_status_message)

    def open_image_for_conversion(self):
        input_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.tr("open_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
        )
        if not input_path:
            return

        dialog = ConversionDialog(image_path=input_path, parent=self)
        dialog.exec()

    def open_tileset(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.tr("open_tileset"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
        )
        if not file_path:
            return
        
        try:
            pil_img = PilImage.open(file_path)
            self.display_tileset(pil_img)
            
            self.main_tabs.setCurrentIndex(1)

        except Exception as e:
            self.current_status_message = self.translator.tr("error_loading_tileset").format(error=str(e))
            self.custom_status_bar.show_message(self.current_status_message)
            QMessageBox.warning(self, self.translator.tr("error"), self.translator.tr("could_not_load_tileset").format(error=str(e)))

    def save_tileset(self):
        pass

    def append_tiles(self):
        pass

    def open_tilemap(self):
        pass

    def save_tilemap(self):
        pass

    def save_selection(self):
        pass

    def setup_grids(self):
        self.grid_manager.register_view(self.edit_tiles_tab.edit_tileset_view, "tileset")
        self.grid_manager.register_view(self.edit_tiles_tab.edit_tilemap_view, "tilemap_edit")
        self.grid_manager.register_view(self.edit_palettes_tab.edit_palettes_view, "palettes")
        self.grid_manager.register_view(self.edit_palettes_tab.edit_tilemap2_view, "tilemap_palettes")
        
        grid_visible = self.config_manager.getboolean('SETTINGS', 'show_grid', False)
        self.grid_manager.set_grid_visible(grid_visible)
        
        if hasattr(self, 'menu_bar') and hasattr(self.menu_bar, 'action_grid'):
            self.menu_bar.action_grid.setChecked(grid_visible)

    def open_palette(self):
        self.current_status_message = self.translator.tr("open_palette_not_implemented")
        self.custom_status_bar.show_message(self.current_status_message)

    def save_palette(self):
        self.current_status_message = self.translator.tr("save_palette_not_implemented")
        self.custom_status_bar.show_message(self.current_status_message)

    def toggle_save_preview(self, checked):
        self.save_preview_files = checked
        self.config_manager.set('SETTINGS', 'save_preview_files', checked)
        self.current_status_message = self.translator.tr("save_preview_status").format(status='Enabled' if checked else 'Disabled')
        self.custom_status_bar.show_message(self.current_status_message)

    def toggle_keep_transparent(self, checked):
        self.keep_transparent_color = checked
        self.config_manager.set('SETTINGS', 'keep_transparent_color', checked)
        self.current_status_message = self.translator.tr("keep_transparent_status").format(status='Enabled' if checked else 'Disabled')
        self.custom_status_bar.show_message(self.current_status_message)

    def toggle_keep_temp(self, checked):
        self.keep_temp_files = checked
        self.config_manager.set('SETTINGS', 'keep_temp_files', checked)
        self.current_status_message = self.translator.tr("keep_temp_status").format(status='Enabled' if checked else 'Disabled')
        self.custom_status_bar.show_message(self.current_status_message)

    def reset_zoom(self):
        self.current_zoom_index = 0
        self.zoom_level = self.zoom_levels[self.current_zoom_index]
        self.apply_zoom_to_all()
        self.update_hover_from_current_cursor()

    def zoom_in(self):
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            self.zoom_level = self.zoom_levels[self.current_zoom_index]
            self.apply_zoom_to_all()
            self.update_hover_from_current_cursor()
            self.current_status_message = self.translator.tr("zoom_level", level=f"{self.zoom_level}%")
            self.custom_status_bar.show_message(self.current_status_message)

    def zoom_out(self):
        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.zoom_level = self.zoom_levels[self.current_zoom_index]
            self.apply_zoom_to_all()
            self.update_hover_from_current_cursor()
            self.current_status_message = self.translator.tr("zoom_level", level=f"{self.zoom_level}%")
            self.custom_status_bar.show_message(self.current_status_message)

    def apply_zoom_to_all(self):
        zoom_factor = self.zoom_level / 100.0

        self.apply_zoom_to_view(self.preview_tab.preview_image_view, zoom_factor)
        self.apply_zoom_to_view(self.edit_tiles_tab.edit_tileset_view, zoom_factor)
        self.apply_zoom_to_view(self.edit_tiles_tab.edit_tilemap_view, zoom_factor)
        
        self.edit_palettes_tab.apply_zoom(zoom_factor)
        self.apply_zoom_to_view(self.edit_palettes_tab.edit_tilemap2_view, zoom_factor)

        self.update_hover_from_current_cursor()

    def apply_zoom_to_view(self, view, zoom_factor):
        if view and view.scene() and view.scene().items():
            view.resetTransform()
            view.scale(zoom_factor, zoom_factor)
            if view.scene().items():
                view.centerOn(view.scene().items()[0])
            
            if (self.grid_manager.is_grid_visible() and 
                self._is_editor_view(view)):
                view_name = self._get_view_name(view)
                if view_name:
                    self.grid_manager.update_grid_for_view(view_name)
            
            if view == self.edit_tiles_tab.edit_tileset_view:
                if hasattr(self.edit_tiles_tab, 'selected_tile_pos') and self.edit_tiles_tab.selected_tile_pos != (-1, -1):
                    tile_x, tile_y = self.edit_tiles_tab.selected_tile_pos
                    self.edit_tiles_tab.highlight_selected_tile(tile_x, tile_y)

    def _is_editor_view(self, view):
        editor_views = [
            self.edit_tiles_tab.edit_tileset_view,
            self.edit_tiles_tab.edit_tilemap_view,
            self.edit_palettes_tab.edit_palettes_view,
            self.edit_palettes_tab.edit_tilemap2_view
        ]
        return view in editor_views

    def _get_view_name(self, view):
        if view == self.edit_tiles_tab.edit_tileset_view:
            return "tileset"
        elif view == self.edit_tiles_tab.edit_tilemap_view:
            return "tilemap_edit"
        elif view == self.edit_palettes_tab.edit_palettes_view:
            return "palettes"
        elif view == self.edit_palettes_tab.edit_tilemap2_view:
            return "tilemap_palettes"
        return None

    def update_hover_from_current_cursor(self):
        current_tab = self.main_tabs.currentWidget()
        
        if current_tab == self.edit_tiles_tab:
            self.hover_manager.update_hover_from_cursor(self.edit_tiles_tab.edit_tilemap_view)
        elif current_tab == self.edit_palettes_tab:
            self.hover_manager.update_hover_from_cursor(self.edit_palettes_tab.edit_tilemap2_view)

    def apply_zoom_to_new_content(self, view):
        if view:
            self.apply_zoom_to_view(view, self.zoom_level / 100.0)

    def toggle_grid(self, checked):
        self.grid_manager.set_grid_visible(checked)
        self.config_manager.set('SETTINGS', 'show_grid', checked)
        
        status = "Enabled" if checked else "Disabled"
        self.current_status_message = self.translator.tr("grid_status").format(status=status)
        self.custom_status_bar.show_message(self.current_status_message)

    def toggle_status_bar(self, checked):
        self.custom_status_bar.setVisible(checked)

    def change_language(self, language_code):
        self.config_manager.set('SETTINGS', 'language', language_code)
        self.translator.load_language(language_code)
        for lang_code, action in self.menu_bar.language_actions.items():
            action.setChecked(lang_code == language_code)
        
        self.retranslate_ui()
        self.current_status_message = self.translator.tr("language_changed", lang=language_code)
        self.custom_status_bar.show_message(self.current_status_message)

    def change_theme(self, theme_code):
        for theme_c, action in self.menu_bar.theme_actions.items():
            action.setChecked(theme_c == theme_code)
        
        self.config_manager.set('SETTINGS', 'theme', theme_code)
        
        from utils.theme_manager import apply_theme
        apply_theme(theme_code)
        
        self.current_status_message = self.translator.tr("theme_changed").format(theme=theme_code)
        self.custom_status_bar.show_message(self.current_status_message)

    def retranslate_ui(self):
        self.main_tabs.setTabText(0, self.translator.tr("preview_tab"))
        self.main_tabs.setTabText(1, self.translator.tr("edit_tiles_tab"))
        self.main_tabs.setTabText(2, self.translator.tr("edit_palettes_tab"))
        
        self.current_status_message = self.translator.tr("ready_status")
        self.custom_status_bar.show_message(self.current_status_message)
        
        self.recreate_menu()

    def recreate_menu(self):
        self.menu_bar.menu_bar.clear()
        self.menu_bar.create_menus()
        self.apply_configuration_to_menu()

    def show_contribute(self):
        contribute_text = """
        <h3>❤️ Support GBA Background Studio Development</h3>
        
        <p>If you're enjoying this application and find it useful for your 
        Game Boy Advance development projects, please consider supporting 
        my work!</p>
        
        <p>Your support helps me continue developing and improving this tool, 
        adding new features, and providing regular updates.</p>
        
        <p><b>You can support me with a donation at:</b></p>
        <p style="text-align: center; font-size: 14px;">
            <a href="https://ko-fi.com/compumax">https://ko-fi.com/compumax</a>
        </p>
        
        <p>Every contribution, no matter how small, makes a big difference 
        and is greatly appreciated! Thank you for using GBA Background Studio. 🎮</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.translator.tr("support_development"))
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(contribute_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def display_tileset(self, pil_img):
        self.edit_tiles_tab.display_tileset(pil_img)
        self.apply_zoom_to_view(self.edit_tiles_tab.edit_tileset_view, self.zoom_level / 100.0)

    def sync_palettes_tab(self):
        grid_was_visible = self.grid_manager.is_grid_visible()
        if grid_was_visible:
            self.grid_manager.set_grid_visible(False)
        
        try:
            if hasattr(self, 'preview_tab') and hasattr(self.preview_tab, 'palette_colors'):
                self.edit_palettes_tab.display_palette_colors(self.preview_tab.palette_colors)

            if hasattr(self, 'edit_tiles_tab') and hasattr(self.edit_tiles_tab, 'edit_tilemap_scene'):
                self.edit_palettes_tab.display_tilemap_replica(self.edit_tiles_tab.edit_tilemap_scene)
                self.edit_palettes_tab.update_palette_overlay(
                    self.edit_tiles_tab.edit_tilemap_scene,
                    self.edit_tiles_tab.tilemap_data,
                    self.edit_tiles_tab.tilemap_width,
                    self.edit_tiles_tab.tilemap_height
                )
                
                self.edit_palettes_tab.tilemap_data = self.edit_tiles_tab.tilemap_data
                self.edit_palettes_tab.tilemap_width = self.edit_tiles_tab.tilemap_width
                self.edit_palettes_tab.tilemap_height = self.edit_tiles_tab.tilemap_height
            
            if grid_was_visible:
                self.grid_manager.set_grid_visible(True)
                
        except Exception as e:
            print(f"Error syncing palettes tab: {e}")
            if grid_was_visible:
                self.grid_manager.set_grid_visible(True)

    def show_about(self):
        about_text = """
        <h3>GBA Background Studio</h3>
        <p>A comprehensive tool for creating and editing Game Boy Advance background graphics.</p>

        <p><b>📥 Downloads:</b>
        <a href="https://github.com/CompuMaxx">GitHub Repository</a></p>

        <p><b>💬 Contact:</b>
        Discord: <a href="https://discordapp.com/users/213803341988364289">CompuMax</a></p>

        <p><b>👨‍💻 Developer:</b>
        CompuMax</p>

        <p><b>© Copyright 2025</b>
        All rights reserved</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.translator.tr("about_title"))
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        
    def load_conversion_results(self):
        tiles_path = "output/tiles.png"
        preview_path = "temp/preview/preview.png"
        palette_path = "temp/preview/palette.pal"
        tilemap_path = "output/map.bin"

        if os.path.exists(tiles_path):
            tiles_img = PilImage.open(tiles_path)
            self.display_tileset(tiles_img)

        if os.path.exists(tilemap_path):
            with open(tilemap_path, 'rb') as f:
                tilemap_data = f.read()
            self.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path)
            
            self.edit_palettes_tab.tilemap_data = tilemap_data
            self.edit_palettes_tab.tilemap_width = self.edit_tiles_tab.tilemap_width
            self.edit_palettes_tab.tilemap_height = self.edit_tiles_tab.tilemap_height

        if os.path.exists(preview_path):
            preview_img = PilImage.open(preview_path)
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            self.preview_tab.preview_image_scene.clear()
            self.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            self.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
            
            self.apply_zoom_to_view(self.preview_tab.preview_image_view, self.zoom_level / 100.0)
            self.preview_tab.preview_image_view.centerOn(self.preview_tab.preview_image_scene.items()[0])

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
                        
                self.preview_tab.display_palette_colors(palette_colors)

            except Exception as e:
                print(f"Error loading palette: {e}")
                grayscale_colors = generate_grayscale_palette()
                self.preview_tab.display_palette_colors(grayscale_colors)

        self.current_status_message = self.translator.tr("conversion_completed")
        self.custom_status_bar.show_message(self.current_status_message)
        
        self.menu_bar.action_save_tileset.setEnabled(True)
        self.menu_bar.action_append_tiles.setEnabled(True)
        self.menu_bar.action_open_tilemap.setEnabled(True)
        self.menu_bar.action_save_tilemap.setEnabled(True)
        self.menu_bar.action_save_selection.setEnabled(True)
        
        self.main_tabs.setCurrentIndex(1)
        self.sync_palettes_tab()


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(False)
        self._is_drawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_drawing = True
            self.mouseMoveEvent(event)
            event.accept()
        elif event.button() == Qt.RightButton:
            self.mouseMoveEvent(event)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_drawing and (event.buttons() & Qt.LeftButton):
            pos = self.mapToScene(event.pos())
            if self.scene():
                tile_x = max(0, min(int(pos.x()) // 8, self.scene().width() // 8 - 1))
                tile_y = max(0, min(int(pos.y()) // 8, self.scene().height() // 8 - 1))
                if hasattr(self, 'on_tile_drawing'):
                    self.on_tile_drawing(tile_x, tile_y)
                event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_drawing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def load_last_output_files(self):
        grid_was_visible = self.grid_manager.is_grid_visible()
        if grid_was_visible:
            self.grid_manager.set_grid_visible(False)
        
        tiles_path = "output/tiles.png"
        preview_path = "temp/preview/preview.png"
        palette_path = "temp/preview/palette.pal"
        tilemap_path = "output/map.bin"
        
        if not (os.path.exists(tiles_path) and os.path.exists(tilemap_path)):
            if grid_was_visible:
                self.grid_manager.set_grid_visible(True)
            return False
        
        try:
            tiles_img = PilImage.open(tiles_path)
            self.display_tileset(tiles_img)
            
            with open(tilemap_path, 'rb') as f:
                tilemap_data = f.read()
            self.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path if os.path.exists(preview_path) else None)
            
            if os.path.exists(preview_path):
                preview_img = PilImage.open(preview_path)
                preview_qimg = pil_to_qimage(preview_img)
                preview_pixmap = QPixmap.fromImage(preview_qimg)
                
                self.preview_tab.preview_image_scene.clear()
                self.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
                self.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
                
                self.apply_zoom_to_view(self.preview_tab.preview_image_view, self.zoom_level / 100.0)
                if self.preview_tab.preview_image_scene.items():
                    self.preview_tab.preview_image_view.centerOn(self.preview_tab.preview_image_scene.items()[0])
            
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
                            
                    self.preview_tab.display_palette_colors(palette_colors)
                except Exception as e:
                    print(f"Error loading palette: {e}")
                    grayscale_colors = generate_grayscale_palette()
                    self.preview_tab.display_palette_colors(grayscale_colors)
            
            self.sync_palettes_tab()
            
            self.menu_bar.action_save_tileset.setEnabled(True)
            self.menu_bar.action_append_tiles.setEnabled(True)
            self.menu_bar.action_open_tilemap.setEnabled(True)
            self.menu_bar.action_save_tilemap.setEnabled(True)
            self.menu_bar.action_save_selection.setEnabled(True)
            
            if grid_was_visible:
                self.grid_manager.set_grid_visible(True)
            
            self.current_status_message = self.translator.tr("last_output_loaded")
            self.custom_status_bar.show_message(self.current_status_message)
            
            return True
            
        except Exception as e:
            print(f"Error loading last output: {e}")
            if grid_was_visible:
                self.grid_manager.set_grid_visible(True)
            return False

    def get_config_manager(self):
        return self.config_manager
