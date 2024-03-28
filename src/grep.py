from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pathlib import Path

class GrepLayout(QVBoxLayout):
    def __init__(self) -> None:
        super(GrepLayout, self).__init__()
        self.initialize_layout()

    def initialize_layout(self):
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setContentsMargins(0, 10, 0, 0)
        self.setSpacing(0)

class Searchbar(QLineEdit):
    def __init__(self, window) -> None:
        super(Searchbar, self).__init__()
        self.window = window
        self.initialize_searchbar()

    def initialize_searchbar(self):
        self.setPlaceholderText("Search")
        self.setFont(self.window.window_font)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

class GrepToggle(QCheckBox):
    def __init__(self, window) -> None:
        super(GrepToggle, self).__init__()
        self.setText("Venv?")
        self.window = window
        self.initialize_toggler()
        self.refresh_style()
    
    def initialize_toggler(self):
        self.setFont(self.window.window_font)

    def refresh_style(self):
        self.setStyleSheet(open("./src/css/grep.qss", "r").read())

class GrepResult(QListWidget):
    def __init__(self, window) -> None:
        super(GrepResult, self).__init__()
        self.window = window
        self.initialize_results()

    def initialize_results(self):
        self.setFont(QFont("Consolas", 14))
        self.setStyleSheet("""
            QListWidget {
                background-color: #0C0C1A;
                border-radius: 5px;
                border: 1px solid #CDCDCD;
                padding: 5px;
                color: #CDCDCD;
            }
        """)
        self.itemClicked.connect(self.grep_view_clicked)

    def grep_view_clicked(self, content):
        self.window.add_tab(Path(content.path))
        editor = self.window.tab.currentWidget()
        editor.setCursorPosition(content.ln, content.endln)
        editor.setFocus()