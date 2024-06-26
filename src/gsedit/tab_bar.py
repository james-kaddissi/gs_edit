from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
from gsedit.popup import PopupMessage

class TabBar(QTabWidget):
    def __init__(self, main_window, status_bar) -> None:
        super(TabBar, self).__init__()
        self.window = main_window
        self.bar = status_bar
        self.refresh_style()
        self.initialize_tabs()
    
    def refresh_style(self):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', 'tabBar.qss')

        with open(style_sheet_path, "r") as style_file:
            style_content = style_file.read()

        icon_path = os.path.join(base_path, 'images', 'close.svg').replace('\\', '/')
        style_content = style_content.replace('url_placeholder', icon_path)

        self.setStyleSheet(style_content)


    def initialize_tabs(self):
        self.setUsesScrollButtons(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.close_current_tab)
    
    def close_current_tab(self, i):
        editor = self.window.tab.currentWidget()
        if editor.unsaved_changes:
            display = PopupMessage("Close", "You have unsaved changes that will be lost if you do not save. Save now?")
            if display == QMessageBox.Yes:
                self.window.save()
        self.window.tab.removeTab(i)