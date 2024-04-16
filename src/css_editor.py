from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class CSSEditor(QMainWindow):
    def __init__(self, parent=None):
        super(CSSEditor, self).__init__(parent)
        self.setWindowTitle("CSS Editor")
        self.resize(600, 400)

        # Set up the text edit widget for CSS
        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setStyleSheet("color: #000; background-color: #fff;")

        # Save button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_css)

        # Layout setup
        layout = QVBoxLayout()
        widget = QWidget()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.save_button)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load_css(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.text_edit.setPlainText(file.read())
                self.current_file = file_path
        except Exception as e:
            print(f"Failed to load file: {e}")

    def save_css(self):
        if hasattr(self, 'current_file'):
            with open(self.current_file, 'w') as file:
                file.write(self.text_edit.toPlainText())
            self.statusBar().showMessage("File saved successfully", 2000)
        else:
            self.save_css_as()

    def save_css_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "CSS files (*.css)")
        if path:
            self.current_file = path
            self.save_css()
