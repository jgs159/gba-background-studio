# ui/main_window/utils.py
def change_language(main_window, language_code):
    main_window.config_manager.set('SETTINGS', 'language', language_code)
    main_window.translator.load_language(language_code)
    for lang_code, action in main_window.menu_bar.language_actions.items():
        action.setChecked(lang_code == language_code)
    
    retranslate_ui(main_window)

def change_theme(main_window, theme_code):
    for theme_c, action in main_window.menu_bar.theme_actions.items():
        action.setChecked(theme_c == theme_code)
    
    main_window.config_manager.set('SETTINGS', 'theme', theme_code)
    
    from utils.theme_manager import apply_theme
    apply_theme(theme_code)

def retranslate_ui(main_window):
    main_window.main_tabs.setTabText(0, main_window.translator.tr("preview_tab"))
    main_window.main_tabs.setTabText(1, main_window.translator.tr("edit_tiles_tab"))
    main_window.main_tabs.setTabText(2, main_window.translator.tr("edit_palettes_tab"))
    main_window.menu_bar.retranslate_menus()
    if hasattr(main_window, 'preview_tab'):
        main_window.preview_tab.retranslate_ui()
    if hasattr(main_window, 'edit_tiles_tab'):
        main_window.edit_tiles_tab.retranslate_ui()
    if hasattr(main_window, 'edit_palettes_tab'):
        main_window.edit_palettes_tab.retranslate_ui()
    if hasattr(main_window, 'context_toolbar'):
        main_window.context_toolbar.retranslate_ui()
