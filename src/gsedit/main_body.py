from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from gsedit.integrated_terminal import IntegratedTerminal
import gsedit.gsconfig

import os

class MainBodyFrame(QFrame):
    def __init__(self, window) -> None:
        super(MainBodyFrame, self).__init__()
        self.window = window
        self.initialize_frame()
        self.set_layout()
        self.refresh_style()

    def refresh_style(self):
        base_path = os.path.dirname(__file__) 
        style_sheet_path = os.path.join(base_path, 'css', 'mainBody.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

    def initialize_frame(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_layout(self):
        
        if(gsedit.gsconfig.get_layout("terminal-span") == "full"):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.horizontal_split = QSplitter(Qt.Horizontal)
            self.horizontal_split.setHandleWidth(2)
            self.horizontal_split.addWidget(self.window.file_explorer_frame)
            self.horizontal_split.addWidget(self.window.tab)

            self.vertical_split = QSplitter(Qt.Vertical)
            self.vertical_split.setHandleWidth(2)  
            
            combined_widget = QWidget()
            combined_layout = QVBoxLayout(combined_widget)
            combined_layout.setContentsMargins(0, 0, 0, 0)
            combined_layout.setSpacing(0)
            
            combined_layout.addWidget(self.window.top_bar)
            self.editor_area = QWidget()
            editor_layout = QHBoxLayout(self.editor_area)
            editor_layout.setContentsMargins(0, 0, 0, 0)
            editor_layout.setSpacing(0)
            editor_layout.addWidget(self.window.sidebar)
            editor_layout.addWidget(self.horizontal_split)
            combined_layout.addWidget(self.editor_area)

            self.terminal_widget = IntegratedTerminal(self)
        
            self.vertical_split.addWidget(combined_widget)
            self.vertical_split.addWidget(self.terminal_widget)
            layout.addWidget(self.vertical_split)
            
            self.terminal_widget.hide()
        elif (gsedit.gsconfig.get_layout("terminal-span") == "editor"):
            self.horizontal_split = QSplitter(Qt.Horizontal)
            self.horizontal_split.setHandleWidth(2)
            self.horizontal_split.addWidget(self.window.file_explorer_frame)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.terminal_widget = IntegratedTerminal(self)
            self.vertical_split = QSplitter(Qt.Vertical)
            self.vertical_split.setHandleWidth(2)  
            
            combined_widget = QWidget()
            combined_layout = QVBoxLayout(combined_widget)
            combined_layout.setContentsMargins(0, 0, 0, 0)
            combined_layout.setSpacing(0)
            
            combined_layout.addWidget(self.window.top_bar)
            self.editor_area = QWidget()
            editor_layout = QHBoxLayout(self.editor_area)
            editor_layout.setContentsMargins(0, 0, 0, 0)
            editor_layout.setSpacing(0)
            self.window.sidebar.setFixedWidth(63) 
            editor_layout.addWidget(self.window.sidebar)

            self.vertical_split.addWidget(self.window.tab)
            self.vertical_split.addWidget(self.terminal_widget)
            self.horizontal_split.addWidget(self.vertical_split)
            editor_layout.addWidget(self.horizontal_split)
            combined_layout.addWidget(self.editor_area)  
            layout.addWidget(combined_widget)
            
            self.terminal_widget.hide()
        else:
            self.horizontal_split = QSplitter(Qt.Horizontal)
            self.horizontal_split.setHandleWidth(2)
            self.horizontal_split.addWidget(self.window.file_explorer_frame)
            self.horizontal_split.addWidget(self.window.tab)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.terminal_widget = IntegratedTerminal(self)
            self.vertical_split = QSplitter(Qt.Vertical)
            self.vertical_split.setHandleWidth(2)  
            
            combined_widget = QWidget()
            combined_layout = QVBoxLayout(combined_widget)
            combined_layout.setContentsMargins(0, 0, 0, 0)
            combined_layout.setSpacing(0)
            
            combined_layout.addWidget(self.window.top_bar)
            self.editor_area = QWidget()
            editor_layout = QHBoxLayout(self.editor_area)
            editor_layout.setContentsMargins(0, 0, 0, 0)
            editor_layout.setSpacing(0)
            self.window.sidebar.setFixedWidth(63) 
            editor_layout.addWidget(self.window.sidebar)
            self.vertical_split.addWidget(self.window.horizontal_split)
            self.vertical_split.addWidget(self.terminal_widget)
            editor_layout.addWidget(self.vertical_split)
            combined_layout.addWidget(self.editor_area)  
            layout.addWidget(combined_widget)
            
            self.terminal_widget.hide()