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

    def configure_body(self):
        # main body
        self.sidebar = Sidebar(self)
        self.horizontal_split = QSplitter(Qt.Horizontal)
        self.tab = TabBar(self, self.bar)
        self.grep_frame = GrepFrame(self)
        self.file_explorer_frame = FileExplorerFrame(self)
        self.horizontal_split.addWidget(self.file_explorer_frame)
        self.horizontal_split.addWidget(self.tab)
        main_body_frame = MainBodyFrame(self)
        self.setCentralWidget(main_body_frame)


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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
