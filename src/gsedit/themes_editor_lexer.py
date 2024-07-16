import os
import json

import gsedit
from gsedit.custom_mini_lexer import SimpleScintillaEditor

from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QListWidget, QListWidgetItem, QPushButton, QSpacerItem, QSizePolicy, QColorDialog
from PyQt5.QtCore import Qt


def css_to_qcolor(css_color):
    if css_color.startswith('#'):
        return QColor(css_color)
    return QColor()

class LexerThemeBrowser(QWidget):
    def __init__(self, theme_data, parent=None, brother=None):
        super(LexerThemeBrowser, self).__init__(parent)
        self.theme_data = theme_data
        self.window = parent
        self.thiswindow = brother
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        title_lbl = QLabel("View Lexer Themes")
        title_lbl.setStyleSheet(self.refresh_style("lexerEditorTitle"))
        title_lbl.setAlignment(Qt.AlignTop)
        layout.addWidget(title_lbl)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self.refresh_style("scrollAreaLexerThemes"))
        list_widget = QListWidget()
        list_widget.setStyleSheet(self.refresh_style("listWidgetLexerThemes"))
        list_widget.setMinimumWidth(scroll_area.width())

        theme_dir = os.path.join(os.path.dirname(__file__), 'lexer-themes')
        if os.path.exists(theme_dir) and os.path.isdir(theme_dir):
            for file_name in os.listdir(theme_dir):
                if file_name.endswith('.json'):
                    theme_name = os.path.splitext(file_name)[0]
                    list_item = QListWidgetItem(theme_name)
                    list_widget.addItem(list_item)

        scroll_area.setWidget(list_widget)
        layout.addWidget(scroll_area)
        save_button = QPushButton("Save Theme")
        save_button.setStyleSheet(self.refresh_style('themeBrowserSaveButton'))
        save_button.clicked.connect(self.save_active_theme)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def save_active_theme(self):
        selected_items = self.findChildren(QListWidget)
        selected_theme = selected_items[0].currentItem().text()
        theme_path = os.path.join(os.path.dirname(__file__), 'lexer-themes', f'{selected_theme}.json')
        with open(theme_path, 'r') as file:
            theme_contents = json.load(file)

        gsedit.theme_editor.write_active_theme(theme_contents)

        try:
            self.thiswindow.close()
            self.window.close()
            os.system("gs")
        except Exception as e:
            self.window.statusBar().showMessage(f"Failed to restart: {e}")
    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()
    
class LexerEditorWidget(QWidget):
    def __init__(self, theme_data, parent=None, brother=None):
        super(LexerEditorWidget, self).__init__(parent)
        self.window = parent
        self.thiswindow = brother
        self.theme_data=theme_data
        self.og_theme_data = theme_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(0)
        title_lbl = QLabel("Customize Lexer")
        title_lbl.setStyleSheet(self.refresh_style("lexerEditorTitle"))
        title_lbl.setAlignment(Qt.AlignTop)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(title_lbl)
        
        for rule in self.theme_data['active-theme']['syntax-rules']:
            for key, value in rule.items():
                item_layout = QHBoxLayout()
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(0)
                label = QLabel(f"{key}: {value['text-color']}")
                label.setStyleSheet(f"""color: {value['text-color']}""")
                label.setStyleSheet(self.refresh_style('lexerEditorRuleLabel'))
                edit_color = QPushButton("Edit")
                button_style = self.refresh_style("lexerEditorRuleButton")
                button_style = button_style.strip()
                if button_style.endswith('}'):
                    button_style = button_style[:-1].strip()
                new_style_sheet = f"{button_style} background-color: {value['text-color']};}}"
                edit_color.setStyleSheet(new_style_sheet)
                edit_color.clicked.connect(lambda _, key=key, value=value, button=edit_color, text=label: self.edit_value(key, value, button, text))
                spacer_item = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
                item_layout.addWidget(label)
                item_layout.addItem(spacer_item)
                item_layout.addWidget(edit_color)
                layout.addLayout(item_layout) 
        
        self.editor = SimpleScintillaEditor(theme_data=self.theme_data, parent=self)
        layout.addWidget(self.editor)
        save_button = QPushButton("Save Changes and Reload")
        save_button.setStyleSheet(self.refresh_style('lexerEditorSaveButton'))
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)
        
        self.setLayout(layout)


    def save_changes(self):
        gsedit.theme_editor.write_theme_file(self.theme_data)
        self.editor.refreshLexer(self.theme_data)
        try:
            self.thiswindow.close()
            self.window.close()
            os.system("gs")
        except Exception as e:
            self.window.statusBar().showMessage(f"Failed to restart: {e}")

    def edit_value(self, key, value, button, text):
        color = QColorDialog.getColor(css_to_qcolor(value['text-color']))
        if color.isValid():
            new_color = color.name()
            text.setText(f"{key}: {new_color}")
            button_style = self.refresh_style("lexerEditorRuleButton")
            button_style = button_style.strip()
            if button_style.endswith('}'):
                button_style = button_style[:-1].strip()
            new_style_sheet = f"{button_style} background-color: {new_color};}}"

            print(new_style_sheet)
            button.setStyleSheet(new_style_sheet)
            for rule in self.theme_data['active-theme']['syntax-rules']:
                if key in rule:
                    rule[key]['text-color'] = new_color
                    self.editor.refreshLexer(self.theme_data)
            

        
    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()


class LexerThemeInfoWidget(QWidget):
    def __init__(self, theme_data, parent=None):
        super(LexerThemeInfoWidget, self).__init__(parent)
        
        self.theme_data = theme_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel(f"Theme Name: {self.theme_data['active-theme']['theme-name']}")
        title_label.setStyleSheet(self.refresh_style("lexerViewTitleLabel"))
        version_label = QLabel(f"Version: {self.theme_data['active-theme']['version']}")
        version_label.setStyleSheet(self.refresh_style("lexerViewVersionLabel"))
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        page_color = QColor(self.theme_data['active-theme']['syntax-rules'][0]['default']['page-color'])
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, page_color)
        self.setPalette(palette)
        font_family = self.theme_data['active-theme']['syntax-rules'][0]['default']['font-family']
        font_label = QLabel(f"Font Family: {font_family}")
        font_label.setStyleSheet(self.refresh_style("lexerViewFontLabel"))
        layout.addWidget(font_label)
        for rule in self.theme_data['active-theme']['syntax-rules']:
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
        
        
        self.setLayout(layout)

    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()