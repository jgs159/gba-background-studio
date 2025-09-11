# core/library_loader.py
import importlib
import time
from types import ModuleType
from typing import Dict, List, Tuple

class LibraryLoader:
    def __init__(self):
        self.libraries_to_preload = [
            "PySide6.QtCore",
            "PySide6.QtGui", 
            "PySide6.QtWidgets",
            "PIL.Image",
            "PIL.ImageOps",
            "numpy",
            "cv2",
        ]
    
    def preload_libraries(self, progress_callback=None):
        total = len(self.libraries_to_preload)
        
        for i, module_name in enumerate(self.libraries_to_preload):
            try:
                if progress_callback:
                    progress = int((i / total) * 100)
                    progress_callback(progress, f"Precargando {module_name}...")
                
                importlib.import_module(module_name)
                
                time.sleep(0.05)
                
            except ImportError as e:
                print(f"⚠️ No se pudo precargar {module_name}: {e}")
                continue
        
        if progress_callback:
            progress_callback(100, "¡Precarga completada!")
