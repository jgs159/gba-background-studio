# ui/dialogs/conversion_dialog_config.py
class ConversionDialogConfig:
    def load_conversion_settings(self):
        if not (self.parent() and hasattr(self.parent(), 'config_manager') and 
                self.parent().save_conversion_params):
            return
        
        try:
            config = self.parent().config_manager
            
            bpp_index = int(config.get('CONVERSION', 'bpp', '0'))
            if 0 <= bpp_index <= 1:
                self.bpp_combo.setCurrentIndex(bpp_index)
            
            if bpp_index == 0:
                use_palettes = config.getboolean('CONVERSION', 'use_palettes', True)
                if use_palettes:
                    self.use_palettes_radio.setChecked(True)
                else:
                    self.use_tilemap_radio.setChecked(True)
                
                palettes_str = config.get('CONVERSION', 'selected_palettes', '0')
                selected_palettes = list(map(int, palettes_str.split(',')))
                for i, cb in enumerate(self.palette_checks):
                    cb.setChecked(i in selected_palettes)
            
            self.transparent_color.setText(config.get('CONVERSION', 'transparent_color', '0,0,0'))
            self.extra_transparent.setValue(int(config.get('CONVERSION', 'extra_transparent', '0')))
            self.tileset_width.setValue(int(config.get('CONVERSION', 'tileset_width', '0')))
            self.origin.setText(config.get('CONVERSION', 'origin', '0,0'))
            
            output_size = config.get('CONVERSION', 'output_size', 'Original')
            index = self.output_combo.findText(output_size)
            if index >= 0:
                self.output_combo.setCurrentIndex(index)
                self.on_output_size_changed()
            
            self.custom_width.setValue(int(config.get('CONVERSION', 'custom_width', '32')))
            self.custom_height.setValue(int(config.get('CONVERSION', 'custom_height', '20')))
            
            self.start_index.setValue(int(config.get('CONVERSION', 'start_index', '0')))
            self.palette_size.setValue(int(config.get('CONVERSION', 'palette_size', '1')))
            
            if hasattr(self, 'palette_size'):
                self.palette_size.update()
            
        except Exception as e:
            print(f"Error loading conversion settings: {e}")

    def save_conversion_settings(self, params):
        if not (self.parent() and hasattr(self.parent(), 'config_manager') and 
                self.parent().save_conversion_params):
            return
        
        try:
            config = self.parent().config_manager
            
            config.set('CONVERSION', 'bpp', str(self.bpp_combo.currentIndex()))
            
            if self.bpp_combo.currentIndex() == 0:
                config.set('CONVERSION', 'use_palettes', str(self.use_palettes_radio.isChecked()))
                
                selected_palettes = [i for i, cb in enumerate(self.palette_checks) if cb.isChecked()]
                config.set('CONVERSION', 'selected_palettes', ','.join(map(str, selected_palettes)))
            
            config.set('CONVERSION', 'transparent_color', self.transparent_color.text())
            config.set('CONVERSION', 'extra_transparent', str(self.extra_transparent.value()))
            config.set('CONVERSION', 'tileset_width', str(self.tileset_width.value()))
            config.set('CONVERSION', 'origin', self.origin.text())
            
            config.set('CONVERSION', 'output_size', self.output_combo.currentText())
            config.set('CONVERSION', 'custom_width', str(self.custom_width.value()))
            config.set('CONVERSION', 'custom_height', str(self.custom_height.value()))
            
            config.set('CONVERSION', 'start_index', str(self.start_index.value()))
            config.set('CONVERSION', 'palette_size', str(self.palette_size.value()))
            
        except Exception as e:
            print(f"Error saving conversion settings: {e}")
