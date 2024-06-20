from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
import gsedit.gsconfig

class ThemeEditor(QMainWindow):
    def __init__(self, parent=None):
        super(ThemeEditor, self).__init__(parent)
        self.setWindowTitle("Theme Editor")
        self.resize(800, 600)
        self.window = parent

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)  
        self.tabs = QTabWidget()
        main_theme_tab = QWidget()
        lexer_theme_tab = QWidget()
        icon_theme_tab = QWidget()
        self.tabs.addTab(main_theme_tab, "Theme Overview")
        self.tabs.addTab(lexer_theme_tab, "Lexer Theme")
        self.tabs.addTab(icon_theme_tab, "Icon Theme")
        self.main_layout.addWidget(self.tabs)
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.refresh_style()

    def refresh_style(self):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', 'themeEditor.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
    
    def set_main_theme_tab(self):
        self.tabs.setCurrentIndex(0)

    def set_lexer_theme_tab(self):
        self.tabs.setCurrentIndex(1)

    def set_icon_theme_tab(self):
        self.tabs.setCurrentIndex(2)

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
            self.setStyleSheet(style_file.read())

class SidebarLayout(QVBoxLayout):
    def __init__(self, window) -> None:
        super(SidebarLayout, self).__init__()
        self.window = window
        self.initialize_layout()
        self.initialize_icons()
    
    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.setAlignment(Qt.AlignTop | Qt.AlignCenter)
    
    def initialize_icons(self):
        base_path = os.path.dirname(__file__)
        folder_icon_path = os.path.join(base_path, 'images', 'folder.svg')
        grep_icon_path = os.path.join(base_path, 'images', 'grep.svg')
        vc_icon_path = os.path.join(base_path, 'images', 'vc.svg')
        paint_icon_path = os.path.join(base_path, 'images', 'paint.svg')

        folder_icon = self.tool_bar_icon(folder_icon_path, "folder")
        grep_icon = self.tool_bar_icon(grep_icon_path, "grep")
        vc_icon = self.tool_bar_icon(vc_icon_path, "vc")
        paint_icon = self.tool_bar_icon(paint_icon_path, "paint")

        self.addWidget(folder_icon)
        self.addWidget(grep_icon)
        self.addWidget(vc_icon)
        self.addStretch()
        self.addWidget(paint_icon)

    def tool_bar_icon(self, path, id):
        label = ToolLabel(path, id, self.window)
        return label

class ToolLabel(QLabel):
    def __init__(self, path, id, window) -> None:
        super(ToolLabel, self).__init__()
        self.path = path
        self.id = id
        self.window = window
        self.isSelected = False
        self.initialize_label()
        self.theme_editor = ThemeEditor(self.window)

    def initialize_label(self):
        icon = QIcon(self.path)
        pixmap = icon.pixmap(QSize(40, 40))
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setFont(self.window.window_font)
        self.update_style()
        self.mousePressEvent = self.on_mouse_press
        self.enterEvent = self.on_mouse_enter
        self.leaveEvent = self.on_mouse_leave

    def update_style(self):
        if self.isSelected:
            self.setStyleSheet("background-color: #4e2132;border-left: 2px solid #5ad8b2; border-top: none; border-bottom: none; border-right: none;")
        else:
            self.setStyleSheet("background-color: none;")  

    def on_mouse_press(self, event):
        if self.id == "paint":
            self.show_command_menu()
            return
        self.isSelected = not self.isSelected 
        self.update_style()
        self.toolbar_toggle(self.id)
    
    def show_command_menu(self):
        menu = QMenu(self)
        theme = menu.addAction("Theme")
        theme.triggered.connect(self.theme_triggered)
        lexer = menu.addAction("Lexer Theme")
        lexer.triggered.connect(self.lexer_triggered)
        icon = menu.addAction("Icon Theme")
        icon.triggered.connect(self.icon_triggered)
        menu.exec_(QCursor.pos())

    def theme_triggered(self):
        self.theme_editor.show()
        self.theme_editor.set_main_theme_tab()
    def lexer_triggered(self):
        self.theme_editor.show()
        self.theme_editor.set_lexer_theme_tab()
    def icon_triggered(self):
        self.theme_editor.show()
        self.theme_editor.set_icon_theme_tab()


    def on_mouse_enter(self, event):
        if not self.isSelected:
            self.setStyleSheet("background-color: #ebcb8b;")
        super().enterEvent(event)

    def on_mouse_leave(self, event):
        self.update_style() 
        super().leaveEvent(event)

    def toolbar_toggle(self, tool):
        frame_map = {
            "folder": self.window.file_explorer_frame,
            "grep": self.window.grep_frame,
            "vc": self.window.vc_frame
        }

        selected_frame = frame_map.get(tool)

        if selected_frame is None:
            return  

        replace_preference = gsedit.gsconfig.get_preference("tools-preferences", "tool-replace")

        if replace_preference and self.window.current_tool is not None and self.window.current_tool != tool:
            current_frame = frame_map[self.window.current_tool]
            current_frame.hide()
            for widget in self.parent().children():
                if isinstance(widget, ToolLabel) and widget.id == self.window.current_tool:
                    widget.isSelected = False
                    widget.update_style()
        
        if selected_frame not in self.window.main_body_frame.horizontal_split.children():
            self.window.main_body_frame.horizontal_split.insertWidget(0, selected_frame)

        if self.isSelected:
            selected_frame.show()
        else:
            selected_frame.hide()

        if self.isSelected:
            self.window.current_tool = tool
        else:
            self.window.current_tool = None

