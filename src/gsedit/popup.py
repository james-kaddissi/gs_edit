from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os

class PopupMessage(QMessageBox):
    def __init__(self, title, text) -> None:
        super(PopupMessage, self).__init__()
        self.title = title
        self.text = text
        self.initialize_popup()

    def initialize_popup(self):
        self.setFont(self.font())
        self.font().setPointSize(16)
        self.setWindowTitle(self.title)
        self.setText(self.text)
        image_path = os.path.join(os.path.dirname(__file__), 'images', 'close.svg')
        self.setWindowIcon(QIcon("./src/gsedit/images/close.svg"))
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        self.setIcon(QMessageBox.Warning)

        return self.exec_()