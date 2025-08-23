# ui/menu_bar.py
from PySide6.QtWidgets import QMenu, QMessageBox, QFileDialog
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt
import os
import shutil


class MenuBar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()
        self.create_menus()

    def create_menus(self):
        # File menu
        file_menu = self.menu_bar.addMenu("&File")
        
        action_open_image = file_menu.addAction("Open Image...")
        action_open_image.setShortcut("Ctrl+O")
        action_open_image.triggered.connect(self.main_window.open_image_for_conversion)
        
        file_menu.addSeparator()
        
        action_export_files = file_menu.addAction("Export Files...")
        action_export_files.setShortcut("Ctrl+E")
        action_export_files.triggered.connect(self.export_files)
        
        file_menu.addSeparator()
        
        action_exit = file_menu.addAction("Exit")
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.main_window.close)

        # Tileset menu
        tileset_menu = self.menu_bar.addMenu("&Tileset")
        
        action_open_tileset = tileset_menu.addAction("Open")
        action_open_tileset.setShortcut("Ctrl+I")
        action_open_tileset.triggered.connect(self.main_window.open_tileset)
        
        self.action_save_tileset = tileset_menu.addAction("Save")
        self.action_save_tileset.setShortcut("Ctrl+S")
        self.action_save_tileset.triggered.connect(self.main_window.save_tileset)
        self.action_save_tileset.setEnabled(False)
        
        self.action_append_tiles = tileset_menu.addAction("Append Tiles")
        self.action_append_tiles.triggered.connect(self.main_window.append_tiles)
        self.action_append_tiles.setEnabled(False)

        # Tilemap menu
        tilemap_menu = self.menu_bar.addMenu("&Tilemap")
        
        self.action_open_tilemap = tilemap_menu.addAction("Open")
        self.action_open_tilemap.setShortcut("Ctrl+Shift+O")
        self.action_open_tilemap.triggered.connect(self.main_window.open_tilemap)
        self.action_open_tilemap.setEnabled(False)
        
        self.action_save_tilemap = tilemap_menu.addAction("Save")
        self.action_save_tilemap.setShortcut("Ctrl+Shift+S")
        self.action_save_tilemap.triggered.connect(self.main_window.save_tilemap)
        self.action_save_tilemap.setEnabled(False)
        
        self.action_save_selection = tilemap_menu.addAction("Save Selection")
        self.action_save_selection.triggered.connect(self.main_window.save_selection)
        self.action_save_selection.setEnabled(False)

        # Palette menu (NUEVO)
        palette_menu = self.menu_bar.addMenu("&Palette")
        
        self.action_open_palette = palette_menu.addAction("Open")
        self.action_open_palette.setShortcut("Ctrl+P")
        self.action_open_palette.triggered.connect(self.main_window.open_palette)
        self.action_open_palette.setEnabled(False)
        
        self.action_save_palette = palette_menu.addAction("Save")
        self.action_save_palette.setShortcut("Ctrl+Shift+P")
        self.action_save_palette.triggered.connect(self.main_window.save_palette)
        self.action_save_palette.setEnabled(False)

        # Edit menu
        edit_menu = self.menu_bar.addMenu("&Edit")
        action_undo = edit_menu.addAction("Undo")
        action_undo.setShortcut("Ctrl+Z")
        action_undo.setEnabled(False)
        action_redo = edit_menu.addAction("Redo")
        action_redo.setShortcut("Ctrl+Y")
        action_redo.setEnabled(False)

        # View menu
        view_menu = self.menu_bar.addMenu("&View")
        
        # Tab navigation
        view_menu.addAction("Preview Tab").triggered.connect(lambda: self.main_window.main_tabs.setCurrentIndex(0))
        view_menu.addAction("Edit Tiles Tab").triggered.connect(lambda: self.main_window.main_tabs.setCurrentIndex(1))
        view_menu.addAction("Edit Palettes Tab").triggered.connect(lambda: self.main_window.main_tabs.setCurrentIndex(2))
        
        view_menu.addSeparator()
        
        action_reset_zoom = view_menu.addAction("Reset Zoom")
        action_reset_zoom.setShortcut("Ctrl+0")
        action_reset_zoom.triggered.connect(self.main_window.reset_zoom)
        
        action_zoom_in = view_menu.addAction("Zoom In")
        action_zoom_in.setShortcut("Ctrl++")
        action_zoom_in.triggered.connect(self.main_window.zoom_in)
        
        action_zoom_out = view_menu.addAction("Zoom Out")
        action_zoom_out.setShortcut("Ctrl+-")
        action_zoom_out.triggered.connect(self.main_window.zoom_out)
        
        view_menu.addSeparator()
        
        action_grid = view_menu.addAction("Grid")
        action_grid.setShortcut("Ctrl+G")
        action_grid.setCheckable(True)
        action_grid.setChecked(False)
        action_grid.triggered.connect(self.main_window.toggle_grid)
        
        view_menu.addSeparator()
        
        self.action_status_bar = view_menu.addAction("Status Bar")
        self.action_status_bar.setCheckable(True)
        self.action_status_bar.setChecked(True)
        self.action_status_bar.triggered.connect(self.main_window.toggle_status_bar)

        # Settings menu
        settings_menu = self.menu_bar.addMenu("&Settings")
        
        # Language submenu
        language_menu = QMenu("Language", self.main_window)
        self.language_actions = {}
        languages = {
            "english": "English",
            "spanish": "Español",
            "br_portuguese": "Português (BR)",
            "french": "Français",
            "german": "Deutsch",
            "italian": "Italiano",
            "portuguese": "Português",
            "indonesian": "Bahasa Indonesia",
            "hindi": "हिन्दी",
            "russian": "Русский",
            "japanese": "日本語",
            "chinese": "中文"
        }
        
        for lang_code, lang_name in languages.items():
            action = language_menu.addAction(lang_name)
            action.setCheckable(True)
            action.setChecked(lang_code == "english")
            action.triggered.connect(lambda checked, lc=lang_code: self.main_window.change_language(lc))
            self.language_actions[lang_code] = action
        
        settings_menu.addMenu(language_menu)
        
        # Theme submenu
        theme_menu = QMenu("Theme", self.main_window)
        self.theme_actions = {}
        themes = {
            "light": "Light",
            "dark": "Dark"
        }
        
        for theme_code, theme_name in themes.items():
            action = theme_menu.addAction(theme_name)
            action.setCheckable(True)
            action.setChecked(theme_code == "light")
            action.triggered.connect(lambda checked, t=theme_code: self.main_window.change_theme(t))
            self.theme_actions[theme_code] = action
        
        settings_menu.addMenu(theme_menu)
        
        settings_menu.addSeparator()
        
        # NUEVAS OPCIONES EN SETTINGS
        self.action_save_preview = settings_menu.addAction("Save Preview Files")
        self.action_save_preview.setCheckable(True)
        self.action_save_preview.setChecked(False)
        self.action_save_preview.triggered.connect(self.main_window.toggle_save_preview)
        
        self.action_keep_transparent = settings_menu.addAction("Keep Transparent Color")
        self.action_keep_transparent.setCheckable(True)
        self.action_keep_transparent.setChecked(False)
        self.action_keep_transparent.triggered.connect(self.main_window.toggle_keep_transparent)
        
        self.action_keep_temp = settings_menu.addAction("Keep Temp Files")
        self.action_keep_temp.setCheckable(True)
        self.action_keep_temp.setChecked(False)
        self.action_keep_temp.triggered.connect(self.main_window.toggle_keep_temp)

        # Tools menu
        tools_menu = self.menu_bar.addMenu("&Tools")
        # Placeholder for future tools submenus
        action_preview = tools_menu.addAction("Preview")
        action_preview.setEnabled(False)
        action_export = tools_menu.addAction("Export")
        action_export.setEnabled(False)

        # Help menu
        help_menu = self.menu_bar.addMenu("&Help")
        
        action_show_logs = help_menu.addAction("Show Logs In Explorer")
        action_show_logs.triggered.connect(self.show_logs_in_explorer)
        
        action_about = help_menu.addAction("About")
        action_about.triggered.connect(self.main_window.show_about)
        
        action_contribute = help_menu.addAction("Contribute")
        action_contribute.triggered.connect(self.main_window.show_contribute)

    def export_files(self):
        """Export output files to selected directory"""
        output_dir = "output"
        if not os.path.exists(output_dir) or not os.listdir(output_dir):
            QMessageBox.information(self.main_window, "Export Files", 
                                  "No files to export. Please convert an image first.")
            return
        
        target_dir = QFileDialog.getExistingDirectory(
            self.main_window,
            "Select Export Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not target_dir:
            return
        
        try:
            # Copy all files from output directory
            for file_name in os.listdir(output_dir):
                source_path = os.path.join(output_dir, file_name)
                target_path = os.path.join(target_dir, file_name)
                
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, target_path)
            
            self.main_window.current_status_message = f"Files exported to: {target_dir}"
            self.main_window.custom_status_bar.show_message(self.main_window.current_status_message)
            QMessageBox.information(self.main_window, "Export Complete", 
                                  f"Files successfully exported to:\n{target_dir}")
            
        except Exception as e:
            error_msg = f"Error exporting files: {str(e)}"
            self.main_window.current_status_message = error_msg
            self.main_window.custom_status_bar.show_message(self.main_window.current_status_message)
            QMessageBox.warning(self.main_window, "Export Error", error_msg)

    def show_logs_in_explorer(self):
        """Open logs directory in file explorer"""
        logs_dir = "logs"
        try:
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Open the directory in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(logs_dir)
            elif os.name == 'posix':  # macOS or Linux
                if os.uname().sysname == 'Darwin':  # macOS
                    import subprocess
                    subprocess.run(['open', logs_dir])
                else:  # Linux
                    import subprocess
                    subprocess.run(['xdg-open', logs_dir])
            
            self.main_window.current_status_message = "Opened logs directory"
            self.main_window.custom_status_bar.show_message(self.main_window.current_status_message)
            
        except Exception as e:
            self.main_window.current_status_message = f"Error opening logs directory: {str(e)}"
            self.main_window.custom_status_bar.show_message(self.main_window.current_status_message)
            QMessageBox.warning(self.main_window, "Error", f"Could not open logs directory:\n{str(e)}")
