from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import os

class StatusBar(QStatusBar):
    def __init__(self) -> None:
        super(StatusBar, self).__init__()
        self.refresh_style()
        self.set_timed_message("GS-Edit started successfully!", 3000)

    def refresh_style(self):
        base_path = os.path.dirname(__file__) 
        style_sheet_path = os.path.join(base_path, 'css', 'statusBar.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

    def set_timed_message(self, message, time):
        self.showMessage(message, time)
