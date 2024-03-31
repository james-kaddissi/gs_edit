from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from integrated_terminal import IntegratedTerminal



class MainBodyFrame(QFrame):
    def __init__(self, window) -> None:
        super(MainBodyFrame, self).__init__()
        self.refresh_style()
        self.window = window
        self.initialize_frame()
        self.set_layout()

    def refresh_style(self):
        self.setStyleSheet(open("./src/css/mainBody.qss", "r").read())

    def initialize_frame(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setContentsMargins(0, 0, 0, 0,)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_layout(self):
        layout = QVBoxLayout(self)
        self.vertical_split = QSplitter(Qt.Vertical)  # This splitter will manage the main content and the terminal
        
        self.editor_area = QWidget()  # Container for the main editor layout
        editor_layout = QHBoxLayout(self.editor_area)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.window.sidebar)
        editor_layout.addWidget(self.window.horizontal_split)
        
        self.terminal_widget = IntegratedTerminal(self)  
        
        # Add the editor area and the terminal to the vertical splitter
        self.vertical_split.addWidget(self.editor_area)
        self.vertical_split.addWidget(self.terminal_widget)
        layout.addWidget(self.vertical_split)
        
        self.terminal_widget.hide()  # Initially hide the terminal
        