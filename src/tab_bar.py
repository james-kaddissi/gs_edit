from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
from pathlib import Path

import os

class TabBar(QTabWidget):
    def __init__(self, main_window, status_bar) -> None:
        super(TabBar, self).__init__()
        self.window = main_window
        self.bar = status_bar
        self.refresh_style()
        self.initialize_tabs()
    
    def refresh_style(self):
        self.setStyleSheet(open("./src/css/tabBar.qss", "r").read())

    def initialize_tabs(self):
        self.setUsesScrollButtons(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.window.close_current_tab)