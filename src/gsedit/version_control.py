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
        self.update_timer.timeout.connect(self.update_changes)
        self.update_timer.start(100)

    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        title_label = QLabel("Unsaved Changes:")
        self.addWidget(title_label)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.unsaved_list = QVBoxLayout(self.scroll_area_widget_contents)
        self.addWidget(self.scroll_area)

        self.update_changes()

    def get_unsaved_widget(self, filename, diff):
        widget = QHBoxLayout()
        icon_label = QLabel()
        # Process the diff string to determine the icon
        if "Added" in diff:
            base_path = os.path.dirname(__file__)  
            image_path = os.path.join(base_path, 'images', 'add_icon.png')
            icon = QIcon(image_path)
        elif "Removed" in diff:
            base_path = os.path.dirname(__file__)  
            image_path = os.path.join(base_path, 'images', 'remove_icon.png')
            icon = QIcon(image_path)
        else:
            base_path = os.path.dirname(__file__)  
            image_path = os.path.join(base_path, 'images', 'neutral_icon.png')
            icon = QIcon(image_path)
        icon_label.setPixmap(icon.pixmap(QSize(16, 16)))
        widget.addWidget(icon_label)

        text_label = QLabel(f"{filename}: {diff}")
        widget.addWidget(text_label)

        container_widget = QWidget()
        container_widget.setLayout(widget)
        return container_widget

    def update_changes(self):
        while self.unsaved_list.count():
            item = self.unsaved_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for i in range(self.window.tab.count()):
            editor = self.window.tab.widget(i)
            if hasattr(editor, 'path'):
                file_path = str(editor.path.as_posix())
                diff = self.vc.get_difference(file_path)
                unsaved_widget = self.get_unsaved_widget(file_path, diff)
                self.unsaved_list.addWidget(unsaved_widget)
    def get_current_file_path(self):
        editor = self.window.tab.currentWidget()
        if editor and hasattr(editor, 'path'):
            return str(editor.path.as_posix())
        return None

    def print_unsaved_changes(self):
        current_file_path = self.get_current_file_path()
        if current_file_path:
            diff = self.vc.get_difference(current_file_path)
            unsaved_changes_text = self.get_unsaved_widget(current_file_path, diff)
            self.unsaved_list.addWidget(unsaved_changes_text)
        for i in range(self.window.tab.count()):
            diff = self.vc.get_difference(self.window.tab.widget(i).path)
            unsaved_changes_text = self.get_unsaved_widget(self.window.tab.widget(i).path, diff)
            self.unsaved_list.addWidget(unsaved_changes_text)
       