'''
This is the main application of GS-Edit. Keeping this file organized is especially important. Try refactoring code into new files.
'''
# Python imports
import sys
import os
# PyQt imports (migration to PyQt6 should be a simple task for a future date)
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# Class imports
from gsedit.status_bar import StatusBar
from gsedit.menu_bar import MenuBar
from gsedit.tab_bar import TabBar
from gsedit.main_body import MainBodyFrame
from gsedit.sidebar import Sidebar
from gsedit.tools import FileExplorerFrame, GrepFrame
from gsedit.css_editor import CSSEditor
# Other function imports
import gsedit.gsconfig

class MainWindow(QMainWindow):
    def __init__(self):
        # CONFIG
        super(QMainWindow, self).__init__()
        self.app_title = "GS-Edit"
        self.app_icon = QIcon("./src/gsedit/images/icon.png")
        self.setWindowIcon(self.app_icon)
        self.app_version = "0.1.0"
        self.initialize_window()
        self.current_file = None
        self.current_tool = "folder"
        self.css_editor = CSSEditor(self)

    def initialize_window(self):
        # window configuration
        self.setWindowTitle(self.app_title)
        self.resize(1400, 1000)
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', 'style.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        self.window_font = QFont("Fixedsys")
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
        self.main_body_frame = MainBodyFrame(self)
        self.setCentralWidget(self.main_body_frame)

    def toggle_terminal(self):
        if self.main_body_frame.terminal_widget.isVisible():
            self.main_body_frame.terminal_widget.hide()
        else:
            self.main_body_frame.terminal_widget.show()

    def open_css_editor(self):
        self.css_editor.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
