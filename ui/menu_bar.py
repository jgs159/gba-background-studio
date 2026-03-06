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
        file_menu = self.menu_bar.addMenu(self.main_window.translator.tr("file_menu"))
        
        action_open_image = file_menu.addAction(self.main_window.translator.tr("open_image"))
        action_open_image.setShortcut("Ctrl+O")
        action_open_image.triggered.connect(self.main_window.open_image_for_conversion)
        
        file_menu.addSeparator()
        
        action_export_files = file_menu.addAction(self.main_window.translator.tr("export_files"))
        action_export_files.setShortcut("Ctrl+E")
        action_export_files.triggered.connect(self.export_files)
        
        file_menu.addSeparator()
        
        action_exit = file_menu.addAction(self.main_window.translator.tr("exit_app"))
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.main_window.close)

        # Tileset menu
        tileset_menu = self.menu_bar.addMenu(self.main_window.translator.tr("tileset_menu"))
        
        action_open_tileset = tileset_menu.addAction(self.main_window.translator.tr("open_tileset"))
        action_open_tileset.setShortcut("Ctrl+I")
        action_open_tileset.triggered.connect(self.main_window.open_tileset)
        
        self.action_save_tileset = tileset_menu.addAction(self.main_window.translator.tr("save_tileset"))
        self.action_save_tileset.setShortcut("Ctrl+S")
        self.action_save_tileset.triggered.connect(self.main_window.save_tileset)
        self.action_save_tileset.setEnabled(False)
        
        # Tilemap menu
        tilemap_menu = self.menu_bar.addMenu(self.main_window.translator.tr("tilemap_menu"))
        
        self.action_open_tilemap = tilemap_menu.addAction(self.main_window.translator.tr("open_tilemap"))
        self.action_open_tilemap.setShortcut("Ctrl+Shift+O")
        self.action_open_tilemap.triggered.connect(self.main_window.open_tilemap)
        self.action_open_tilemap.setEnabled(False)
        
        self.action_new_tilemap = tilemap_menu.addAction(self.main_window.translator.tr("new_tilemap"))
        self.action_new_tilemap.setShortcut("Ctrl+Shift+N")
        self.action_new_tilemap.triggered.connect(self.main_window.new_tilemap)
        self.action_new_tilemap.setEnabled(False)
        
        self.action_save_tilemap = tilemap_menu.addAction(self.main_window.translator.tr("save_tilemap"))
        self.action_save_tilemap.setShortcut("Ctrl+Shift+S")
        self.action_save_tilemap.triggered.connect(self.main_window.save_tilemap)
        self.action_save_tilemap.setEnabled(False)
        
        self.action_save_selection = tilemap_menu.addAction(self.main_window.translator.tr("save_selection"))
        self.action_save_selection.triggered.connect(self.main_window.save_selection)
        self.action_save_selection.setEnabled(False)

        # Palette menu
        palette_menu = self.menu_bar.addMenu(self.main_window.translator.tr("palette_menu"))
        
        self.action_open_palette = palette_menu.addAction(self.main_window.translator.tr("open_palette"))
        self.action_open_palette.setShortcut("Ctrl+P")
        self.action_open_palette.triggered.connect(self.main_window.open_palette)
        self.action_open_palette.setEnabled(True)
        
        self.action_save_palette = palette_menu.addAction(self.main_window.translator.tr("save_palette"))
        self.action_save_palette.setShortcut("Ctrl+Shift+P")
        self.action_save_palette.triggered.connect(self.main_window.save_palette)
        self.action_save_palette.setEnabled(True)

        # Edit menu
        edit_menu = self.menu_bar.addMenu(self.main_window.translator.tr("edit_menu"))
        
        self.action_undo = edit_menu.addAction(self.main_window.translator.tr("undo"))
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.main_window.undo)
        self.action_undo.setEnabled(False)

        self.action_redo = edit_menu.addAction(self.main_window.translator.tr("redo"))
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.main_window.redo)
        self.action_redo.setEnabled(False)

        # View menu
        view_menu = self.menu_bar.addMenu(self.main_window.translator.tr("view_menu"))
        
        # Tab navigation
        view_menu.addAction(self.main_window.translator.tr("preview_tab_menu")).triggered.connect(lambda: self.main_window.main_tabs.setCurrentIndex(0))
        view_menu.addAction(self.main_window.translator.tr("edit_tiles_tab_menu")).triggered.connect(lambda: self.main_window.main_tabs.setCurrentIndex(1))
        view_menu.addAction(self.main_window.translator.tr("edit_palettes_tab_menu")).triggered.connect(lambda: self.main_window.main_tabs.setCurrentIndex(2))
        
        view_menu.addSeparator()
        
        action_reset_zoom = view_menu.addAction(self.main_window.translator.tr("reset_zoom"))
        action_reset_zoom.setShortcut("Ctrl+0")
        action_reset_zoom.triggered.connect(self.main_window.reset_zoom)
        
        action_zoom_in = view_menu.addAction(self.main_window.translator.tr("zoom_in"))
        action_zoom_in.setShortcut("Ctrl++")
        action_zoom_in.triggered.connect(self.main_window.zoom_in)
        
        action_zoom_out = view_menu.addAction(self.main_window.translator.tr("zoom_out"))
        action_zoom_out.setShortcut("Ctrl+-")
        action_zoom_out.triggered.connect(self.main_window.zoom_out)
        
        view_menu.addSeparator()
        
        # Grid toggle action
        self.action_grid = view_menu.addAction(self.main_window.translator.tr("grid_toggle"))
        self.action_grid.setShortcut("Ctrl+G")
        self.action_grid.setCheckable(True)

        grid_visible = self.main_window.config_manager.getboolean('SETTINGS', 'show_grid', False)
        self.action_grid.setChecked(grid_visible)
        self.action_grid.triggered.connect(self.main_window.toggle_grid)
        
        view_menu.addSeparator()
        
        self.action_status_bar = view_menu.addAction(self.main_window.translator.tr("status_bar_toggle"))
        self.action_status_bar.setCheckable(True)
        self.action_status_bar.setChecked(True)
        self.action_status_bar.triggered.connect(self.main_window.toggle_status_bar)

        # Settings menu
        settings_menu = self.menu_bar.addMenu(self.main_window.translator.tr("settings_menu"))
        
        # Language submenu
        language_menu = QMenu(self.main_window.translator.tr("language_menu"), self.main_window)
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
            action.triggered.connect(lambda checked, lc=lang_code: self.main_window.change_language(lc))
            self.language_actions[lang_code] = action
        
        settings_menu.addMenu(language_menu)
        
        # Theme submenu
        theme_menu = QMenu(self.main_window.translator.tr("theme_menu"), self.main_window)
        self.theme_actions = {}
        themes = {
            "light": "Light",
            "dark": "Dark"
        }
        
        for theme_code, theme_name in themes.items():
            action = theme_menu.addAction(theme_name)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, t=theme_code: self.main_window.change_theme(t))
            self.theme_actions[theme_code] = action
        
        settings_menu.addMenu(theme_menu)
        
        settings_menu.addSeparator()
        
        # Option's Settings
        self.action_save_preview = settings_menu.addAction(self.main_window.translator.tr("save_preview"))
        self.action_save_preview.setCheckable(True)
        self.action_save_preview.triggered.connect(self.main_window.toggle_save_preview)
        
        self.action_keep_transparent = settings_menu.addAction(self.main_window.translator.tr("keep_transparent"))
        self.action_keep_transparent.setCheckable(True)
        self.action_keep_transparent.triggered.connect(self.main_window.toggle_keep_transparent)
        
        self.action_keep_temp = settings_menu.addAction(self.main_window.translator.tr("keep_temp"))
        self.action_keep_temp.setCheckable(True)
        self.action_keep_temp.triggered.connect(self.main_window.toggle_keep_temp)

        self.action_load_last_output = settings_menu.addAction(self.main_window.translator.tr("load_last_output"))
        self.action_load_last_output.setCheckable(True)
        self.action_load_last_output.setChecked(self.main_window.load_last_output)
        self.action_load_last_output.triggered.connect(self.main_window.toggle_load_last_output)

        self.action_save_conversion_params = settings_menu.addAction(self.main_window.translator.tr("save_conversion_params"))
        self.action_save_conversion_params.setCheckable(True)
        self.action_save_conversion_params.setChecked(self.main_window.save_conversion_params)
        self.action_save_conversion_params.triggered.connect(self.main_window.toggle_save_conversion_params)

        self.action_show_success_dialog = settings_menu.addAction(self.main_window.translator.tr("show_success_dialog"))
        self.action_show_success_dialog.setCheckable(True)
        self.action_show_success_dialog.triggered.connect(self.main_window.toggle_show_success_dialog)

        # Help menu
        help_menu = self.menu_bar.addMenu(self.main_window.translator.tr("help_menu"))
        
        action_about = help_menu.addAction(self.main_window.translator.tr("about"))
        action_about.triggered.connect(self.main_window.show_about)
        
        action_contribute = help_menu.addAction(self.main_window.translator.tr("contribute"))
        action_contribute.triggered.connect(self.main_window.show_contribute)

    def export_files(self):
        """Export output files to selected directory"""
        output_dir = "output"
        if not os.path.exists(output_dir) or not os.listdir(output_dir):
            QMessageBox.information(self.main_window, self.main_window.translator.tr("export_files"), 
                                  self.main_window.translator.tr("no_files_to_export"))
            return
        
        target_dir = QFileDialog.getExistingDirectory(
            self.main_window,
            self.main_window.translator.tr("select_export_directory"),
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
            
            QMessageBox.information(self.main_window, self.main_window.translator.tr("export_complete"), 
                                  self.main_window.translator.tr("export_success").format(path=target_dir))
            
        except Exception as e:
            error_msg = self.main_window.translator.tr("export_error").format(error=str(e))
            QMessageBox.warning(self.main_window, self.main_window.translator.tr("export_error_title"), error_msg)
