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
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.print_unsaved_changes)
        self.update_timer.start(100)

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

    def get_current_file_path(self):
        editor = self.window.tab.currentWidget()
        if editor and hasattr(editor, 'path'):
            return str(editor.path.as_posix())
        return None

    def print_unsaved_changes(self):
        current_file_path = self.get_current_file_path()
        if current_file_path:
            diff = self.vc.get_difference(current_file_path)
            self.unsaved_changes_text.setPlainText(diff)
        else:
            self.unsaved_changes_text.setPlainText("No file selected or no changes available.")
