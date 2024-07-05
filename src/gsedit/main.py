'''
This is the main application of GS-Edit. Keeping this file organized is especially important. Try refactoring code into new files.
'''
# Python imports
import sys
import os
# PyQt imports (migration to PyQt6 should be a simple task for a future date)
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# Class imports
from gsedit.status_bar import StatusBar
from gsedit.menu_bar import MenuBar
from gsedit.tab_bar import TabBar
from gsedit.main_body import MainBodyFrame
from gsedit.sidebar import Sidebar
from gsedit.tools import FileExplorerFrame, GrepFrame, VersionControlFrame
from gsedit.css_editor import CSSEditor
from gsedit.top_bar import TopBar
# Other function imports
import gsedit.gsconfig

from gsedit import vc

from qframelesswindow import FramelessMainWindow

class MainWindow(FramelessMainWindow):
    def __init__(self):
        # CONFIG
        super(QMainWindow, self).__init__()
        self.version_control = vc.VersionControl()
        self.app_title = "GS-Edit"
        self.app_icon = QIcon("./src/gsedit/images/icon.png")
        self.setWindowIcon(self.app_icon)
        self.app_version = "0.2.6"
        self.initialize_window()
        self.current_file = None
        self.current_tool = None
        self.css_editor = CSSEditor(self)
        self.center_window()

    def get_version_control(self):
        return self.version_control

    def initialize_window(self):
        # window configuration
        self.setWindowTitle(self.app_title)
        self.resize(1400, 1000)
        base_path = os.path.dirname(__file__)
        style_sheet_path = os.path.join(base_path, 'css', 'style.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        self.window_font = QFont("Consolas")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)
        self.configure_statusbar()
        self.configure_body()
        self.show()
    
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        print("WORK")

    def configure_statusbar(self):
        self.bar = StatusBar()
        self.setStatusBar(self.bar)

    def configure_body(self):
        # main body
        
        

        self.tab = TabBar(self, self.bar)
        self.tab.setStyleSheet(self.tab.styleSheet())
        self.grep_frame = GrepFrame(self)
        self.file_explorer_frame = FileExplorerFrame(self)
        self.sidebar = Sidebar(self)
        self.vc_frame = VersionControlFrame(self)
        
        self.top_bar = TopBar(self)
        self.top_bar.setStyleSheet(self.top_bar.styleSheet() + "border: none; border-bottom: 1px solid #333641; border-bottom-left-radius: 0; border-bottom-right-radius: 0;")
        self.main_body_frame = MainBodyFrame(self)
        self.setCentralWidget(self.main_body_frame)
        self.file_explorer_frame.hide()
        self.grep_frame.hide()

    def toggle_terminal(self):
        if self.main_body_frame.terminal_widget.isVisible():
            self.main_body_frame.terminal_widget.hide()
        else:
            self.main_body_frame.terminal_widget.show()

    def open_css_editor(self):
        self.css_editor.show()



if __name__ == '__main__':
    print("Yo")
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    window = MainWindow()
    app.installEventFilter(window.top_bar)
    sys.exit(app.exec())
