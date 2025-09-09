# utils/theme_manager.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


def apply_theme(theme_name):
    """
    Applies a color theme to the application.
    Currently supports only 'dark' theme. Falls back to default theme otherwise.
    """
    app = QApplication.instance()
    if app is None:
        return

    if theme_name == "dark":
        palette = QPalette()

        # Define dark theme colors
        dark_bg = QColor(45, 45, 45)          # Main background
        dark_widget = QColor(55, 55, 55)      # Widget background
        dark_border = QColor(80, 80, 80)      # Border and separator color
        dark_text = QColor(220, 220, 220)     # Text color
        dark_highlight = QColor(75, 110, 175) # Highlight/selection color
        dark_menu = QColor(50, 50, 50)        # Menu background

        # Set palette colors
        palette.setColor(QPalette.Window, dark_bg)
        palette.setColor(QPalette.WindowText, dark_text)
        palette.setColor(QPalette.Base, dark_widget)
        palette.setColor(QPalette.AlternateBase, dark_bg)
        palette.setColor(QPalette.ToolTipBase, dark_bg)
        palette.setColor(QPalette.ToolTipText, dark_text)
        palette.setColor(QPalette.Text, dark_text)
        palette.setColor(QPalette.Button, dark_widget)
        palette.setColor(QPalette.ButtonText, dark_text)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, dark_highlight)
        palette.setColor(QPalette.Highlight, dark_highlight)
        palette.setColor(QPalette.HighlightedText, Qt.white)

        # Ensure menu and button colors are consistent
        palette.setColor(QPalette.Button, dark_menu)
        palette.setColor(QPalette.ButtonText, dark_text)

        app.setPalette(palette)

        # Apply custom dark stylesheet
        dark_stylesheet = f"""
        /* MAIN WINDOW AND BACKGROUNDS */
        QMainWindow, QWidget {{
            background-color: {dark_bg.name()};
            color: {dark_text.name()};
        }}

        /* MENU BAR */
        QMenuBar {{
            background-color: {dark_menu.name()};
            color: {dark_text.name()};
            border-bottom: 1px solid {dark_border.name()};
        }}

        QMenuBar::item {{
            background-color: transparent;
            color: {dark_text.name()};
            padding: 4px 10px;
            border-radius: 2px;
        }}

        QMenuBar::item:selected {{
            background-color: {dark_highlight.name()};
        }}

        QMenuBar::item:pressed {{
            background-color: {dark_highlight.darker(120).name()};
        }}

        /* DROP-DOWN MENUS */
        QMenu {{
            background-color: {dark_menu.name()};
            color: {dark_text.name()};
            border: 1px solid {dark_border.name()};
        }}

        QMenu::item {{
            background-color: transparent;
            padding: 4px 20px 4px 10px;
            border: 1px solid transparent;
        }}

        QMenu::item:selected {{
            background-color: {dark_highlight.name()};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {dark_border.name()};
            margin: 4px 0px;
        }}

        /* GROUP BOXES */
        QGroupBox {{
            color: {dark_text.name()};
            border: 2px solid {dark_border.name()};
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: {dark_widget.name()};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {dark_text.name()};
            background-color: transparent;
        }}

        /* LABELS */
        QLabel {{
            color: {dark_text.name()};
            background-color: transparent;
        }}

        /* FORM CONTROLS */
        QComboBox, QSpinBox, QLineEdit, QTextEdit {{
            background-color: {dark_widget.name()};
            color: {dark_text.name()};
            border: 1px solid {dark_border.name()};
            padding: 2px;
            border-radius: 3px;
            selection-background-color: {dark_highlight.name()};
        }}

        QComboBox:editable, QLineEdit:editable {{
            background: {dark_widget.lighter(110).name()};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: {dark_border.name()};
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }}

        /* BUTTONS */
        QPushButton {{
            background-color: {dark_widget.name()};
            color: {dark_text.name()};
            border: 1px solid {dark_border.name()};
            padding: 5px;
            border-radius: 3px;
        }}

        QPushButton:hover {{
            background-color: {dark_widget.lighter(120).name()};
        }}

        QPushButton:pressed {{
            background-color: {dark_widget.darker(120).name()};
        }}

        QPushButton:disabled {{
            background-color: {dark_widget.darker(150).name()};
            color: {dark_text.darker(150).name()};
        }}

        /* TABS */
        QTabWidget::pane {{
            border: 1px solid {dark_border.name()};
            background-color: {dark_widget.name()};
        }}

        QTabBar::tab {{
            background-color: {dark_menu.name()};
            color: {dark_text.name()};
            padding: 8px;
            border: 1px solid {dark_border.name()};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {dark_widget.name()};
            border-bottom: 1px solid {dark_widget.name()};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {dark_menu.lighter(120).name()};
        }}

        /* PROGRESS BARS */
        QProgressBar {{
            border: 1px solid {dark_border.name()};
            border-radius: 3px;
            text-align: center;
            background-color: {dark_widget.name()};
        }}

        QProgressBar::chunk {{
            background-color: {dark_highlight.name()};
            width: 10px;
        }}
        """

        app.setStyleSheet(dark_stylesheet)

    else:
        # Reset to system default theme
        app.setPalette(QApplication.style().standardPalette())
        app.setStyleSheet("")