import os
import json

import gsedit

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QListWidget, QListWidgetItem, QPushButton, QSpacerItem, QSizePolicy, QColorDialog
from PyQt5.QtCore import Qt

def css_to_qcolor(css_color):
    if css_color.startswith('#'):
        return QColor(css_color)
    return QColor()


class EditorThemeBrowser(QWidget):
    def __init__(self, theme_data, parent=None, brother=None):
        super(EditorThemeBrowser, self).__init__(parent)
        self.theme_data = theme_data
        self.window = parent
        self.thiswindow = brother
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        title_lbl = QLabel("View Editor Themes")
        title_lbl.setStyleSheet(self.refresh_style("editorEditorTitle"))
        title_lbl.setAlignment(Qt.AlignTop)
        layout.addWidget(title_lbl)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self.refresh_style("scrollAreaEditorThemes"))
        list_widget = QListWidget()
        list_widget.setStyleSheet(self.refresh_style("listWidgetEditorThemes"))
        list_widget.setMinimumWidth(scroll_area.width())

        theme_dir = os.path.join(os.path.dirname(__file__), 'editor-themes')
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
        theme_path = os.path.join(os.path.dirname(__file__), 'editor-themes', f'{selected_theme}.json')
        with open(theme_path, 'r') as file:
            theme_contents = json.load(file)

        gsedit.theme_editor.write_active_editor_theme(theme_contents)

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



    
class EditorEditorWidget(QWidget):
    def __init__(self, theme_data, parent=None, brother=None):
        super(EditorEditorWidget, self).__init__(parent)
        self.window = parent
        self.thiswindow = brother
        self.theme_data=theme_data
        self.og_theme_data = theme_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(0)
        title_lbl = QLabel("Customize Editor Theme")
        title_lbl.setStyleSheet(self.refresh_style("editorEditorTitle"))
        title_lbl.setAlignment(Qt.AlignTop)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(title_lbl)
        for key, value in self.theme_data['active-theme']['colors'].items():
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(0)
            label = QLabel(f"{key}: {value}")
            label.setStyleSheet(f"""color: {value}""")
            label.setStyleSheet(self.refresh_style('editorEditorRuleLabel'))
            edit_color = QPushButton("Edit")
            button_style = self.refresh_style("editorEditorRuleButton")
            button_style = button_style.strip()
            if button_style.endswith('}'):
                button_style = button_style[:-1].strip()
            new_style_sheet = f"{button_style} background-color: {value};}}"
            edit_color.setStyleSheet(new_style_sheet)
            edit_color.clicked.connect(lambda _, key=key, value=value, button=edit_color, text=label: self.edit_value(key, value, button, text))
            spacer_item = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            item_layout.addWidget(label)
            item_layout.addItem(spacer_item)
            item_layout.addWidget(edit_color)
            layout.addLayout(item_layout)
        
        save_button = QPushButton("Save Changes and Reload")
        save_button.setStyleSheet(self.refresh_style('editorEditorSaveButton'))
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)
        
        self.setLayout(layout)


    def save_changes(self):
        pass
        gsedit.theme_editor.write_editor_theme_file(self.theme_data)
        try:
            self.thiswindow.close()
            self.window.close()
            os.system("gs")
        except Exception as e:
            self.window.statusBar().showMessage(f"Failed to restart: {e}")

    def edit_value(self, key, value, button, text):
        color = QColorDialog.getColor(css_to_qcolor(value))
        if color.isValid():
            new_color = color.name()
            text.setText(f"{key}: {new_color}")
            button_style = self.refresh_style("editorEditorRuleButton")
            button_style = button_style.strip()
            if button_style.endswith('}'):
                button_style = button_style[:-1].strip()
            new_style_sheet = f"{button_style} background-color: {new_color};}}"

            print(new_style_sheet)
            button.setStyleSheet(new_style_sheet)
            for rule in self.theme_data['active-theme']['colors']:
                if key in rule:
                    self.theme_data['active-theme']['colors'][key]= new_color
                    break
            

        
    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()


class EditorThemeInfoWidget(QWidget):
    def __init__(self, theme_data, parent=None):
        super(EditorThemeInfoWidget, self).__init__(parent)
        
        self.theme_data = theme_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel(f"Theme Name: {self.theme_data['active-theme']['theme-name']}")
        title_label.setStyleSheet(self.refresh_style("editorViewTitleLabel"))
        version_label = QLabel(f"Version: {self.theme_data['active-theme']['version']}")
        version_label.setStyleSheet(self.refresh_style("editorViewVersionLabel"))
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        for key, value in self.theme_data['active-theme']['colors'].items():
            syntax_label = QLabel(f"{key.capitalize()}")
            text_color = QColor(value)
            if key == "font_color":
                syntax_label.setStyleSheet(f"color: white; background-color: {self.theme_data['active-theme']['colors']['font_color']}; padding: 5px; border-radius: 5px; font-size: 20px; font-family: Fire Code; font-weight: bold;")
            elif key == "main_color":
                syntax_label.setStyleSheet(f"color: white; background-color: {self.theme_data['active-theme']['colors']['main_color']}; padding: 5px; border-radius: 5px; font-size: 20px; font-family: Fire Code; font-weight: bold;")
            else:
                syntax_label.setStyleSheet(f"color: white; background-color: {self.theme_data['active-theme']['colors']['secondary_color']};padding: 5px; border-radius: 5px; font-size: 20px; font-family: Fire Code; font-weight: bold;")
            layout.addWidget(syntax_label)
        
        self.setLayout(layout)

    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()

