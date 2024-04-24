from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pathlib import Path
from gsedit.text_editor import TextEditor
import gsedit.gsconfig

import os

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
        base_path = os.path.dirname(__file__) 
        style_sheet_path = os.path.join(base_path, 'css', 'grep.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

class GrepResult(QListWidget):
    def __init__(self, window) -> None:
        super(GrepResult, self).__init__()
        self.window = window
        self.initialize_results()
        self.refresh_style()

    def refresh_style(self):
        base_path = os.path.dirname(__file__) 
        style_sheet_path = os.path.join(base_path, 'css', 'grep.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

    def initialize_results(self):
        self.setFont(QFont("Fixedsys", 14))
        self.itemClicked.connect(self.grep_view_clicked)

    def grep_view_clicked(self, content):
        self.add_tab(self.window, Path(content.path))
        editor = self.window.tab.currentWidget()
        editor.setCursorPosition(content.ln, content.endln)
        editor.setFocus()

    def finish_grep(self, content):
        self.clear()
        for i in content:
            self.addItem(i)

    def text_editor(self, path=None, pyf=None, cf=None, jsonf=None, rustf=None, cppf=None, jsf=None) -> QsciScintilla:
        editor = TextEditor(self.window, path=path, pyf=pyf, cf=cf, jsonf=jsonf, rustf=rustf, cppf=cppf, jsf=jsf)
        return editor

    def valid_file_check(self, path):
        with open(path, 'rb') as f:
            return b'\0' in f.read(1024)

    def add_tab(self, window, path: Path, is_new_file=False):
        if not is_new_file and self.valid_file_check(path):
            window.statusBar().set_timed_message("Cannot open this file type", 2000)
            return
        if path.is_dir():
            return

        editor = self.text_editor(
            path,
            path.suffix in gsedit.gsconfig.get_consideration("python"), 
            path.suffix in gsedit.gsconfig.get_consideration("c"), 
            path.suffix in gsedit.gsconfig.get_consideration("json"),
            path.suffix in gsedit.gsconfig.get_consideration("rust"), 
            path.suffix in gsedit.gsconfig.get_consideration("cpp"),
            path.suffix in gsedit.gsconfig.get_consideration("javascript")
        )
        if is_new_file:
            window.tab.addTab(editor, "untitled")
            window.setWindowTitle("untitled - " + window.app_title)
            window.statusBar().set_timed_message("untitled created", 2000)
            window.tab.setCurrentIndex(window.tab.count() - 1)
            window.current_file = None
            return

        for i in range(window.tab.count()):
            if window.tab.tabText(i) == path.name or window.tab.tabText(i) == "*" + path.name:
                window.tab.setCurrentIndex(i)
                window.current_file = path
                return

        window.tab.addTab(editor, path.name)

        if not is_new_file:
            editor.setText(path.read_text(encoding="utf-8"))
        window.setWindowTitle(path.name)
        window.current_file = path
        window.tab.setCurrentIndex(window.tab.count() - 1)
        window.statusBar().set_timed_message(f"{path.name} opened", 2000)