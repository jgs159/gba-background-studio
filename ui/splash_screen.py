# ui/splash_screen.py
from PySide6.QtWidgets import QSplashScreen, QProgressBar
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QTimer
import os

class GBASplashScreen(QSplashScreen):
    def __init__(self, translator=None):
        self.translator = translator
        
        splash_width = 500
        splash_height = 300
        
        pixmap = QPixmap(splash_width, splash_height)
        pixmap.fill(QColor(40, 40, 60))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 255, 255))
        
        splash_image = None
        splash_path = os.path.join("assets", "splash.png")
        if os.path.exists(splash_path):
            try:
                splash_image = QPixmap(splash_path)
                if not splash_image.isNull():
                    scaled_image = splash_image.scaled(400, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    x_pos = (splash_width - scaled_image.width()) // 2
                    y_pos = 20
                    painter.drawPixmap(x_pos, y_pos, scaled_image)
            except Exception as e:
                print(f"Error loading splash image: {e}")
        
        presents_text = self._tr_splash("splash_presents", "CompuMax Productions Present:")
        title_text = "GBA Background Studio"
        
        presents_font = painter.font()
        presents_font.setPointSize(12)
        presents_font.setItalic(True)
        painter.setFont(presents_font)
        
        painter.drawText(0, 175, splash_width, 30, Qt.AlignCenter, presents_text)
        
        title_font = painter.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_font.setItalic(False)
        painter.setFont(title_font)
        painter.drawText(0, 200, splash_width, 40, Qt.AlignCenter, title_text)
        
        painter.end()
        
        super().__init__(pixmap)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 250, 400, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2C2C4C;
                border-radius: 6px;
                text-align: center;
                background: #1A1A2E;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #FF6B6B, stop: 0.5 #4ECDC4, stop: 1 #45B7D1
                );
                border-radius: 4px;
            }
        """)
        
        self.setCursor(Qt.BusyCursor)
    
    def _tr_splash(self, key, default_text):
        if self.translator and hasattr(self.translator, 'translations'):
            return self.translator.translations.get(key, default_text)
        return default_text
    
    def set_progress(self, value, message=""):
        self.progress_bar.setValue(value)
        if message:
            translated_message = self._tr_splash(f"splash_{message.lower().replace(' ', '_')}", message)
            self.showMessage(translated_message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        
        QTimer.singleShot(10, self._process_events)
    
    def _process_events(self):
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()