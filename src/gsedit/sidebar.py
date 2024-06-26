from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pygame import Color
from qframelesswindow import FramelessMainWindow, TitleBar
from gsedit.top_bar import TopBarSmall
import gsedit.theme_editor
import os
import gsedit.gsconfig
class ColorPickerButton(QWidget):
    def __init__(self, parent=None):
        super(ColorPickerButton, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.color_label = QLabel(self)
        self.color_label.setText("Color Picker")
        self.color_label.setStyleSheet("background-color: red; color: white;")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setFixedSize(70, 30)
        font_size = 7 
        font = QFont()
        font.setPointSize(font_size)
        self.color_label.setFont(font)
        
        self.color_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.color_label.mousePressEvent = self.start_color_picker

    def start_color_picker(self, event):
        self.grabMouse()
        self.setCursor(Qt.CrossCursor)
        self.color_label.setText("Picking...")

    def mouseMoveEvent(self, event):
        screen = QApplication.primaryScreen()
        color = screen.grabWindow(QApplication.desktop().winId(), event.globalX(), event.globalY(), 1, 1).toImage().pixel(0, 0)
        color = QColor(color)
        hex_color = color.name()
        print(hex_color)
        self.color_label.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 5px;")
        self.color_label.setText(hex_color)
        self.update()

    def mousePressEvent(self, event):
        screen = QApplication.primaryScreen()
        color = screen.grabWindow(QApplication.desktop().winId(), event.globalX(), event.globalY(), 1, 1).toImage().pixel(0, 0)
        color = QColor(color)
        hex_color = color.name()
        clipboard = QApplication.clipboard()
        clipboard.setText(hex_color)
        self.releaseMouse()
        self.setCursor(Qt.ArrowCursor)
        self.color_label.setText(f"Copied: {hex_color}")
        self.color_label.setStyleSheet(f"background-color: {hex_color}; color: white;")

class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.minBtn.setHoverColor(Qt.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.minBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }""")
        
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)
        self.closeBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-normalColor: white;
                qproperty-normalBackgroundColor: transparent;
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: red;
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)

class ThemeInfoWidget(QWidget):
    def __init__(self, theme_data, parent=None):
        super(ThemeInfoWidget, self).__init__(parent)
        
        self.theme_data = theme_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel(f"Theme Name: {self.theme_data['active-theme']['theme-name']}")
        version_label = QLabel(f"Version: {self.theme_data['active-theme']['version']}")
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        page_color = QColor(self.theme_data['active-theme']['syntax-rules'][0]['default']['page-color'])
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, page_color)
        self.setPalette(palette)
        font_family = self.theme_data['active-theme']['syntax-rules'][0]['default']['font-family']
        font_label = QLabel(f"Font Family: {font_family}")
        layout.addWidget(font_label)
        for rule in self.theme_data['active-theme']['syntax-rules']:
            for key, value in rule.items():
                syntax_label = QLabel(f"{key.capitalize()}: example1 example2 example3")
                font = QFont()
                font.setFamily(value['font-family'])
                font.setPointSize(value['font-size'])
                font.setWeight(QFont.Normal if value['font-weight'] == "normal" else QFont.Bold)
                font.setItalic(value['italic'])
                font.setUnderline(value['underlined'])
                font.setStrikeOut(value['strikethrough'])
                
                syntax_label.setFont(font)
                
                text_color = QColor(value['text-color'])
                syntax_label.setStyleSheet(f"color: {text_color.name()};")
                
                layout.addWidget(syntax_label)
        
        self.setLayout(layout)

class ThemeEditor(FramelessMainWindow):
    def __init__(self, parent=None):
        super(ThemeEditor, self).__init__(parent)
        self.setWindowTitle("Theme Editor")
        self.resize(800, 600)
        self.mwindow = parent
        self.title_bar = CustomTitleBar(self)
        self.setTitleBar(self.title_bar)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        main_theme_tab = self.mainTab()
        
        self.main_layout.addWidget(main_theme_tab)
        
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.color_picker = ColorPickerButton()
        self.color_picker.setFixedSize(70, 30)
        self.color_picker.setStyleSheet("""margin: 0px; padding: 0px""")
        bottom_bar_layout.addWidget(self.color_picker, alignment=Qt.AlignBottom | Qt.AlignLeft)
        self.main_layout.addLayout(bottom_bar_layout)
        
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setLayout(self.main_layout)
        self.main_widget.setStyleSheet(self.refresh_style('mainWidgetThemeEditor'))
        self.setCentralWidget(self.main_widget)
        self.setStyleSheet(self.refresh_style('themeEditor'))

        self.titleBar.raise_()
        
    def mainTab(self):
        tab = QWidget()
        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        main_theme_list = QListWidget()
        main_theme_list.addItem("Current Theme")
        main_theme_list.addItem("Customize Current Theme")
        main_theme_list.addItem("Browse Themes")
        
        stack = QStackedWidget()
        stack.addWidget(ThemeInfoWidget(theme_data=gsedit.theme_editor.read_theme_file()))
        stack.addWidget(ColorPickerButton())
        stack.addWidget(QLabel("Browse Themes"))
        
        main_theme_list.currentRowChanged.connect(stack.setCurrentIndex)
        
        tab_layout.addWidget(main_theme_list)
        tab_layout.addWidget(stack)
        
        tab.setLayout(tab_layout)
        return tab
    
    def refresh_style(self, name):
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', name+'.qss')
        with open(style_sheet_path, "r") as style_file:
            return style_file.read()
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
    def lexer_triggered(self):
        self.theme_editor.show()
    def icon_triggered(self):
        self.theme_editor.show()


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

