# ui/dialogs/conversion_dialog_logic.py
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap
import os
import sys
import time
from contextlib import redirect_stdout
from core.image_utils import pil_to_qimage
from core.main import main as converter_main
from .conversion_params import get_conversion_parameters
from .show_success_dialog import show_success_dialog
from .gba_compatibility_dialog import GBACompatibilityDialog
from PIL import Image as PilImage

class ConversionDialogLogic:
    def on_mode_changed(self):
        is_rot = self.mode_combo.currentIndex() == 1
        if is_rot:
            self.bpp_combo.setCurrentIndex(1)
        self.bpp_combo.setEnabled(not is_rot)
        self.PRESETS = self.PRESETS_ROT if is_rot else self.PRESETS_TEXT
        self.output_combo.blockSignals(True)
        self.output_combo.clear()
        for label in self.PRESETS.keys():
            self.output_combo.addItem(label)
        self.output_combo.blockSignals(False)
        self.output_combo.setCurrentIndex(0)
        self.on_output_size_changed()
        self.on_bpp_changed()

    def _handle_start_index_change(self, value):
        self.palette_size.update()
        QTimer.singleShot(10, self.update_8bpp_size)

    def on_palette_tilemap_toggled(self):
        use_palettes = self.use_palettes_radio.isChecked()
        self.palettes_widget_container.setVisible(use_palettes)
        self.tilemap_file_container.setVisible(not use_palettes)

    def browse_tilemap_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Tilemap File", 
            "", 
            "Binary Files (*.bin);;All Files (*)"
        )
        
        if file_path:
            self.tilemap_path_edit.setText(file_path)

    def on_bpp_changed(self):
        is_8bpp = self.bpp_combo.currentIndex() == 1
        self.palettes_container.setVisible(not is_8bpp)
        
        for widget in self.bpp8_widgets:
            widget.setVisible(is_8bpp)
        for label in self.bpp8_labels:
            label.setVisible(is_8bpp)
        
        if is_8bpp:
            self.use_palettes_radio.setEnabled(False)
            self.use_tilemap_radio.setEnabled(False)
            self.palettes_widget_container.setVisible(False)
            self.tilemap_file_container.setVisible(False)
        else:
            self.use_palettes_radio.setEnabled(True)
            self.use_tilemap_radio.setEnabled(True)
            use_palettes = self.use_palettes_radio.isChecked()
            self.palettes_widget_container.setVisible(use_palettes)
            self.tilemap_file_container.setVisible(not use_palettes)
        
        if hasattr(self, 'palette_size'):
            self.palette_size.update()

    def update_8bpp_size(self):
        self.convert_btn.setEnabled(True)

    def on_palette_toggled(self):
        if not any(cb.isChecked() for cb in self.palette_checks):
            sender = self.sender()
            sender.setChecked(True)

    def on_eyedropper_toggled(self, active):
        from PySide6.QtCore import Qt
        if active:
            self.input_view.setCursor(Qt.CrossCursor)
            self.input_view.mousePressEvent = self._eyedropper_pick
        else:
            self.input_view.setCursor(Qt.ArrowCursor)
            self.input_view.mousePressEvent = self._default_input_press

    def _eyedropper_pick(self, event):
        from PySide6.QtCore import Qt
        pos = self.input_view.mapToScene(event.pos())
        items = self.input_scene.items(pos)
        for item in items:
            from PySide6.QtWidgets import QGraphicsPixmapItem
            if isinstance(item, QGraphicsPixmapItem):
                px = item.pixmap()
                ix, iy = int(pos.x() - item.x()), int(pos.y() - item.y())
                if 0 <= ix < px.width() and 0 <= iy < px.height():
                    color = px.toImage().pixelColor(ix, iy)
                    self.transparent_color.setText(f"{color.red()},{color.green()},{color.blue()}")
                break
        self.eyedropper_btn.setChecked(False)

    def _default_input_press(self, event):
        from PySide6.QtWidgets import QGraphicsView
        QGraphicsView.mousePressEvent(self.input_view, event)

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
            self._default_input_press = self.input_view.mousePressEvent
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
        if w_px > 1024 or h_px > 2048:
            self.output_info.setText(f"Output Size: {w_px}x{h_px} px ⚠️ Exceeds 1024x2048")
            self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #cc0000; padding: 4px; }")
        else:
            self.output_info.setText(f"Output Size: {w_px}x{h_px} px")
            self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #0066cc; padding: 4px; }")
        self.output_width_tiles = w_tiles
        self.output_height_tiles = h_tiles

    def on_convert(self):
        if (self.parent() and hasattr(self.parent(), 'grid_manager') and 
            self.parent().grid_manager.is_grid_visible()):
            self.grid_was_visible = True
            self.parent().grid_manager.set_grid_visible(False)
        else:
            self.grid_was_visible = False

        tc_text = self.transparent_color.text().strip()
        try:
            tc = tuple(map(int, tc_text.split(','))) if tc_text else (0, 0, 0)
            if len(tc) != 3 or not all(0 <= c <= 255 for c in tc):
                raise ValueError
        except:
            QMessageBox.critical(self, "Error", "Invalid transparent color. Use 'R,G,B' with values 0-255.")
            return

        origin_text = self.origin.text().strip()
        if origin_text and origin_text != "0,0":
            try:
                parts = origin_text.split(",")
                if len(parts) != 2:
                    raise ValueError
                for p in parts:
                    p = p.strip()
                    if p.endswith('t'):
                        int(p[:-1])
                    else:
                        int(p)
            except:
                QMessageBox.critical(self, "Error", "Invalid origin. Use 'x,y' or 'xt,yt' (e.g. '10,20' or '1t,2t').")
                return

        tilemap_path = None
        palettes_to_use = []
        
        is_rot = self.mode_combo.currentIndex() == 1
        is_8bpp = self.bpp_combo.currentIndex() == 1

        if not is_8bpp and not is_rot:
            if self.use_tilemap_radio.isChecked():
                tilemap_path = self.tilemap_path_edit.text().strip()
                if not tilemap_path:
                    QMessageBox.warning(self, "Warning", "Please select a tilemap file")
                    return
                if not os.path.exists(tilemap_path):
                    QMessageBox.warning(self, "Warning", f"The selected tilemap file does not exist:\n{tilemap_path}")
                    return
            else:
                palettes_to_use = [i for i, cb in enumerate(self.palette_checks) if cb.isChecked()]

        if not is_rot and self.output_combo.currentText() == "Custom":
            w = self.custom_width.value()
            h = self.custom_height.value()
            if w > 32:
                adjusted_w = ((w + 31) // 32) * 32
                adjusted_h = ((h + 31) // 32) * 32
                if adjusted_w != w or adjusted_h != h:
                    dlg = GBACompatibilityDialog(w, h, adjusted_w, adjusted_h, self)
                    if dlg.exec():
                        self.custom_width.setValue(adjusted_w)
                        self.custom_height.setValue(adjusted_h)
                        self.update_output_info()
                    else:
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
                keep_temp = False
                keep_transparent = False
                save_preview = False

                if self.parent():
                    keep_temp = getattr(self.parent(), 'keep_temp_files', False)
                    keep_transparent = getattr(self.parent(), 'keep_transparent_color', False)
                    save_preview = getattr(self.parent(), 'save_preview_files', False)

                params = get_conversion_parameters(
                    self.image_path,
                    self.output_combo.currentText(),
                    self.bpp_combo.currentIndex() == 1,
                    palettes_to_use,
                    self.transparent_color.text(),
                    self.extra_transparent.value(),
                    self.tileset_width.value(),
                    self.origin.text(),
                    self.img_width_tiles,
                    self.img_height_tiles,
                    self.custom_width.value(),
                    self.custom_height.value(),
                    self.start_index.value(),
                    self.palette_size.value(),
                    save_preview,
                    keep_temp,
                    keep_transparent,
                    tilemap_path,
                    is_rot
                )
                
                converter_main(**params)
            finally:
                sys.stdout = old_stdout

            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Conversion completed.")
            QApplication.processEvents()

            self.save_conversion_settings(params)
            if self.parent() and hasattr(self.parent(), 'load_conversion_results'):
                self.parent().load_conversion_results()
            
            if (self.parent() and hasattr(self.parent(), 'grid_manager') and 
                self.grid_was_visible):
                self.parent().grid_manager.set_grid_visible(True)
            
            if self.parent() and self.parent().show_success_dialog:
                show_success_dialog(self)
            time.sleep(0.3)
            self.accept()
        except (Exception, SystemExit) as e:
            if (self.parent() and hasattr(self.parent(), 'grid_manager') and 
                self.grid_was_visible):
                self.parent().grid_manager.set_grid_visible(True)
                
            self.progress_bar.setFormat("Error")
            QApplication.processEvents()
            msg = str(e) if str(e) else "Process exited unexpectedly."
            QMessageBox.critical(self, "Error", f"Conversion failed: {msg}")
            self.convert_btn.setEnabled(True)
