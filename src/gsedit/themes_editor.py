from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pygame import Color
from qframelesswindow import FramelessMainWindow, TitleBar
from gsedit.top_bar import TopBarSmall
import gsedit.theme_editor
import os
import gsedit.gsconfig

class ColorPickerButton(QWidget):
    def __init__(self, parent=None):
        super(ColorPickerButton, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.color_label = QLabel(self)
        self.color_label.setText("Color Picker")
        self.color_label.setStyleSheet("background-color: red; color: white;")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setFixedSize(70, 30)
        font_size = 7 
        font = QFont()
        font.setPointSize(font_size)
        self.color_label.setFont(font)
        
        self.color_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.color_label.mousePressEvent = self.start_color_picker

    def start_color_picker(self, event):
        self.grabMouse()
        self.setCursor(Qt.CrossCursor)
        self.color_label.setText("Picking...")

    def mouseMoveEvent(self, event):
        screen = QApplication.primaryScreen()
        color = screen.grabWindow(QApplication.desktop().winId(), event.globalX(), event.globalY(), 1, 1).toImage().pixel(0, 0)
        color = QColor(color)
        hex_color = color.name()
        print(hex_color)
        self.color_label.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 5px;")
        self.color_label.setText(hex_color)
        self.update()

    def mousePressEvent(self, event):
        screen = QApplication.primaryScreen()
        color = screen.grabWindow(QApplication.desktop().winId(), event.globalX(), event.globalY(), 1, 1).toImage().pixel(0, 0)
        color = QColor(color)
        hex_color = color.name()
        clipboard = QApplication.clipboard()
        clipboard.setText(hex_color)
        self.releaseMouse()
        self.setCursor(Qt.ArrowCursor)
        self.color_label.setText(f"Copied: {hex_color}")
        self.color_label.setStyleSheet(f"background-color: {hex_color}; color: white;")

class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.minBtn.setHoverColor(Qt.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.minBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }""")
        
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)
        self.closeBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: red;
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)

class LexerEditorWidget(QWidget):
    def __init__(self, theme_data, parent=None):
        super(LexerEditorWidget, self).__init__(parent)
        self.theme_data=theme_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title_lbl = QLabel("Customize Lexer")
        title_lbl.setStyleSheet(self.refresh_style("lexerEditorTitle"))
        
        layout.addWidget(title_lbl)
        self.setLayout(layout)
    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()

class ThemeInfoWidget(QWidget):
    def __init__(self, theme_data, parent=None):
        super(ThemeInfoWidget, self).__init__(parent)
        
        self.theme_data = theme_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel(f"Theme Name: {self.theme_data['active-theme']['theme-name']}")
        version_label = QLabel(f"Version: {self.theme_data['active-theme']['version']}")
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        page_color = QColor(self.theme_data['active-theme']['syntax-rules'][0]['default']['page-color'])
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, page_color)
        self.setPalette(palette)
        font_family = self.theme_data['active-theme']['syntax-rules'][0]['default']['font-family']
        font_label = QLabel(f"Font Family: {font_family}")
        layout.addWidget(font_label)
        for rule in self.theme_data['active-theme']['syntax-rules']:
            for key, value in rule.items():
                syntax_label = QLabel(f"{key.capitalize()}: example1 example2 example3")
                font = QFont()
                font.setFamily(value['font-family'])
                font.setPointSize(value['font-size'])
                font.setWeight(QFont.Normal if value['font-weight'] == "normal" else QFont.Bold)
                font.setItalic(value['italic'])
                font.setUnderline(value['underlined'])
                font.setStrikeOut(value['strikethrough'])
                
                syntax_label.setFont(font)
                
                text_color = QColor(value['text-color'])
                syntax_label.setStyleSheet(f"color: {text_color.name()};")
                
                layout.addWidget(syntax_label)
        
        self.setLayout(layout)

class ThemeEditor(FramelessMainWindow):
    def __init__(self, parent=None):
        super(ThemeEditor, self).__init__(parent)
        self.setWindowTitle("Theme Editor")
        self.resize(800, 600)
        self.mwindow = parent
        self.title_bar = CustomTitleBar(self)
        self.setTitleBar(self.title_bar)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        main_theme_tab = self.mainTab()
        
        self.main_layout.addWidget(main_theme_tab)
        
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.color_picker = ColorPickerButton()
        self.color_picker.setFixedSize(70, 30)
        self.color_picker.setStyleSheet("""margin: 0px; padding: 0px""")
        bottom_bar_layout.addWidget(self.color_picker, alignment=Qt.AlignBottom | Qt.AlignLeft)
        self.main_layout.addLayout(bottom_bar_layout)
        
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setLayout(self.main_layout)
        self.main_widget.setStyleSheet(self.refresh_style('mainWidgetThemeEditor'))
        self.setCentralWidget(self.main_widget)
        self.setStyleSheet(self.refresh_style('themeEditor'))

        self.titleBar.raise_()
        
    def mainTab(self):
        tab = QWidget()
        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        main_theme_list = QListWidget()
        main_theme_list.addItem("Current Theme")
        main_theme_list.addItem("Customize Current Theme")
        main_theme_list.addItem("Browse Themes")
        
        stack = QStackedWidget()
        stack.addWidget(ThemeInfoWidget(theme_data=gsedit.theme_editor.read_theme_file()))
        stack.addWidget(LexerEditorWidget(theme_data=gsedit.theme_editor.read_theme_file()))
        stack.addWidget(QLabel("Browse Themes"))
        
        main_theme_list.currentRowChanged.connect(stack.setCurrentIndex)
        
        tab_layout.addWidget(main_theme_list)
        tab_layout.addWidget(stack)
        
        tab.setLayout(tab_layout)
        return tab
    
    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()