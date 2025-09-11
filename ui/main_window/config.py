# ui/main_window/config.py
def load_configuration(main_window):
    main_window.save_preview_files = main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
    main_window.keep_transparent_color = main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)
    main_window.keep_temp_files = main_window.config_manager.getboolean('SETTINGS', 'keep_temp_files', False)
    main_window.load_last_output = main_window.config_manager.getboolean('SETTINGS', 'load_last_output', True)
    main_window.show_success_dialog = main_window.config_manager.getboolean('SETTINGS', 'show_success_dialog', True)
    main_window.save_conversion_params = main_window.config_manager.getboolean('SETTINGS', 'save_conversion_params', True)

def apply_configuration_to_menu(main_window):
    if hasattr(main_window, 'menu_bar'):
        main_window.menu_bar.action_save_preview.setChecked(main_window.save_preview_files)
        main_window.menu_bar.action_keep_transparent.setChecked(main_window.keep_transparent_color)
        main_window.menu_bar.action_keep_temp.setChecked(main_window.keep_temp_files)
        main_window.menu_bar.action_load_last_output.setChecked(main_window.load_last_output)
        main_window.menu_bar.action_show_success_dialog.setChecked(main_window.show_success_dialog)
        main_window.menu_bar.action_save_conversion_params.setChecked(main_window.save_conversion_params)
        
        theme = main_window.config_manager.get('SETTINGS', 'theme', 'light')
        for theme_code, action in main_window.menu_bar.theme_actions.items():
            action.setChecked(theme_code == theme)
        
        language = main_window.config_manager.get('SETTINGS', 'language', 'english')
        for lang_code, action in main_window.menu_bar.language_actions.items():
            action.setChecked(lang_code == language)

def setup_grids(main_window):
    main_window.grid_manager.register_view(main_window.edit_tiles_tab.edit_tileset_view, "tileset")
    main_window.grid_manager.register_view(main_window.edit_tiles_tab.edit_tilemap_view, "tilemap_edit")
    main_window.grid_manager.register_view(main_window.edit_palettes_tab.edit_palettes_view, "palettes")
    main_window.grid_manager.register_view(main_window.edit_palettes_tab.edit_tilemap2_view, "tilemap_palettes")
    
    grid_visible = main_window.config_manager.getboolean('SETTINGS', 'show_grid', False)
    main_window.grid_manager.set_grid_visible(grid_visible)
    
    if hasattr(main_window, 'menu_bar') and hasattr(main_window.menu_bar, 'action_grid'):
        main_window.menu_bar.action_grid.setChecked(grid_visible)

def toggle_show_success_dialog(main_window, checked):
    main_window.show_success_dialog = checked
    main_window.config_manager.set('SETTINGS', 'show_success_dialog', checked)

def toggle_load_last_output(main_window, checked):
    main_window.load_last_output = checked
    main_window.config_manager.set('SETTINGS', 'load_last_output', checked)

def toggle_save_conversion_params(main_window, checked):
    main_window.save_conversion_params = checked
    main_window.config_manager.set('SETTINGS', 'save_conversion_params', checked)

def toggle_save_preview(main_window, checked):
    main_window.save_preview_files = checked
    main_window.config_manager.set('SETTINGS', 'save_preview_files', checked)

def toggle_keep_transparent(main_window, checked):
    main_window.keep_transparent_color = checked
    main_window.config_manager.set('SETTINGS', 'keep_transparent_color', checked)

def toggle_keep_temp(main_window, checked):
    main_window.keep_temp_files = checked
    main_window.config_manager.set('SETTINGS', 'keep_temp_files', checked)

def toggle_grid(main_window, checked):
    main_window.grid_manager.set_grid_visible(checked)
    main_window.config_manager.set('SETTINGS', 'show_grid', checked)

def toggle_status_bar(main_window, checked):
    main_window.custom_status_bar.setVisible(checked)
