# ui/main_window.py
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
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QFont,
    QPixmap,
    QPainter,
    QColor,
    QBrush,
    QPen,
    QImage,
)
from PIL import Image as PilImage
import os


class GBABackgroundStudio(QMainWindow):
    def __init__(self, language="english"):
        super().__init__()
        from utils.translator import Translator
        self.translator = Translator(lang_dir="lang", default_lang=language)
        self.setWindowTitle(self.translator.tr("app_name"))
        self.resize(1200, 800)

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
        self.tiles_view = QGraphicsView()
        self.tiles_scene = QGraphicsScene()
        self.tiles_view.setScene(self.tiles_scene)
        self.tiles_view.setRenderHint(QPainter.Antialiasing, False)
        self.tiles_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.tiles_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.tiles_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.tiles_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tile_palette_splitter.addWidget(self.tiles_view)

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
        for i in range(256):
            row = i // 16
            col = i % 16
            level = int((i / 255) * 248) & 0b11111000
            color = QColor(level, level, level)
            brush = QBrush(color)
            rect = self.palette_scene.addRect(col * tile_size, row * tile_size, tile_size, tile_size, QPen(Qt.gray), brush)
            rect.setData(1, (level, level, level))
            rect.mousePressEvent = lambda e, r=level, g=level, b=level: self.show_color_rgb(r, g, b)

    def show_color_rgb(self, r, g, b):
        self.status_bar.showMessage(f"RGB: ({r}, {g}, {b})")

    def pil_to_qimage(self, pil_img):
        if pil_img.mode == "RGBA":
            data = pil_img.tobytes("raw", "RGBA")
            return QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
        else:
            rgb_img = pil_img.convert("RGB")
            data = rgb_img.tobytes("raw", "RGB")
            return QImage(data, rgb_img.size[0], rgb_img.size[1], QImage.Format_RGB888)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(self.translator.tr("menu_file"))
        action_open = file_menu.addAction(self.translator.tr("action_open"))
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.open_image)

        action_convert = file_menu.addAction("Convert Image to Tilemap")
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

        from ui.conversion_dialog import ConversionDialog
        dialog = ConversionDialog(image_path=input_path, parent=self)
        if dialog.exec() == QDialog.Accepted:
            params = dialog.get_parameters()
            try:
                import core.converter as converter
                converter.LANGUAGE = "eng"

                converter.main(
                    input_path=input_path,
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

                tiles_path = "output/tiles.png"
                preview_path = "output/preview.png"
                palette_path = "output/palette.pal"

                if os.path.exists(tiles_path):
                    tiles_img = PilImage.open(tiles_path)
                    self.display_tileset(tiles_img)

                if os.path.exists(preview_path):
                    preview_img = PilImage.open(preview_path)
                    preview_qimg = self.pil_to_qimage(preview_img)
                    preview_pixmap = QPixmap.fromImage(preview_qimg)
                    self.preview_scene.clear()
                    self.preview_scene.addPixmap(preview_pixmap)
                    self.preview_scene.setSceneRect(preview_pixmap.rect())

                if os.path.exists(palette_path):
                    palette_colors = self.load_gba_palette(palette_path)
                    self.display_palette_colors(palette_colors)
                else:
                    self.display_palette_colors([(0, 0, 0)] * 256)

                self.status_bar.showMessage("✓ Conversion completed: output/")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")

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
        self.tiles_scene.clear()
        tile_size_px = 16
        w, h = pil_img.size
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                box = (x, y, x+8, y+8)
                tile = pil_img.crop(box)
                qimg = self.pil_to_qimage(tile)
                pix = QPixmap.fromImage(qimg).scaled(tile_size_px, tile_size_px, Qt.IgnoreAspectRatio, Qt.FastTransformation)
                self.tiles_scene.addPixmap(pix).setPos(x * 2, y * 2)
        self.tiles_scene.setSceneRect(0, 0, w * 2, h * 2)

    def show_about(self):
        QMessageBox.about(
            self,
            self.translator.tr("about_title"),
            self.translator.tr("about_text")
        )