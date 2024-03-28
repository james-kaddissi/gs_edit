from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class MainBodyLayout(QHBoxLayout):
    def __init__(self, window) -> None:
        super(MainBodyLayout, self).__init__()
        self.window = window
        self.initialize_layout()

    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.addWidget(self.window.sidebar)
        self.addWidget(self.window.horizontal_split)

class MainBodyFrame(QFrame):
    def __init__(self, window) -> None:
        super(MainBodyFrame, self).__init__()
        self.window = window
        self.initialize_frame()
        self.set_layout()

    def initialize_frame(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setContentsMargins(0, 0, 0, 0,)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_layout(self):
        self.setLayout(MainBodyLayout(self.window))
        