import json
import os
from qframelesswindow import FramelessMainWindow

import gsedit
from gsedit.themes_editor_editor import EditorEditorWidget, EditorThemeBrowser, EditorThemeInfoWidget
from gsedit.themes_editor_lexer import LexerThemeInfoWidget, LexerThemeBrowser, LexerEditorWidget
from gsedit.custom_title_bar import CustomTitleBar
from gsedit.custom_color_picker import ColorPickerButton

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ThemeInfoWidget(QWidget):
    def __init__(self, lexer_theme_data, editor_theme_data, parent=None):
        super(ThemeInfoWidget, self).__init__(parent)
        self.window = parent
        self.lexer_theme_data = lexer_theme_data
        self.editor_theme_data = editor_theme_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        if(gsedit.gsconfig.get_config("syncThemes")):
            title_label = QLabel(f"Theme Name: {self.lexer_theme_data['active-theme']['theme-name']}")
            title_label.setStyleSheet(self.refresh_style("lexerViewTitleLabel"))
            version_label = QLabel(f"Version: {self.lexer_theme_data['active-theme']['version']}")
            version_label.setStyleSheet(self.refresh_style("lexerViewVersionLabel"))
            layout.addWidget(title_label)
            layout.addWidget(version_label)
        page_color = QColor(self.lexer_theme_data['active-theme']['syntax-rules'][0]['default']['page-color'])
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, page_color)
        self.setPalette(palette)
        font_family = self.lexer_theme_data['active-theme']['syntax-rules'][0]['default']['font-family']
        font_label = QLabel(f"Font Family: {font_family}")
        font_label.setStyleSheet(self.refresh_style("lexerViewFontLabel"))
        layout.addWidget(font_label)
        for rule in self.lexer_theme_data['active-theme']['syntax-rules']:
            for key, value in rule.items():
                syntax_label = QLabel(f"{key.capitalize()}")
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
        for key, value in self.editor_theme_data['active-theme']['colors'].items():
            syntax_label = QLabel(f"{key.capitalize()}")
            text_color = QColor(value)
            if key == "font_color":
                syntax_label.setStyleSheet(f"color: white; background-color: {self.editor_theme_data['active-theme']['colors']['font_color']}; padding: 5px; border-radius: 5px; font-size: 20px; font-family: Fire Code; font-weight: bold;")
            elif key == "main_color":
                syntax_label.setStyleSheet(f"color: white; background-color: {self.editor_theme_data['active-theme']['colors']['main_color']}; padding: 5px; border-radius: 5px; font-size: 20px; font-family: Fire Code; font-weight: bold;")
            else:
                syntax_label.setStyleSheet(f"color: white; background-color: {self.editor_theme_data['active-theme']['colors']['secondary_color']};padding: 5px; border-radius: 5px; font-size: 20px; font-family: Fire Code; font-weight: bold;")
            layout.addWidget(syntax_label)
        
        
        self.setLayout(layout)

    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()

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
        bottom_bar_layout.setSpacing(0)
        bottom_bar_layout.setDirection(QBoxLayout.LeftToRight)
        
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
        tab.setObjectName("mainTab")
        tab.setStyleSheet(self.refresh_style('mainTabThemeEditor'))
        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        
        main_theme_list = QListWidget()
        main_theme_list.setStyleSheet(self.refresh_style('themeEditorList'))
        separator = QListWidgetItem("Theme Overview")
        separator.setFlags(separator.flags() & ~Qt.ItemIsSelectable)
        separator.setFlags(separator.flags() & ~Qt.ItemIsEnabled) 
        font = QFont()
        font.setPointSize(20)
        separator.setFont(font)
        separator.setForeground(QColor("#ffffff"))
        separator.setTextAlignment(Qt.AlignCenter)
        main_theme_list.addItem(separator)
        main_theme_list.addItem("Current Theme")
        separator0 = QListWidgetItem("Lexer")
        separator0.setFlags(separator0.flags() & ~Qt.ItemIsSelectable)
        separator0.setFlags(separator0.flags() & ~Qt.ItemIsEnabled) 
        font = QFont()
        font.setPointSize(20)
        separator0.setFont(font)
        separator0.setForeground(QColor("#ffffff"))
        separator0.setTextAlignment(Qt.AlignCenter)
        main_theme_list.addItem(separator0)
        main_theme_list.addItem("Current Lexer Theme")
        main_theme_list.addItem("Customize Current Lexer Theme")
        main_theme_list.addItem("Browse Lexer Themes")
        separator1 = QListWidgetItem("Editor")
        separator1.setFlags(separator1.flags() & ~Qt.ItemIsSelectable)
        separator1.setFlags(separator1.flags() & ~Qt.ItemIsEnabled) 
        font = QFont()
        font.setPointSize(20)
        separator1.setFont(font)
        separator1.setForeground(QColor("#ffffff"))
        separator1.setTextAlignment(Qt.AlignCenter)
        main_theme_list.addItem(separator1)
        main_theme_list.addItem("Current Editor Theme")
        main_theme_list.addItem("Customize Current Editor Theme")
        main_theme_list.addItem("Browse Editor Themes")

        stack = QStackedWidget()
        stack.addWidget(ThemeInfoWidget(lexer_theme_data=gsedit.theme_editor.read_theme_file(), editor_theme_data=gsedit.theme_editor.read_editor_theme_file(), parent=self.mwindow))
        stack.addWidget(ThemeInfoWidget(lexer_theme_data=gsedit.theme_editor.read_theme_file(), editor_theme_data=gsedit.theme_editor.read_editor_theme_file(), parent=self.mwindow))
        stack.addWidget(LexerThemeInfoWidget(theme_data=gsedit.theme_editor.read_theme_file()))
        stack.addWidget(LexerThemeInfoWidget(theme_data=gsedit.theme_editor.read_theme_file()))
        stack.addWidget(LexerEditorWidget(theme_data=gsedit.theme_editor.read_theme_file(), parent=self.mwindow, brother=self))
        stack.addWidget(LexerThemeBrowser(theme_data=gsedit.theme_editor.read_theme_file(), parent=self.mwindow, brother=self))
        stack.addWidget(QLabel("TITLE"))
        stack.addWidget(EditorThemeInfoWidget(theme_data=gsedit.theme_editor.read_editor_theme_file()))
        stack.addWidget(EditorEditorWidget(theme_data=gsedit.theme_editor.read_editor_theme_file(), parent=self.mwindow, brother=self))
        stack.addWidget(EditorThemeBrowser(theme_data=gsedit.theme_editor.read_editor_theme_file(), parent=self.mwindow, brother=self))
        
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