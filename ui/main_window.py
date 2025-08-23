# ui/main_window.py
import os
import math
import colorsys
from PIL import Image as PilImage
from PySide6.QtCore import Qt
from utils.translator import Translator
from ui.conversion_dialog import ConversionDialog
from core.image_utils import pil_to_qimage
from PySide6.QtGui import (
    QFont,
    QPixmap,
    QPainter,
    QColor,
    QBrush,
    QPen,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QMenuBar,
    QStatusBar,
    QFileDialog,
    QMessageBox,
    QGraphicsView,
    QGraphicsScene,
    QSizePolicy,
    QTabWidget,
    QSplitter,
    QDialog,
    QPushButton,
    QProgressBar,
)


class GBABackgroundStudio(QMainWindow):
    def __init__(self, language="english"):
        super().__init__()
        self.translator = Translator(lang_dir="lang", default_lang=language)
        self.setWindowTitle(self.translator.tr("app_name"))
        self.resize(1200, 800)

        # === CONFIGURACIÓN DE TILES ===
        self.tile_size = 8
        
        # === SISTEMA DE SELECCIÓN DE TILES ===
        self.selected_tile_id = None
        self.selected_tile_image = None
        self.tileset_columns = 0
        self.tileset_rows = 0
        self.tileset_tiles = []
        self.tileset_ids = {}
        
        # === SISTEMA DE TILEMAP ===  
        self.tilemap_ids = []
        self.tilemap_tiles = []
        self.tilemap_columns = 0
        self.tilemap_rows = 0
        self.tilemap_scene = None
        
        # === VARIABLES TEMPORALES ===
        self.current_tileset = None

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Main splitter: left (editor) / right (tabs)
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)

        # === LEFT PANEL: Editor (50/50 split) ===
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setChildrenCollapsible(False)
        left_splitter.setHandleWidth(6)

        # --- TOP: Tile Editor ---
        top_panel = QWidget()
        top_layout = QVBoxLayout()
        top_panel.setLayout(top_layout)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        tile_editor_header = self.create_header(self.translator.tr("header_tile_editor"))
        top_layout.addWidget(tile_editor_header)

        tile_palette_splitter = QSplitter(Qt.Horizontal)
        tile_palette_splitter.setChildrenCollapsible(False)
        tile_palette_splitter.setHandleWidth(6)
        tile_palette_splitter.setOpaqueResize(True)

        # Input Tiles Area
        self.tileset_view = QGraphicsView()
        self.tileset_scene = QGraphicsScene()
        self.tileset_view.setScene(self.tileset_scene)
        self.tileset_view.setRenderHint(QPainter.Antialiasing, False)
        self.tileset_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.tileset_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.tileset_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.tileset_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tile_palette_splitter.addWidget(self.tileset_view)

        # Palette Editor Area
        self.palette_view = QGraphicsView()
        self.palette_scene = QGraphicsScene()
        self.palette_view.setScene(self.palette_scene)
        self.palette_view.setRenderHint(QPainter.Antialiasing, False)
        self.palette_view.setStyleSheet("QGraphicsView { background: #f9f9f9; border: 1px solid #ccc; }")
        self.palette_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.palette_view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.palette_view.setFixedWidth(136)
        tile_palette_splitter.addWidget(self.palette_view)
        self.init_default_palette()

        tile_palette_splitter.setSizes([800, 136])
        top_layout.addWidget(tile_palette_splitter)
        left_splitter.addWidget(top_panel)

        # --- BOTTOM: Preview ---
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_panel.setLayout(bottom_layout)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(4)

        preview_header = self.create_header(self.translator.tr("header_preview"))
        bottom_layout.addWidget(preview_header)

        self.preview_view = QGraphicsView()
        self.preview_scene = QGraphicsScene()
        self.preview_view.setScene(self.preview_scene)
        self.preview_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.preview_view.setStyleSheet("QGraphicsView { background: #e0e0e0; border: 1px solid #ccc; }")
        self.preview_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.preview_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bottom_layout.addWidget(self.preview_view)

        left_splitter.addWidget(bottom_panel)
        left_splitter.setSizes([400, 400])
        main_splitter.addWidget(left_splitter)

        # === RIGHT PANEL: Edit Tabs ===
        right_panel = QTabWidget()
        right_panel.setTabPosition(QTabWidget.North)

        edit_tiles_tab = QWidget()
        edit_tiles_layout = QVBoxLayout()
        edit_tiles_label = QLabel(self.translator.tr("tab_edit_tiles"))
        edit_tiles_label.setAlignment(Qt.AlignCenter)
        edit_tiles_layout.addWidget(edit_tiles_label)
        edit_tiles_tab.setLayout(edit_tiles_layout)

        edit_palettes_tab = QWidget()
        edit_palettes_layout = QVBoxLayout()
        edit_palettes_label = QLabel(self.translator.tr("tab_edit_palettes"))
        edit_palettes_label.setAlignment(Qt.AlignCenter)
        edit_palettes_layout.addWidget(edit_palettes_label)
        edit_palettes_tab.setLayout(edit_palettes_layout)

        right_panel.addTab(edit_tiles_tab, self.translator.tr("tab_edit_tiles"))
        right_panel.addTab(edit_palettes_tab, self.translator.tr("tab_edit_palettes"))

        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([800, 400])

        layout.addWidget(main_splitter)

        # Menu bar
        self.create_menu_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.translator.tr("status_ready"))

    def create_header(self, text):
        header = QLabel(text)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        return header

    def init_default_palette(self):
        self.palette_scene.clear()
        tile_size = 8
        palette_path = "assets/default_rainbow.pal"
        
        colors = self.generate_grayscale_palette()
        
        try:
            if os.path.exists(palette_path):
                colors = self.load_gba_palette(palette_path)
            else:
                print("ℹ️ Archivo de paleta no encontrado, usando escala de grises")
                
        except Exception as e:
            print(f"❌ Error cargando paleta: {e}, usando escala de grises")
        
        for i, (r, g, b) in enumerate(colors):
            if i >= 256:
                break
                
            row = i // 16
            col = i % 16
            color = QColor(r, g, b)
            brush = QBrush(color)
            
            rect = self.palette_scene.addRect(
                col * tile_size, 
                row * tile_size, 
                tile_size, 
                tile_size, 
                QPen(Qt.gray), 
                brush
            )
            rect.setData(1, (r, g, b))
            rect.mousePressEvent = lambda e, r=r, g=g, b=b: self.show_color_rgb(r, g, b)

    def generate_grayscale_palette(self):
        colors = []
        for i in range(256):
            level = int((i / 255) * 248) & 0b11111000
            colors.append((level, level, level))
        return colors

    def show_color_rgb(self, r, g, b):
        self.status_bar.showMessage(f"RGB: ({r}, {g}, {b})")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(self.translator.tr("menu_file"))
        action_open = file_menu.addAction(self.translator.tr("action_open"))
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.open_image)

        action_convert = file_menu.addAction("Convert Image to Tilemap")
        action_convert.setShortcut("Ctrl+I")
        action_convert.triggered.connect(self.convert_image)

        file_menu.addSeparator()
        action_exit = file_menu.addAction(self.translator.tr("action_exit"))
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.close)

        edit_menu = menu_bar.addMenu(self.translator.tr("menu_edit"))
        action_undo = edit_menu.addAction(self.translator.tr("action_undo"))
        action_undo.setShortcut("Ctrl+Z")
        action_undo.setEnabled(False)
        action_redo = edit_menu.addAction(self.translator.tr("action_redo"))
        action_redo.setShortcut("Ctrl+Y")
        action_redo.setEnabled(False)

        tools_menu = menu_bar.addMenu(self.translator.tr("menu_tools"))
        action_preview = tools_menu.addAction(self.translator.tr("action_preview"))
        action_preview.setEnabled(False)
        action_export = tools_menu.addAction(self.translator.tr("action_export"))
        action_export.setEnabled(False)

        help_menu = menu_bar.addMenu(self.translator.tr("menu_help"))
        action_about = help_menu.addAction(self.translator.tr("action_about"))
        action_about.triggered.connect(self.show_about)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.tr("action_open"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
        )
        if not file_path:
            return
        self.status_bar.showMessage(self.translator.tr("status_image_loaded", path=os.path.basename(file_path)))

    def convert_image(self):
        input_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select image to convert",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)"
        )
        if not input_path:
            return

        dialog = ConversionDialog(image_path=input_path, parent=self)
        dialog.exec()

    def load_gba_palette(self, pal_path):
        if not os.path.exists(pal_path):
            print(f"Palette file not found: {pal_path}")
            return [(0, 0, 0)] * 256
        try:
            with open(pal_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
            count = int(lines[0])
            colors = []
            for line in lines[1:1 + count]:
                r, g, b = map(int, line.split())
                colors.append((r, g, b))
            while len(colors) < 256:
                colors.append((0, 0, 0))
            return colors[:256]
        except Exception as e:
            print(f"Error reading palette: {e}")
            return [(0, 0, 0)] * 256

    def display_palette_colors(self, colors):
        self.palette_scene.clear()
        tile_size = 8
        for i, (r, g, b) in enumerate(colors):
            row = i // 16
            col = i % 16
            color = QColor(r, g, b)
            brush = QBrush(color)
            rect = self.palette_scene.addRect(
                col * tile_size,
                row * tile_size,
                tile_size,
                tile_size,
                QPen(Qt.gray),
                brush
            )
            rect.setData(1, (r, g, b))
            rect.mousePressEvent = lambda event, r=r, g=g, b=b: self.show_color_rgb(r, g, b)

    def display_tileset(self, pil_img):
        self.tileset_scene.clear()
        tile_size_px = 16
        w, h = pil_img.size
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                box = (x, y, x+8, y+8)
                tile = pil_img.crop(box)
                qimg = pil_to_qimage(tile)
                pix = QPixmap.fromImage(qimg).scaled(tile_size_px, tile_size_px, Qt.IgnoreAspectRatio, Qt.FastTransformation)
                self.tileset_scene.addPixmap(pix).setPos(x * 2, y * 2)
        self.tileset_scene.setSceneRect(0, 0, w * 2, h * 2)

    def show_about(self):
        QMessageBox.about(
            self,
            self.translator.tr("about_title"),
            self.translator.tr("about_text")
        )
        
    def load_conversion_results(self):
        """Actualiza la interfaz con los resultados de conversión."""
        tiles_path = "output/tiles.png"
        preview_path = "temp/preview/preview.png"
        palette_path = "temp/preview/palette.pal"

        # === 1. CARGAR TILESET (GUARDAR TILES E IDs) ===
        if os.path.exists(tiles_path):
            tiles_img = PilImage.open(tiles_path)
            tiles_qimg = pil_to_qimage(tiles_img)
            tiles_pixmap = QPixmap.fromImage(tiles_qimg)
            
            self.tileset_scene.clear()
            self.tileset_scene.addPixmap(tiles_pixmap)
            self.tileset_scene.setSceneRect(tiles_pixmap.rect())
            
            zoom_factor = 2.0
            self.tileset_view.resetTransform()
            self.tileset_view.scale(zoom_factor, zoom_factor)
            
            # Centrar la vista después del zoom
            self.tileset_view.centerOn(self.tileset_scene.items()[0])

            # PRE-CALCULAR todos los tiles e IDs
            self.tileset_tiles = []  # Lista de imágenes de tiles
            self.tileset_ids = {}    # Diccionario ID -> tile image
            
            # USAR self.tile_size definido en el constructor
            tile_width = self.tile_size
            tile_height = self.tile_size
            columns = tiles_img.width // tile_width
            rows = tiles_img.height // tile_height
            
            # Guardar dimensiones para selección futura
            self.tileset_columns = columns
            self.tileset_rows = rows
            
            for y in range(rows):
                for x in range(columns):
                    # Recortar tile individual
                    left = x * tile_width
                    upper = y * tile_height
                    right = left + tile_width
                    lower = upper + tile_height
                    
                    tile_img = tiles_img.crop((left, upper, right, lower))
                    tile_id = y * columns + x
                    
                    self.tileset_tiles.append(tile_img)
                    self.tileset_ids[tile_id] = tile_img  # ID -> imagen

        # === 2. CARGAR PREVIEW ===
        if os.path.exists(preview_path):
            preview_img = PilImage.open(preview_path)
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            self.preview_scene.clear()
            self.preview_scene.addPixmap(preview_pixmap)
            self.preview_scene.setSceneRect(preview_pixmap.rect())

        # === 3. CARGAR PALETA UNIFICADA ===
        if os.path.exists(palette_path):
            palette_colors = [(0, 0, 0)] * 256
            try:
                with open(palette_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f 
                            if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
                
                if lines:
                    color_count = int(lines[0])
                    for i in range(1, min(1 + color_count, 257)):
                        r, g, b = map(int, lines[i].split())
                        palette_colors[i - 1] = (r, g, b)

            except Exception as e:
                print(f"Error loading palette: {e}")


        self.display_palette_colors(palette_colors)

        self.status_bar.showMessage("✓ Conversion completed")
