# ui/conversion_dialog.py
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QFrame,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QCheckBox,
    QLabel,
    QStackedWidget,
    QGraphicsView,
    QGraphicsScene,
    QProgressBar,
    QPushButton,
    QMessageBox,
    QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QImage
from PIL import Image as PilImage
import os


class ConversionDialog(QDialog):
    PRESETS = {
        "Original": None,
        "Screen Size (256x160)": (32, 20),
        "BG0 (256x256)": (32, 32),
        "BG1 (512x256)": (64, 32),
        "BG2 (256x512)": (32, 64),
        "BG3 (512x512)": (64, 64),
        "Custom": None
    }

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.result = None
        self.img_width_tiles = 32
        self.img_height_tiles = 32
        self.output_width_tiles = 32
        self.output_height_tiles = 20

        try:
            pil_img = PilImage.open(image_path)
            self.img_width_tiles = (pil_img.width // 8)
            self.img_height_tiles = (pil_img.height // 8)
        except:
            pass

        self.setWindowTitle("Convert Image to Tilemap")
        self.resize(1100, 650)
        self.setMinimumSize(900, 500)
        self.setup_ui()

    def setup_ui(self):
        from PySide6.QtGui import QFont

        layout = QVBoxLayout(self)

        # Main splitter: left (image) 70% / right (params) 30%
        from PySide6.QtWidgets import QSplitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)

        # === LEFT PANEL: Image preview (top 50%) + Preview area (bottom 50%) ===
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Header: Input Image
        input_header = QLabel("Input Image (100% pixels)")
        input_header.setFont(QFont("Arial", 10, QFont.Bold))
        input_header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        input_header.setFixedHeight(30)
        left_layout.addWidget(input_header)

        # Input Image View (100% scale)
        from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
        self.input_view = QGraphicsView()
        self.input_scene = QGraphicsScene()
        self.input_view.setScene(self.input_scene)
        self.input_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.input_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.input_view.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.input_view, 1)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("QFrame { margin: 8px 0; }")
        left_layout.addWidget(separator)

        # Header: Preview Area
        preview_header = QLabel("Preview (after conversion)")
        preview_header.setFont(QFont("Arial", 10, QFont.Bold))
        preview_header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        preview_header.setFixedHeight(30)
        left_layout.addWidget(preview_header)

        # Preview Area (after conversion)
        self.preview_view = QGraphicsView()
        self.preview_scene = QGraphicsScene()
        self.preview_view.setScene(self.preview_scene)
        self.preview_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.preview_view.setStyleSheet("QGraphicsView { background: #e0e0e0; border: 1px solid #ccc; }")
        self.preview_view.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.preview_view, 1)

        # Add left panel to splitter
        main_splitter.addWidget(left_panel)

        # === RIGHT PANEL: Parameters (30%) ===
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        right_layout.setContentsMargins(8, 8, 8, 8)

        params_group = QGroupBox("Conversion Parameters")
        form_layout = QFormLayout()

        # === Palettes (styled like other form labels) ===
        # This ensures "Palettes" has same font/style as "Transparent Color:"
        palette_label = QLabel("Palettes")
        # No need to set font manually — QFormLayout does it
        form_layout.addRow(palette_label, QLabel(""))  # Hack: add empty widget to keep layout

        palette_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 2, 0, 2)
        grid_layout.setSpacing(1)
        palette_widget.setLayout(grid_layout)

        self.palette_checks = []

        for i in range(16):
            # Checkbox
            cb = QCheckBox("")
            cb.setFixedSize(20, 20)
            cb.setChecked(i == 0)
            cb.toggled.connect(self.on_palette_toggled)
            self.palette_checks.append(cb)
            grid_layout.addWidget(cb, 0, i)

            # Label (number)
            label = QLabel(hex(i)[2:].upper())
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(20)
            label.setStyleSheet("QLabel { font-size: 9px; font-weight: bold; color: #555; }")
            grid_layout.addWidget(label, 1, i)

        form_layout.addRow(palette_widget)

        # --transparent-color
        self.transparent_color = QLineEdit("0,0,0")
        self.transparent_color.setPlaceholderText("R,G,B (0-255)")
        form_layout.addRow("Transparent Color:", self.transparent_color)

        # --extra-transparent-tiles
        self.extra_transparent = QSpinBox()
        self.extra_transparent.setRange(0, 10)
        self.extra_transparent.setValue(0)
        form_layout.addRow("Extra Transparent Tiles:", self.extra_transparent)

        # --tileset-width
        self.tileset_width = QSpinBox()
        self.tileset_width.setRange(0, 64)
        self.tileset_width.setValue(0)
        self.tileset_width.setSpecialValueText("Auto")
        form_layout.addRow("Tileset Width (tiles):", self.tileset_width)

        # --origin
        self.origin = QLineEdit("0,0")
        self.origin.setPlaceholderText("x,y or xt,yt")
        form_layout.addRow("Origin:", self.origin)

        # --output-size (Combo + Custom widgets)
        output_hlayout = QHBoxLayout()

        self.output_combo = QComboBox()
        for label in self.PRESETS.keys():
            self.output_combo.addItem(label)
        self.output_combo.setCurrentText("Original")
        self.output_combo.currentTextChanged.connect(self.on_output_size_changed)

        output_hlayout.addWidget(self.output_combo)
        form_layout.addRow("Output Size:", output_hlayout)

        # Custom size stack
        self.custom_stack = QStackedWidget()
        self.custom_none = QWidget()
        self.custom_widget = QWidget()
        self.custom_stack.addWidget(self.custom_none)
        self.custom_stack.addWidget(self.custom_widget)

        custom_layout = QFormLayout()

        self.custom_width = QSpinBox()
        self.custom_width.setRange(1, 64)
        self.custom_width.setValue(32)
        self.custom_width.valueChanged.connect(self.update_output_info)

        self.custom_height = QSpinBox()
        self.custom_height.setRange(1, 64)
        self.custom_height.setValue(20)
        self.custom_height.valueChanged.connect(self.update_output_info)

        custom_layout.addRow("Width (tiles):", self.custom_width)
        custom_layout.addRow("Height (tiles):", self.custom_height)
        self.custom_widget.setLayout(custom_layout)

        form_layout.addRow(self.custom_stack)

        # Output size info
        self.output_info = QLabel("Tamaño de Salida: 256x160 px")
        self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #0066cc; padding: 4px; }")
        form_layout.addRow(self.output_info)

        # --keep-temp
        self.keep_temp = QCheckBox("Keep temp/ folder")
        form_layout.addRow("", self.keep_temp)

        # --keep-transparent
        self.keep_transparent = QCheckBox("Keep transparent color in palette")
        form_layout.addRow("", self.keep_transparent)

        params_group.setLayout(form_layout)
        right_layout.addWidget(params_group)

        # === Progress Bar ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        right_layout.addStretch()

        # Add right panel
        main_splitter.addWidget(right_panel)

        # Set sizes: 70% / 30%
        main_splitter.setSizes([770, 330])

        layout.addWidget(main_splitter)

        # === Buttons ===
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        cancel_btn = QPushButton("Cancel")
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setDefault(True)

        cancel_btn.clicked.connect(self.reject)
        self.convert_btn.clicked.connect(self.on_convert)

        button_layout.addSpacerItem(spacer)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.convert_btn)

        layout.addLayout(button_layout)

        # Load input image at 100%
        self.load_input_image()
        self.on_output_size_changed()

    def on_palette_toggled(self):
        """Ensure at least one palette is selected."""
        if not any(cb.isChecked() for cb in self.palette_checks):
            sender = self.sender()
            sender.setChecked(True)   
    
    def load_input_image(self):
        try:
            pil_img = PilImage.open(self.image_path).convert("RGBA")
            qimg = self.pil_to_qimage(pil_img)
            pix = QPixmap.fromImage(qimg)

            self.input_scene.clear()
            item = self.input_scene.addPixmap(pix)
            self.input_scene.setSceneRect(pix.rect())
            self.input_view.resetTransform()
            self.input_view.scale(1.0, 1.0)
            self.input_view.centerOn(item)
        except Exception as e:
            print(f"Error loading input image: {e}")

    def pil_to_qimage(self, pil_img):
        if pil_img.mode == "RGBA":
            data = pil_img.tobytes("raw", "RGBA")
            return QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
        else:
            rgb_img = pil_img.convert("RGB")
            data = rgb_img.tobytes("raw", "RGB")
            return QImage(data, rgb_img.size[0], rgb_img.size[1], QImage.Format_RGB888)

    def on_output_size_changed(self):
        text = self.output_combo.currentText()
        if text == "Custom":
            self.custom_stack.setCurrentIndex(1)
            self.update_output_info()
        elif text == "Original":
            self.custom_stack.setCurrentIndex(0)
            w_tiles = self.img_width_tiles
            h_tiles = self.img_height_tiles
            w_px, h_px = w_tiles * 8, h_tiles * 8
            self.output_width_tiles = w_tiles
            self.output_height_tiles = h_tiles
            self.output_info.setText(f"Tamaño de Salida: {w_px}x{h_px} px")
        else:
            self.custom_stack.setCurrentIndex(0)
            w_tiles, h_tiles = self.PRESETS[text]
            self.output_width_tiles = w_tiles
            self.output_height_tiles = h_tiles
            w_px, h_px = w_tiles * 8, h_tiles * 8
            self.output_info.setText(f"Tamaño de Salida: {w_px}x{h_px} px")

    def update_output_info(self):
        w_tiles = self.custom_width.value()
        h_tiles = self.custom_height.value()
        w_px, h_px = w_tiles * 8, h_tiles * 8
        if w_px > 512 or h_px > 512:
            self.output_info.setText(f"Tamaño de Salida: {w_px}x{h_px} px ⚠️ Excede 512px")
            self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #cc0000; padding: 4px; }")
        else:
            self.output_info.setText(f"Tamaño de Salida: {w_px}x{h_px} px")
            self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #0066cc; padding: 4px; }")
        self.output_width_tiles = w_tiles
        self.output_height_tiles = h_tiles

    def on_convert(self):
        tc_text = self.transparent_color.text().strip()
        try:
            tc = tuple(map(int, tc_text.split(',')))
            if len(tc) != 3 or not all(0 <= c <= 255 for c in tc):
                raise ValueError
        except:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", "Invalid transparent color. Use 'R,G,B' with values 0-255.")
            return

        self.convert_btn.setEnabled(False)
        self.output_combo.setEnabled(False)
        self.origin.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("Starting...")
        self.progress_bar.setValue(0)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            import core.converter as converter
            converter.LANGUAGE = "eng"

            steps = [
                ("Validating input...", 10),
                ("Splitting into groups...", 25),
                ("Quantizing with IrfanView...", 40),
                ("Applying GBA palette...", 55),
                ("Rebuilding image...", 70),
                ("Generating assets...", 85),
                ("Cleaning temp files...", 95),
                ("Done", 100)
            ]

            import io
            import sys
            from contextlib import redirect_stdout

            def update_progress(text):
                for keyword, value in [
                    ("Validating", 10),
                    ("Splitting", 25),
                    ("Quantizing", 40),
                    ("Applying", 55),
                    ("Rebuilding", 70),
                    ("Generating", 85),
                    ("Cleaning", 95),
                    ("completed", 100),
                ]:
                    if keyword.lower() in text.lower():
                        self.progress_bar.setValue(value)
                        self.progress_bar.setFormat(keyword.capitalize() + "...")
                        QApplication.processEvents()
                        break

            class ProgressWriter:
                def write(self, text):
                    if text.strip():
                        update_progress(text)
                def flush(self):
                    pass

            old_stdout = sys.stdout
            sys.stdout = ProgressWriter()

            try:
                params = self.get_parameters()
                converter.main(
                    input_path=self.image_path,
                    tilemap_path=None,
                    start_index=params['start_index'],
                    num_palettes=params['num_palettes'],
                    transparent_color=params['transparent_color'],
                    extra_transparent_tiles=params['extra_transparent_tiles'],
                    tile_width=params['tile_width'],
                    origin=params['origin'],
                    end=None,
                    output_size=params['output_size'],
                    keep_temp=params['keep_temp'],
                    keep_transparent=params['keep_transparent']
                )
            finally:
                sys.stdout = old_stdout

            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Conversion completed.")
            QApplication.processEvents()
            import time
            time.sleep(0.5)
            self.accept()

        except Exception as e:
            self.progress_bar.setFormat("Error")
            QApplication.processEvents()
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")
            self.convert_btn.setEnabled(True)

    def get_parameters(self):
        """Return conversion parameters as dict."""
        output_text = self.output_combo.currentText()
        if output_text == "Custom":
            w = self.custom_width.value()
            h = self.custom_height.value()
            output_size = f"{w}t,{h}t"
        elif output_text == "Original":
            w = self.img_width_tiles
            h = self.img_height_tiles
            output_size = f"{w}t,{h}t"
        else:
            output_size = output_text.split()[0].lower()

        # Get selected palette indices
        selected_palettes = [i for i, cb in enumerate(self.palette_checks) if cb.isChecked()]
        # Ensure at least one
        if not selected_palettes:
            selected_palettes = [0]

        return {
            'num_palettes': len(selected_palettes),  # Number of palettes to use
            'start_index': min(selected_palettes),   # Not used in logic, but pass min index
            'selected_palettes': selected_palettes,  # To be used in converter logic
            'transparent_color': tuple(map(int, self.transparent_color.text().split(','))),
            'extra_transparent_tiles': self.extra_transparent.value(),
            'tile_width': self.tileset_width.value() if self.tileset_width.value() > 0 else None,
            'origin': self.origin.text(),
            'output_size': output_size,
            'keep_temp': self.keep_temp.isChecked(),
            'keep_transparent': self.keep_transparent.isChecked()
        }