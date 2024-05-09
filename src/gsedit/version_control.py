from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os


class VersionControlLayout(QVBoxLayout):
    def __init__(self, window):
        super(VersionControlLayout, self).__init__()
        self.window = window
        self.editor = self.window.tab.currentWidget()
        self.vc = self.window.get_version_control()
        self.initialize_layout()

    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        title_label = QLabel("Unsaved Changes:")
        self.addWidget(title_label)

        self.unsaved_changes_text = QPlainTextEdit()
        self.unsaved_changes_text.setReadOnly(True)
        self.addWidget(self.unsaved_changes_text)

        self.print_unsaved_changes()

    def update_changes(self):
        self.editor = self.window.tab.currentWidget()
        if self.editor:
            self.print_unsaved_changes()
        else:
            self.unsaved_changes_text.setPlainText("No file selected")

    def print_unsaved_changes(self):
        self.unsaved_changes_text.setPlainText(self.window.get_version_control().get_full_hisotry())
