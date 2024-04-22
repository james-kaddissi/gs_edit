from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import re
import sys
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

        self.valid_properties = ['color', 'background-color', 'border-color', 'font-size', 'margin', 'padding']  


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

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_css)
        self.apply_button = QPushButton("Reload")
        self.apply_button.clicked.connect(self.restart_program)
        self.reload_button = QPushButton("Save and Reload")
        self.reload_button.clicked.connect(self.apply_styles)
        

        self.statusBar()
        self.load_file_list()
        self.refresh_style()
        self.splitter.setSizes([300, 500])

    def refresh_style(self):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', 'cssEditor.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

    def load_file_list(self):
        base_path = os.path.dirname(__file__) 
        css_path = os.path.join(base_path, 'css')  

        if not os.path.exists(css_path):
            self.statusBar().showMessage('CSS directory not found: {}'.format(css_path))
            return

        for file_name in os.listdir(css_path):
            if file_name.endswith('.qss'):
                self.file_browser.addItem(file_name)

    def load_css_properties(self, current, previous):
        if not current:
            return

        base_path = os.path.dirname(__file__)
        css_path = os.path.join(base_path, 'css', current.text())
        
        self.refresh_css_editor(css_path)

    def refresh_css_editor(self, file_path):
        while self.property_layout.count():
            child = self.property_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.property_layout.addWidget(QLabel(f"Editing: {file_path}"))
        self.list_view = QListWidget()
        self.list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
        self.css_blocks = {} 
        try:
            with open(file_path, 'r') as file:
                css_content = file.read()
            blocks = self.extract_blocks(css_content)
            for widget_name, styles in blocks:
                self.css_blocks[widget_name] = {}
                header_item = QListWidgetItem(f"{widget_name} Styles:")
                header_item.setData(Qt.UserRole, widget_name)
                self.list_view.addItem(header_item)
                for line in styles.split(';'):
                    if ':' in line:
                        prop, value = line.split(':')
                        prop, value = prop.strip(), value.strip()
                        self.css_blocks[widget_name][prop] = value  
                        widget = QWidget()
                        widget.setProperty('css_selector', widget_name) 
                        row_layout = QHBoxLayout(widget)
                        row_layout.addWidget(QLabel(prop))
                        if is_color_property(prop):
                            color_button = QPushButton()
                            color_button.setStyleSheet(f"background-color: {value}; border: none;")
                            color_button.clicked.connect(lambda _, p=prop, v=value, b=color_button, s=widget_name:
                                self.change_color(p, v, b, s))
                            row_layout.addWidget(color_button)
                        else:
                            editor = QLineEdit(value)
                            editor.textChanged.connect(lambda v, p=prop, s=widget_name:
                                                       self.update_property_value(s, p, v))
                            row_layout.addWidget(editor)
                        list_item = QListWidgetItem(self.list_view)
                        list_item.setSizeHint(widget.sizeHint())
                        self.list_view.addItem(list_item)
                        self.list_view.setItemWidget(list_item, widget)
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load file: {e}")
        self.property_layout.addWidget(self.list_view)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.apply_button)
        self.buttons_layout.addWidget(self.reload_button)
        self.property_layout.addLayout(self.buttons_layout)

    def save_css(self):
        css_content = ""
        for selector, properties in self.css_blocks.items():
            css_content += f"{selector} {{" + "\n"
            for prop, value in properties.items():
                css_content += f"    {prop}: {value};\n"
            css_content += "}\n\n"
        with open(self.current_file, 'w') as file:
            file.write(css_content)
        self.statusBar().showMessage("CSS saved successfully.")

    def update_property_value(self, selector, property_name, value):
        if selector in self.css_blocks:
            self.css_blocks[selector][property_name] = value
            self.save_css() 

    def restart_program(self):
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            self.statusBar().showMessage(f"Failed to restart: {e}")

    def apply_styles(self):
        self.save_css() 
        self.restart_program()
    def reload_styles(self):
        self.refresh_css_editor(self.current_file)

    def extract_blocks(self, css_content):
        pattern = r"(\w+[^{]*)\s*\{([^\}]*)\}"
        matches = re.findall(pattern, css_content)
        return [(match[0].strip(), match[1].strip()) for match in matches]

    def change_color(self, property_name, current_color, button, selector):
        color = QColorDialog.getColor(css_to_qcolor(current_color))
        if color.isValid():
            new_color = color.name()
            button.setStyleSheet(f"background-color: {new_color}; border: none;")
            self.update_property_value(selector, property_name, new_color)

    def show_context_menu(self, position):
        item = self.list_view.itemAt(position)
        if item is not None:
            menu = QMenu()
            add_property_action = menu.addAction("Add Property")
            action = menu.exec_(self.list_view.viewport().mapToGlobal(position))
            if action == add_property_action:
                self.add_new_property(item)

    def add_new_property(self, item):
        if item.data(Qt.UserRole):
            selector = item.data(Qt.UserRole)
            key, ok = QInputDialog.getItem(self, "Select Property", "Choose a CSS property to add:", self.valid_properties, 0, False)
            if ok and key:
                value, ok = QInputDialog.getText(self, "Enter Value", "Enter the value for the property:")
                if ok and value:
                    if selector in self.css_blocks:
                        self.css_blocks[selector][key] = value
                        self.save_css()
                    self.refresh_css_editor(self.current_file) 

