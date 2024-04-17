from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def is_color_property(prop_name):
    # Extend this function to include other CSS color properties
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

        self.statusBar()
        self.load_file_list()

    def load_file_list(self):
        import os
        path = './src/css'
        for file_name in os.listdir(path):
            if file_name.endswith('.qss'):
                self.file_browser.addItem(file_name)

    def load_css_properties(self, current, previous):
        if not current:
            return

        for i in reversed(range(self.property_layout.count())): 
            widget_to_remove = self.property_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        file_path = f"./src/css/{current.text()}"
        self.property_layout.addWidget(QLabel(f"Editing: {file_path}"))

        try:
            with open(file_path, 'r') as file:
                css_content = file.read()
                for line in css_content.split(';'):
                    if ':' in line:
                        prop, value = line.split(':')
                        prop, value = prop.strip(), value.strip()
                        row_layout = QHBoxLayout()
                        row_layout.addWidget(QLabel(prop))
                        if is_color_property(prop):
                            color_button = QPushButton()
                            color_button.setStyleSheet(f"background-color: {value}; border: none;")
                            color_button.clicked.connect(lambda _, p=prop, v=value: self.change_color(p, v, color_button))
                            row_layout.addWidget(color_button)
                        else:
                            editor = QLineEdit(value)
                            row_layout.addWidget(editor)
                        self.property_layout.addLayout(row_layout)
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load file: {e}")

    def change_color(self, property_name, current_color, button):
        color = QColorDialog.getColor(css_to_qcolor(current_color))
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: none;")

    def save_css(self):
        # Implementation needed to save changes back to the CSS file
        pass

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    editor = CSSEditor()
    editor.show()
    sys.exit(app.exec_())
