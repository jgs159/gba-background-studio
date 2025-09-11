# main.py
import os
os.environ['JOBLIB_WORKER_COUNT'] = '4'
os.environ['JOBLIB_MULTIPROCESSING'] = '0'
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

import sys
import importlib
import time

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    language = "english"
    try:
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        language = config_manager.get('SETTINGS', 'language', 'english')
    except Exception as e:
        print(f"Error loading config, using default English: {e}")
    
    from utils.translator import Translator
    translator = Translator(lang_dir="lang", default_lang=language)
    
    from ui.splash_screen import GBASplashScreen
    splash = GBASplashScreen(translator)
    splash.show()
    
    libraries_to_preload = [
        "PySide6.QtCore",
        "PySide6.QtGui", 
        "PySide6.QtWidgets",
        "PIL.Image",
        "PIL.ImageOps",
        "core.image_utils",
        "core.palette_utils",
        "core.config_manager",
    ]
    
    total = len(libraries_to_preload)
    for i, module_name in enumerate(libraries_to_preload):
        try:
            progress = int((i / total) * 80)
            module_display_name = module_name.split('.')[-1]
            splash.set_progress(progress, f"Loading {module_display_name}...")
            
            importlib.import_module(module_name)
            time.sleep(0.03)
            
        except Exception as e:
            print(f"Error precargando {module_name}: {e}")
            continue
    
    splash.set_progress(90, "Initializing interface...")
    time.sleep(0.3)
    
    from ui.main_window import GBABackgroundStudio
    window = GBABackgroundStudio()
    
    splash.set_progress(100, "Ready!")
    time.sleep(0.2)
    
    window.show()
    splash.finish(window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()