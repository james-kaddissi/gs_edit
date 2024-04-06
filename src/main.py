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
        self.main_body_frame = MainBodyFrame(self)
        self.setCentralWidget(self.main_body_frame)

    def toggle_terminal(self):
        if self.main_body_frame.terminal_widget.isVisible():
            self.main_body_frame.terminal_widget.hide()
        else:
            self.main_body_frame.terminal_widget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
