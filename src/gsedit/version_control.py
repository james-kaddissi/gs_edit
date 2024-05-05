from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

from gsedit import vc

class VersionControlLayout(QVBoxLayout):
    def __init__(self, window) -> None:
        super(VersionControlLayout, self).__init__()
        self.window = window
        self.editor = self.window.tab.currentWidget()
        self.initialize_layout()

    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        title_label = QLabel("Unsaved Changes:")
        self.addWidget(title_label)

        self.unsaved_changes_text = QPlainTextEdit()
        self.unsaved_changes_text.setReadOnly(True)
        self.addWidget(self.unsaved_changes_text)

        self.vcdb = vc.create_version_control()

        self.print_unsaved_changes()

    def update_changes(self):
        self.editor = self.window.tab.currentWidget()
        self.print_unsaved_changes()

    def print_unsaved_changes(self):
        if self.editor != None:
            if self.editor.unsaved_changes:
                unsaved_changes = self.get_unsaved_changes()
                self.unsaved_changes_text.setPlainText(unsaved_changes)
            else:
                self.unsaved_changes_text.setPlainText("No unsaved changes.")

    def get_unsaved_changes(self):
        return self.editor.get_unsaved_changes()