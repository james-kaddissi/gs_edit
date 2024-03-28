'''
This is the main application of GS-Edit. Keeping this file organized is especially important. Try refactoring code into new files.
'''

# Python imports
import sys
import os
from pathlib import Path
# PyQt imports (migration to PyQt6 should be a simple task for a future date)
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# Class imports

from text_editor import TextEditor
from grepgine import Grepgine, GrepListItem
from file_explorer import FileExplorer, FileExplorerLayout
from code_completer import Completer
from status_bar import StatusBar
from menu_bar import MenuBar
from tab_bar import TabBar
from main_body import MainBodyFrame
from sidebar import Sidebar
from tools import FileExplorerFrame, GrepFrame
# Other function imports
import gsconfig



class MainWindow(QMainWindow):
    def __init__(self):
        # CONFIG
        super(QMainWindow, self).__init__()
        self.app_title = "GS-Edit"
        self.app_icon = QIcon("./src/images/icon.png")
        self.setWindowIcon(self.app_icon)
        self.app_version = "0.1.0"
        self.initialize_window()
        self.current_file = None
        self.current_tool = "folder"

    def initialize_window(self):
        # window configuration
        self.setWindowTitle(self.app_title)
        self.resize(1400, 1000)
        # initialize styles
        self.setStyleSheet(open("./src/css/style.qss", "r").read())
        self.window_font = QFont("Consolas")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)
        self.configure_statusbar()
        self.configure_body()
        self.configure_menu()
        self.show()

    def configure_statusbar(self):
        self.bar = StatusBar()
        self.setStatusBar(self.bar)

    def configure_menu(self):
        top_menu_bar = MenuBar(self, self.bar, self.file_explorer_frame.file_explorer)
        self.setMenuBar(top_menu_bar)

    def text_editor(self, path=None, pyf=True) -> QsciScintilla:
        editor = TextEditor(self, path=path, pyf=pyf)
        return editor

    def valid_file_check(self, path):
        with open(path, 'rb') as f:
            return b'\0' in f.read(1024)

    def add_tab(self, path: Path, is_new_file=False):
        if not is_new_file and self.valid_file_check(path):
            self.statusBar().set_timed_message("Cannot open this file type", 2000)
            return
        if path.is_dir():
            return

        editor = self.text_editor(path, path.suffix in gsconfig.get_consideration("python"))
        if is_new_file:
            self.tab.addTab(editor, "untitled")
            self.setWindowTitle("untitled - " + self.app_title)
            self.statusBar().set_timed_message("untitled created", 2000)
            self.tab.setCurrentIndex(self.tab.count() - 1)
            self.current_file = None
            return

        for i in range(self.tab.count()):
            if self.tab.tabText(i) == path.name or self.tab.tabText(i) == "*" + path.name:
                self.tab.setCurrentIndex(i)
                self.current_file = path
                return

        self.tab.addTab(editor, path.name)

        if not is_new_file:
            editor.setText(path.read_text(encoding="utf-8"))
        self.setWindowTitle(path.name)
        self.current_file = path
        self.tab.setCurrentIndex(self.tab.count() - 1)
        self.statusBar().set_timed_message(f"{path.name} opened", 2000)

    def configure_body(self):
        # main body
        self.sidebar = Sidebar(self)
        self.horizontal_split = QSplitter(Qt.Horizontal)
        self.tab = TabBar(self, self.bar)
        self.file_explorer_frame = FileExplorerFrame(self)
        self.grep_frame = GrepFrame(self)
        self.horizontal_split.addWidget(self.file_explorer_frame)
        self.horizontal_split.addWidget(self.tab)
        main_body_frame = MainBodyFrame(self)
        self.setCentralWidget(main_body_frame)

    def finish_grep(self, content):
        self.grep_frame.grep_view.clear()
        for i in content:
            self.grep_frame.grep_view.addItem(i)

    def display_text(self, header, text):
        display = QMessageBox(self)
        display.setFont(self.font())
        display.font().setPointSize(16)
        display.setWindowTitle(header)
        display.setText(text)
        display.setWindowIcon(QIcon("./src/images/close.svg"))
        display.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        display.setDefaultButton(QMessageBox.No)
        display.setIcon(QMessageBox.Warning)

        return display.exec_()

    def close_current_tab(self, i):
        editor = self.tab.currentWidget()
        if editor.unsaved_changes:
            display = self.display_text("Close", "You have unsaved changes that will be lost if you do not save. Save now?")
            if display == QMessageBox.Yes:
                self.save()
        self.tab.removeTab(i)

    def grep_view_clicked(self, content: GrepListItem):
        self.add_tab(Path(content.path))
        editor = self.tab.currentWidget()
        editor.setCursorPosition(content.ln, content.endln)
        editor.setFocus()

    def file_explorer_context_menu(self, pos):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
