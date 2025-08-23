# ui/main_window.py
import os
from PIL import Image as PilImage
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap
from .custom_status_bar import CustomStatusBar
from .preview_tab import PreviewTab
from .edit_tiles_tab import EditTilesTab
from .edit_palettes_tab import EditPalettesTab
from .menu_bar import MenuBar
from utils.translator import Translator
from ui.conversion_dialog import ConversionDialog
from core.image_utils import pil_to_qimage
from core.palette_utils import generate_grayscale_palette


class GBABackgroundStudio(QMainWindow):
    def __init__(self, language="english"):
        super().__init__()
        self.translator = Translator(lang_dir="lang", default_lang=language)
        self.setWindowTitle(self.translator.tr("app_name"))
        self.resize(754, 644)

        # === TILES CONFIGURATION ===
        self.tile_size = 8
        
        # === TILE SELECTION SYSTEM ===
        self.selected_tile_id = None
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
        self.current_status_message = "Ready"

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

        # Create tabs
        self.preview_tab = PreviewTab(self)
        self.edit_tiles_tab = EditTilesTab(self)
        self.edit_palettes_tab = EditPalettesTab(self)
        
        self.main_tabs.addTab(self.preview_tab, "Preview")
        self.main_tabs.addTab(self.edit_tiles_tab, "Edit Tiles")
        self.main_tabs.addTab(self.edit_palettes_tab, "Edit Palettes")

        # Custom status bar at the bottom
        self.custom_status_bar = CustomStatusBar()
        main_layout.addWidget(self.custom_status_bar)

        # Menu bar
        self.menu_bar = MenuBar(self)

        # Store references to actions for easy access
        self.action_save_tileset = self.menu_bar.action_save_tileset
        self.action_append_tiles = self.menu_bar.action_append_tiles
        self.action_open_tilemap = self.menu_bar.action_open_tilemap
        self.action_save_tilemap = self.menu_bar.action_save_tilemap
        self.action_save_selection = self.menu_bar.action_save_selection
        self.action_status_bar = self.menu_bar.action_status_bar

    def show_color_rgb(self, r, g, b):
        self.current_status_message = f"RGB: ({r}, {g}, {b})"
        self.custom_status_bar.show_message(self.current_status_message)

    def open_image_for_conversion(self):
        """Open image for conversion (File -> Open Image)"""
        input_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select image to convert",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
        )
        if not input_path:
            return

        dialog = ConversionDialog(image_path=input_path, parent=self)
        dialog.exec()

    def open_tileset(self):
        """Open tileset image (Tileset -> Open)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Tileset",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
        )
        if not file_path:
            return
        
        try:
            # Load and display the tileset in Edit Tiles tab
            pil_img = PilImage.open(file_path)
            self.display_tileset(pil_img)
            
            # Switch to Edit Tiles tab
            self.main_tabs.setCurrentIndex(1)
            
            # Update status message
            self.current_status_message = f"Tileset loaded: {os.path.basename(file_path)}"
            self.custom_status_bar.show_message(self.current_status_message)
            
        except Exception as e:
            self.current_status_message = f"Error loading tileset: {str(e)}"
            self.custom_status_bar.show_message(self.current_status_message)
            QMessageBox.warning(self, "Error", f"Could not load tileset:\n{str(e)}")

    def save_tileset(self):
        # Placeholder for save tileset functionality
        pass

    def append_tiles(self):
        # Placeholder for append tiles functionality
        pass

    def open_tilemap(self):
        # Placeholder for open tilemap functionality
        pass

    def save_tilemap(self):
        # Placeholder for save tilemap functionality
        pass

    def save_selection(self):
        # Placeholder for save selection functionality
        pass

    def open_palette(self):
        """Placeholder for open palette functionality"""
        # TODO: Implementar apertura de paleta
        self.current_status_message = "Open Palette functionality not implemented yet"
        self.custom_status_bar.show_message(self.current_status_message)

    def save_palette(self):
        """Placeholder for save palette functionality"""
        # TODO: Implementar guardado de paleta
        self.current_status_message = "Save Palette functionality not implemented yet"
        self.custom_status_bar.show_message(self.current_status_message)

    def toggle_keep_transparent(self, checked):
        """Toggle Keep Transparent Color setting"""
        self.current_status_message = f"Keep Transparent Color: {'Enabled' if checked else 'Disabled'}"
        self.custom_status_bar.show_message(self.current_status_message)
        # TODO: Implementar lógica para mantener color transparente

    def toggle_keep_temp(self, checked):
        """Toggle Keep Temp setting"""
        self.current_status_message = f"Keep Temp Files: {'Enabled' if checked else 'Disabled'}"
        self.custom_status_bar.show_message(self.current_status_message)
        # TODO: Implementar lógica para mantener archivos temporales

    def reset_zoom(self):
        # Placeholder for reset zoom functionality
        pass

    def zoom_in(self):
        # Placeholder for zoom in functionality
        pass

    def zoom_out(self):
        # Placeholder for zoom out functionality
        pass

    def toggle_grid(self, checked):
        # Placeholder for grid toggle functionality
        pass

    def toggle_status_bar(self, checked):
        self.custom_status_bar.setVisible(checked)

    def toggle_logging_bar(self, checked):
        # Placeholder for logging bar toggle functionality
        pass

    def change_language(self, language_code):
        # Update check states
        for lang_code, action in self.menu_bar.language_actions.items():
            action.setChecked(lang_code == language_code)
        
        # Placeholder for language change functionality
        print(f"Language changed to: {language_code}")

    def change_theme(self, theme_code):
        # Update check states
        for theme_c, action in self.menu_bar.theme_actions.items():
            action.setChecked(theme_c == theme_code)
        
        # Placeholder for theme change functionality
        print(f"Theme changed to: {theme_code}")

    def toggle_save_preview(self, checked):
        """Toggle Save Preview Files setting"""
        self.current_status_message = f"Save Preview Files: {'Enabled' if checked else 'Disabled'}"
        self.custom_status_bar.show_message(self.current_status_message)
        # TODO: Implementar lógica para guardar archivos de preview

    def show_contribute(self):
        """Show contribution information dialog"""
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
        msg_box.setWindowTitle("Support Development")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(contribute_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def display_tileset(self, pil_img):
        """Display tileset image in the Edit Tiles section with crisp pixels"""
        self.edit_tiles_tab.edit_tileset_scene.clear()
        w, h = pil_img.size
        
        # Convert PIL image to QPixmap and display
        qimg = pil_to_qimage(pil_img)
        pixmap = QPixmap.fromImage(qimg)
        
        # Add pixmap to scene without scaling for crisp pixels
        pixmap_item = self.edit_tiles_tab.edit_tileset_scene.addPixmap(pixmap)
        self.edit_tiles_tab.edit_tileset_scene.setSceneRect(0, 0, w, h)
        
        # Reset zoom to 1:1 for crisp pixel display
        self.edit_tiles_tab.edit_tileset_view.resetTransform()
        self.edit_tiles_tab.edit_tileset_view.scale(1.0, 1.0)
        self.edit_tiles_tab.edit_tileset_view.centerOn(pixmap_item)

    def show_about(self):
        about_text = """
        <h3>GBA Background Studio</h3>
        <p>A comprehensive tool for creating and editing Game Boy Advance background graphics.</p>
        
        <p><b>📥 Downloads:</b><br>
        <a href="https://github.com/CompuMaxx">https://github.com/CompuMaxx</a></p>
        
        <p><b>💬 Contact:</b><br>
        Discord: <a href="https://discordapp.com/users/213803341988364289">CompuMax</a></p>
        
        <p><b>👨‍💻 Developer:</b><br>
        CompuMax</p>
        
        <p><b>© Copyright 2025</b><br>
        All rights reserved</p>
        
        <p>Developed with ❤️ for the GBA homebrew community</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About GBA Background Studio")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        
        # Hacer los enlaces clickeables
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        
    def load_conversion_results(self):
        """Updates the interface with conversion results."""
        tiles_path = "output/tiles.png"
        preview_path = "temp/preview/preview.png"
        palette_path = "temp/preview/palette.pal"

        # === 1. LOAD TILESET IN EDIT TILES TAB ===
        if os.path.exists(tiles_path):
            tiles_img = PilImage.open(tiles_path)
            self.display_tileset(tiles_img)

        # === 2. LOAD PREVIEW IN PREVIEW TAB ===
        if os.path.exists(preview_path):
            preview_img = PilImage.open(preview_path)
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            self.preview_tab.preview_image_scene.clear()
            self.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            self.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
            
            # Center the preview image
            self.preview_tab.preview_image_view.resetTransform()
            self.preview_tab.preview_image_view.scale(1.0, 1.0)
            self.preview_tab.preview_image_view.centerOn(self.preview_tab.preview_image_scene.items()[0])

        # === 3. LOAD UNIFIED PALETTE IN PREVIEW PALETTE ===
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
                        
                # Display the loaded palette
                self.preview_tab.display_palette_colors(palette_colors)

            except Exception as e:
                print(f"Error loading palette: {e}")
                # Fallback to grayscale if there's an error
                grayscale_colors = generate_grayscale_palette()
                self.preview_tab.display_palette_colors(grayscale_colors)

        # Update status message
        self.current_status_message = "✓ Conversion completed"
        self.custom_status_bar.show_message(self.current_status_message)
        
        # Enable relevant menu actions after conversion
        self.action_save_tileset.setEnabled(True)
        self.action_append_tiles.setEnabled(True)
        self.action_open_tilemap.setEnabled(True)
        self.action_save_tilemap.setEnabled(True)
        self.action_save_selection.setEnabled(True)
        
        # Switch to Preview tab to show results
        self.main_tabs.setCurrentIndex(0)
