from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

from gsedit.file_explorer import FileExplorer, FileExplorerLayout
from gsedit.version_control import VersionControlLayout
from gsedit.grep import GrepLayout, Searchbar, GrepToggle, GrepResult
from gsedit.grepgine import Grepgine

class GeneralToolFrame(QFrame):
    def __init__(self) -> None:
        super(GeneralToolFrame, self).__init__()
        self.initialize_frame(200, 400)
        self.refresh_style()
    
    def initialize_frame(self, minimum, maximum) -> QFrame:
        self.setMaximumWidth(maximum)
        self.setMinimumWidth(minimum)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setContentsMargins(0, 0, 0, 0)

    def refresh_style(self):
        base_path = os.path.dirname(__file__) 
        style_sheet_path = os.path.join(base_path, 'css', 'tools.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

class FileExplorerFrame(GeneralToolFrame):
    def __init__(self, window) -> None:
        super(FileExplorerFrame, self).__init__()
        self.window = window
        self.file_explorer_layout = FileExplorerLayout()
        self.file_explorer = FileExplorer(tab=self.window.tab, add_tab=self.window.grep_frame.grep_view.add_tab, window=self.window)
        self.file_explorer_layout.addWidget(self.file_explorer)
        self.setLayout(self.file_explorer_layout)

class GrepFrame(GeneralToolFrame):
    def __init__(self, window) -> None:
        super(GrepFrame, self).__init__()
        self.window = window
        grep_layout = GrepLayout()
        grep_result = Searchbar(self.window)
        self.grep_box = GrepToggle(self.window)
        self.grepgine = Grepgine()
        self.grep_view = GrepResult(self.window)
        self.grepgine.final_result.connect(self.grep_view.finish_grep)
        grep_result.textChanged.connect(
            lambda x: self.grepgine.modify(
                x,
                self.window.file_explorer_frame.file_explorer.file_system_model.rootDirectory().absolutePath(),
                self.grep_box.isChecked()
            )
        )
        grep_layout.addWidget(self.grep_box)
        grep_layout.addWidget(grep_result)
        grep_layout.addSpacerItem(QSpacerItem(4, 4, QSizePolicy.Minimum, QSizePolicy.Minimum))
        grep_layout.addWidget(self.grep_view)

        self.setLayout(grep_layout)
    
class VersionControlFrame(GeneralToolFrame):
    def __init__(self, window) -> None:
        super(VersionControlFrame, self).__init__()
        self.window = window
        self.vclayout = VersionControlLayout()       