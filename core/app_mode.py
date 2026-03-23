# core/app_mode.py
_gui_mode = False

def set_gui_mode(enabled: bool):
    global _gui_mode
    _gui_mode = enabled

def is_gui_mode() -> bool:
    return _gui_mode
