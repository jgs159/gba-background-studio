# ui/main_window/dialogs.py
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

def show_contribute(main_window):
    contribute_text = main_window.translator.tr("contribute_text")
    
    msg_box = QMessageBox(main_window)
    msg_box.setWindowTitle(main_window.translator.tr("contribute_title"))
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(contribute_text)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()

def show_about(main_window):
    about_text = main_window.translator.tr("about_text")
    
    msg_box = QMessageBox(main_window)
    msg_box.setWindowTitle(main_window.translator.tr("about_title"))
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(about_text)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()
