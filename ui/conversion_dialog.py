# ui/conversion_dialog.py
import io
import os
import sys
import time
import subprocess
from PIL import Image as PilImage
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QFont
from core.image_utils import pil_to_qimage
from core.main import main as converter_main
from contextlib import redirect_stdout
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
    QListWidget,
    QSplitter,
    QApplication,
)


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

    class AutoSpinBox(QSpinBox):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._is_auto = True
            self.setRange(1, 256)
            self.setSpecialValueText("Auto (256 - start)")
            super().setValue(1)

        def setValue(self, value):
            if value == 0:
                super().setValue(1)
                self._is_auto = True
            else:
                super().setValue(value)
                self._is_auto = False

        def value(self):
            if self._is_auto:
                return 0
            return super().value()

        def textFromValue(self, value):
            if self._is_auto:
                return "Auto (256 - start)"
            return super().textFromValue(value)

        def valueFromText(self, text):
            if text.strip() == "Auto (256 - start)":
                self._is_auto = True
                return 1
            self._is_auto = False
            return super().valueFromText(text)

        def stepEnabled(self):
            if self._is_auto:
                return QSpinBox.StepNone
            return super().stepEnabled()

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
        layout = QVBoxLayout(self)

        # Main splitter: left (image) 70% / right (params) 30%
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

        # --- BPP Selector ---
        self.bpp_combo = QComboBox()
        self.bpp_combo.addItems(["4bpp (16 colors per palette)", "8bpp (256 colors)"])
        self.bpp_combo.setCurrentIndex(0)
        self.bpp_combo.currentIndexChanged.connect(self.on_bpp_changed)
        form_layout.addRow("Bits per pixel:", self.bpp_combo)

        # --- Selector de paletas (4bpp) ---
        self.palettes_container = QWidget()
        palettes_main_layout = QVBoxLayout()
        palettes_main_layout.setContentsMargins(0, 0, 0, 0)
        palettes_main_layout.setSpacing(2)
        self.palettes_container.setLayout(palettes_main_layout)

        self.palettes_label = QLabel("Palettes (4bpp):")
        palettes_main_layout.addWidget(self.palettes_label)

        self.palettes_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 1, 0, 1)
        grid_layout.setSpacing(1)
        self.palettes_widget.setLayout(grid_layout)

        self.palette_checks = []
        for i in range(16):
            cb = QCheckBox("")
            cb.setFixedSize(16, 16)
            cb.setChecked(i == 0)
            cb.toggled.connect(self.on_palette_toggled)
            self.palette_checks.append(cb)
            grid_layout.addWidget(cb, 0, i)

            label = QLabel(hex(i)[2:].upper())
            label.setFixedSize(16, 12)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("QLabel { font-size: 10px; font-weight: bold; color: #555; margin: 0; padding: 0; }")
            grid_layout.addWidget(label, 1, i)

        self.palettes_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.palettes_widget.setFixedWidth(300)
        palettes_main_layout.addWidget(self.palettes_widget)

        form_layout.addRow(self.palettes_container)

        # --- 8bpp Parameters (start-index, palette-size) ---
        self.bpp8_widget = QWidget()
        bpp8_layout = QFormLayout()

        self.start_index = QSpinBox()
        self.start_index.setRange(0, 255)
        self.start_index.setValue(0)
        self.start_index.valueChanged.connect(self.on_8bpp_param_changed)
        bpp8_layout.addRow("Start Index:", self.start_index)

        self.palette_size = self.AutoSpinBox()
        self.palette_size.valueChanged.connect(self.on_8bpp_param_changed)
        bpp8_layout.addRow("Palette Size:", self.palette_size)

        self.size_warning = QLabel("")
        self.size_warning.setStyleSheet("QLabel { color: #cc0000; font-weight: bold; }")
        self.size_warning.setVisible(False)
        bpp8_layout.addRow("", self.size_warning)

        self.bpp8_widget.setLayout(bpp8_layout)
        form_layout.addRow(self.bpp8_widget)

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
        self.output_info = QLabel("Output Size: 256x160 px")
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

        # Set sizes: 770 / 330
        main_splitter.setSizes([770, 330])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

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
        self.on_bpp_changed()

    def on_bpp_changed(self):
        is_8bpp = self.bpp_combo.currentIndex() == 1
        self.palettes_container.setVisible(not is_8bpp)
        self.bpp8_widget.setVisible(is_8bpp)
        self.update_8bpp_size()

    def on_8bpp_param_changed(self):
        self.update_8bpp_size()

    def update_8bpp_size(self):
        start = self.start_index.value()
        raw_size = self.palette_size.value()
        auto_size = 256 - start
        current_size = auto_size if raw_size == 0 else raw_size
        total = start + current_size
        if total > 256:
            self.size_warning.setText("❌ Overflow: max 256")
            self.size_warning.setVisible(True)
            self.convert_btn.setEnabled(False)
        else:
            self.size_warning.setVisible(False)
            self.convert_btn.setEnabled(True)

    def on_palette_toggled(self):
        if not any(cb.isChecked() for cb in self.palette_checks):
            sender = self.sender()
            sender.setChecked(True)

    def load_input_image(self):
        try:
            pil_img = PilImage.open(self.image_path).convert("RGBA")
            qimg = pil_to_qimage(pil_img)
            pix = QPixmap.fromImage(qimg)
            self.input_scene.clear()
            item = self.input_scene.addPixmap(pix)
            self.input_scene.setSceneRect(pix.rect())
            self.input_view.resetTransform()
            self.input_view.scale(1.0, 1.0)
            self.input_view.centerOn(item)
        except Exception as e:
            print(f"Error loading input image: {e}")

    def on_output_size_changed(self):
        text = self.output_combo.currentText()
        if text == "Custom":
            self.custom_stack.setCurrentIndex(1)
            self.update_output_info()
        elif text == "Original":
            self.custom_stack.setCurrentIndex(0)
            w_px, h_px = self.img_width_tiles * 8, self.img_height_tiles * 8
            self.output_width_tiles = self.img_width_tiles
            self.output_height_tiles = self.img_height_tiles
            self.output_info.setText(f"Output Size: {w_px}x{h_px} px")
        else:
            self.custom_stack.setCurrentIndex(0)
            w_tiles, h_tiles = self.PRESETS[text]
            self.output_width_tiles = w_tiles
            self.output_height_tiles = h_tiles
            w_px, h_px = w_tiles * 8, h_tiles * 8
            self.output_info.setText(f"Output Size: {w_px}x{h_px} px")

    def update_output_info(self):
        w_tiles = self.custom_width.value()
        h_tiles = self.custom_height.value()
        w_px, h_px = w_tiles * 8, h_tiles * 8
        if w_px > 512 or h_px > 512:
            self.output_info.setText(f"Output Size: {w_px}x{h_px} px ⚠️ Exceeds 512px")
            self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #cc0000; padding: 4px; }")
        else:
            self.output_info.setText(f"Output Size: {w_px}x{h_px} px")
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
            QMessageBox.critical(self, "Error", "Invalid transparent color. Use 'R,G,B' with values 0-255.")
            return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("Starting...")
        self.progress_bar.setValue(0)
        QApplication.processEvents()

        try:
            def update_progress(text):
                if "Splitting" in text:
                    self.progress_bar.setValue(10)
                    self.progress_bar.setFormat("Splitting...")
                elif "Quantizing" in text:
                    self.progress_bar.setValue(25)
                    self.progress_bar.setFormat("Quantizing...")
                elif "Applying" in text:
                    self.progress_bar.setValue(50)
                    self.progress_bar.setFormat("Applying GBA palette...")
                elif "Extracting" in text:
                    self.progress_bar.setValue(65)
                    self.progress_bar.setFormat("Extracting palettes...")
                elif "Rebuilding" in text:
                    self.progress_bar.setValue(70)
                    self.progress_bar.setFormat("Rebuilding image...")
                elif "Generating" in text:
                    self.progress_bar.setValue(85)
                    self.progress_bar.setFormat("Generating assets...")
                elif "completed" in text and "Process" in text:
                    self.progress_bar.setValue(100)
                    self.progress_bar.setFormat("Conversion completed.")
                QApplication.processEvents()

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
                converter_main(**params)
            finally:
                sys.stdout = old_stdout

            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Conversion completed.")
            QApplication.processEvents()

            if self.parent() and hasattr(self.parent(), 'load_conversion_results'):
                self.parent().load_conversion_results()
            
            # === Show success window ===
            self.show_success_dialog()
            time.sleep(0.3)
            self.accept()
        except Exception as e:
            self.progress_bar.setFormat("Error")
            QApplication.processEvents()
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")
            self.convert_btn.setEnabled(True)

    def get_parameters(self):
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

        is_8bpp = self.bpp_combo.currentIndex() == 1

        if is_8bpp:
            start_index = self.start_index.value()
            raw_size = self.palette_size.value()

            if raw_size == 0:
                palette_size = 256 - start_index
            else:
                palette_size = raw_size

            if start_index + palette_size > 256:
                palette_size = 256 - start_index

            params = {
                'input_path': self.image_path,
                'tilemap_path': None,
                'selected_palettes': None,
                'transparent_color': tuple(map(int, self.transparent_color.text().split(','))),
                'extra_transparent_tiles': self.extra_transparent.value(),
                'tile_width': self.tileset_width.value() if self.tileset_width.value() > 0 else None,
                'origin': self.origin.text(),
                'end': None,
                'output_size': output_size,
                'keep_temp': self.keep_temp.isChecked(),
                'keep_transparent': self.keep_transparent.isChecked(),
                'bpp': 8,
                'start_index': start_index,
                'palette_size': palette_size
            }
        else:
            selected_palettes = [i for i, cb in enumerate(self.palette_checks) if cb.isChecked()]
            if not selected_palettes:
                selected_palettes = [0]
            params = {
                'input_path': self.image_path,
                'tilemap_path': None,
                'selected_palettes': selected_palettes,
                'transparent_color': tuple(map(int, self.transparent_color.text().split(','))),
                'extra_transparent_tiles': self.extra_transparent.value(),
                'tile_width': self.tileset_width.value() if self.tileset_width.value() > 0 else None,
                'origin': self.origin.text(),
                'end': None,
                'output_size': output_size,
                'keep_temp': self.keep_temp.isChecked(),
                'keep_transparent': self.keep_transparent.isChecked(),
                'bpp': 4,
                'start_index': 0,
                'palette_size': 256
            }

        return params

    def show_success_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("✅ Conversion Completed")
        dialog.resize(400, 300)

        layout = QVBoxLayout()

        # Title
        title = QLabel("The conversion was completed successfully!")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #006600;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Generated files:"))

        # File list
        list_widget = QListWidget()
        output_dir = "output"
        if os.path.exists(output_dir):
            for file in sorted(os.listdir(output_dir)):
                list_widget.addItem(file)
        else:
            list_widget.addItem("(No output folder)")
        layout.addWidget(list_widget)

        # Button: Open Folder
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        open_btn = QPushButton("📁 Open Output Folder")

        def open_folder():
            path = os.path.abspath(output_dir)
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])

        open_btn.clicked.connect(open_folder)
        btn_layout.addWidget(open_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()
