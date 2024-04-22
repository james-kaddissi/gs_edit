from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os

class Sidebar(QFrame):
    def __init__(self, window) -> None:
        super(Sidebar, self).__init__()
        self.window = window
        self.initialize_sidebar()
        self.refresh_style()
    
    def initialize_sidebar(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setLayout(SidebarLayout(self.window))

    def refresh_style(self):
        base_path = os.path.dirname(__file__)  
        style_sheet_path = os.path.join(base_path, 'css', 'sidebar.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read()) #collin smith

class SidebarLayout(QVBoxLayout):
    def __init__(self, window) -> None:
        super(SidebarLayout, self).__init__()
        self.window = window
        self.initialize_layout()
        self.initialize_icons()
    
    def initialize_layout(self):
        self.setContentsMargins(5, 10, 5, 0)
        self.setSpacing(0)
        self.setAlignment(Qt.AlignTop | Qt.AlignCenter)
    
    def initialize_icons(self):
        folder_icon = self.tool_bar_icon("./src/gsedit/images/folder.svg",  "folder")
        self.addWidget(folder_icon)
        grep_icon = self.tool_bar_icon("./src/gsedit/images/grep.svg", "grep")
        self.addWidget(grep_icon)

    def tool_bar_icon(self, path, id):
        label = ToolLabel(path, id, self.window)
        return label

class ToolLabel(QLabel):
    def __init__(self, path, id, window) -> None:
        super(ToolLabel, self).__init__()
        self.path = path
        self.id = id
        self.window = window
        self.isSelected = False  # Track if the label is selected
        self.initialize_label()

    def initialize_label(self):
        self.setPixmap(QPixmap(self.path).scaled(QSize(35, 35)))
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setFont(self.window.window_font)
        self.update_style()
        self.mousePressEvent = self.on_mouse_press
        self.enterEvent = self.on_mouse_enter
        self.leaveEvent = self.on_mouse_leave

    def update_style(self):
        if self.isSelected:
            self.setStyleSheet("background-color: #a3be8c;")
        else:
            self.setStyleSheet("background-color: none;")  

    def on_mouse_press(self, event):
        self.isSelected = not self.isSelected 
        self.update_style()
        self.toolbar_toggle(self.id)

    def on_mouse_enter(self, event):
        if not self.isSelected:
            self.setStyleSheet("background-color: #ebcb8b;")
        super().enterEvent(event)

    def on_mouse_leave(self, event):
        self.update_style() 
        super().leaveEvent(event)

    def toolbar_toggle(self, tool):
        if tool == "folder":
            if self.window.current_tool != "folder":
                self.window.horizontal_split.insertWidget(0, self.window.file_explorer_frame)
        elif tool == "grep":
            if self.window.current_tool != "grep":
                self.window.horizontal_split.insertWidget(0, self.window.grep_frame)

        if self.window.current_tool == tool:
            temp_frame = self.window.horizontal_split.widget(0)
            if temp_frame.isHidden():
                temp_frame.show()
            else:
                temp_frame.hide()
        self.window.current_tool = tool