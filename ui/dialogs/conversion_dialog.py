# ui/dialogs/conversion_dialog.py
from PySide6.QtWidgets import QDialog
from PIL import Image as PilImage
from .conversion_dialog_ui import ConversionDialogUI
from .conversion_dialog_logic import ConversionDialogLogic
from .conversion_dialog_config import ConversionDialogConfig
from .auto_spinbox import AutoSpinBox

class ConversionDialog(QDialog, ConversionDialogUI, ConversionDialogLogic, ConversionDialogConfig):
    PRESETS_TEXT = {
        "Original": None,
        "Screen Size (256x160)": (32, 20),
        "Screen Size 0 (256x256)": (32, 32),
        "Screen Size 1 (512x256)": (64, 32),
        "Screen Size 2 (256x512)": (32, 64),
        "Screen Size 3 (512x512)": (64, 64),
        "Custom": None
    }
    PRESETS_ROT = {
        "16×16 (128×128)": (16, 16),
        "32×32 (256×256)": (32, 32),
        "64×64 (512×512)": (64, 64),
        "128×128 (1024×1024)": (128, 128),
    }
    PRESETS = PRESETS_TEXT  # default, overridden dynamically

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.result = None
        self.img_width_tiles = 32
        self.img_height_tiles = 32
        self.output_width_tiles = 32
        self.output_height_tiles = 20
        self.grid_was_visible = False

        try:
            pil_img = PilImage.open(image_path)
            self.img_width_tiles = (pil_img.width // 8)
            self.img_height_tiles = (pil_img.height // 8)
        except:
            pass

        self.setWindowTitle("Convert Image to Tilemap")
        self.setFixedSize(844, 558)
        self.setup_ui()
        self.load_conversion_settings()
