from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

from gsedit import vc

class VersionControlLayout(QVBoxLayout):
    def __init__(self, window):
        super(VersionControlLayout, self).__init__()
        self.window = window
        self.editor = self.window.tab.currentWidget()
        self.vc = vc.VersionControl() 
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
        self.print_unsaved_changes()

    def print_unsaved_changes(self):
        if self.editor is not None:
            path = self.editor.file_path
            try:
                unsaved_changes = self.get_unsaved_changes(path)
                formatted_changes = self.format_changes(unsaved_changes)
                self.unsaved_changes_text.setPlainText(formatted_changes)
            except Exception as e:
                self.unsaved_changes_text.setPlainText(str(e))
        else:
            self.unsaved_changes_text.setPlainText("No file selected")

    def get_unsaved_changes(self, path):
        saved_version_id = self.editor.saved_version_id
        return self.vc.get_unsaved_changes(path, saved_version_id)

    def format_changes(self, changes):
        formatted_text = ""
        for change in changes:
            line = change['line']
            change_type = change['type']
            text = change['text']
            formatted_text += f"Line {line}: {change_type} -> {text}\n"
        return formatted_text if formatted_text else "No unsaved changes."