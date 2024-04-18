from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import re

def is_color_property(prop_name):
    color_props = ['color', 'background-color', 'border-color']
    return any(prop in prop_name for prop in color_props)

def css_to_qcolor(css_color):
    if css_color.startswith('#'):
        return QColor(css_color)
    return QColor()

class CSSEditor(QMainWindow):
    def __init__(self, parent=None):
        super(CSSEditor, self).__init__(parent)
        self.setWindowTitle("CSS Editor")
        self.resize(800, 600)

        self.splitter = QSplitter(self)
        self.setCentralWidget(self.splitter)

        self.file_browser = QListWidget(self.splitter)
        self.file_browser.currentItemChanged.connect(self.load_css_properties)

        self.scroll_area = QScrollArea(self.splitter)
        self.scroll_area.setWidgetResizable(True)
        self.property_editor = QWidget()
        self.scroll_area.setWidget(self.property_editor)
        self.property_layout = QVBoxLayout(self.property_editor)
        self.property_editor.setLayout(self.property_layout)

        # Save and Reload Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_css)
        self.apply_button = QPushButton("Apply Styles")
        self.apply_button.clicked.connect(self.apply_styles)
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload_styles)
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.apply_button)
        self.buttons_layout.addWidget(self.reload_button)
        self.property_layout.addLayout(self.buttons_layout)

        self.statusBar()
        self.load_file_list()
        self.refresh_style()

    def refresh_style(self):
        try:
            with open("./src/css/cssEditor.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load style: {e}")

    def load_file_list(self):
        path = './src/css'
        for file_name in os.listdir(path):
            if file_name.endswith('.qss'):
                self.file_browser.addItem(file_name)

    def load_css_properties(self, current, previous):
        if not current:
            return
        self.current_file = f"./src/css/{current.text()}"  
        self.refresh_css_editor(self.current_file)

    def refresh_css_editor(self, file_path):
        self.property_layout.addWidget(QLabel(f"Editing: {file_path}"))
        self.list_view = QListWidget()
        self.list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        try:
            with open(file_path, 'r') as file:
                css_content = file.read()
            blocks = self.extract_blocks(css_content)
            for block in blocks:
                widget_name, styles = block
                self.list_view.addItem(QListWidgetItem(f"{widget_name} Styles:"))
                for line in styles.split(';'):
                    if ':' in line:
                        prop, value = line.split(':')
                        prop, value = prop.strip(), value.strip()
                        widget = QWidget()
                        row_layout = QHBoxLayout(widget)
                        row_layout.addWidget(QLabel(prop))
                        if is_color_property(prop):
                            color_button = QPushButton()
                            color_button.setStyleSheet(f"background-color: {value}; border: none;")
                            color_button.clicked.connect(lambda _, p=prop, v=value, b=color_button: self.change_color(p, v, b))
                            row_layout.addWidget(color_button)
                        else:
                            editor = QLineEdit(value)
                            row_layout.addWidget(editor)
                        list_item = QListWidgetItem(self.list_view)
                        list_item.setSizeHint(widget.sizeHint())
                        self.list_view.addItem(list_item)
                        self.list_view.setItemWidget(list_item, widget)
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load file: {e}")
        self.property_layout.addWidget(self.list_view)

    def save_css(self):
        css_content = ""
        for i in range(self.list_view.count()):
            item = self.list_view.item(i)
            widget = self.list_view.itemWidget(item)
            if widget:
                layout = widget.layout()
                if layout:
                    label = layout.itemAt(0).widget().text()
                    editor = layout.itemAt(1).widget()
                    value = editor.text() if isinstance(editor, QLineEdit) else editor.styleSheet().split(':')[1].split(';')[0].strip()
                    css_content += f"{label}: {value};\n"
        with open(self.current_file, 'w') as file:
            file.write(css_content)
        self.statusBar().showMessage("CSS saved successfully.")

    def apply_styles(self):
        self.refresh_style()

    def reload_styles(self):
        self.refresh_css_editor(self.current_file)

    def extract_blocks(self, css_content):
        pattern = r"(\w+[^{]*)\s*\{([^\}]*)\}"
        matches = re.findall(pattern, css_content)
        return [(match[0].strip(), match[1].strip()) for match in matches]

    def change_color(self, property_name, current_color, button):
        color = QColorDialog.getColor(css_to_qcolor(current_color))
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: none;")
            button.setText(color.name()) 

