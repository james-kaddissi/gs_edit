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
        self.icons = self.load_icons()
        self.initialize_layout()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_changes)
        self.update_timer.start(100)

    def load_icons(self):
        base_path = os.path.dirname(__file__)
        icons = {}
        icons['added'] = QPixmap(os.path.join(base_path, 'images', 'add_icon.png')).scaled(16, 16, Qt.KeepAspectRatio)
        icons['removed'] = QPixmap(os.path.join(base_path, 'images', 'remove_icon.png')).scaled(16, 16, Qt.KeepAspectRatio)
        icons['neutral'] = QPixmap(os.path.join(base_path, 'images', 'neutral_icon.png')).scaled(16, 16, Qt.KeepAspectRatio)
        return icons

    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        title_label = QLabel("Unsaved Changes:")
        title_label.setAlignment(Qt.AlignCenter)
        self.addWidget(title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #0c0f11")
        self.scroll_area_widget_contents = QListWidget()
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.addWidget(self.scroll_area)

        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setMinimumHeight(200)

    def get_unsaved_widget(self, filepath, diff):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        if "Added" in diff:
            icon_label.setPixmap(self.icons['added'])
        elif "Removed" in diff:
            icon_label.setPixmap(self.icons['removed'])
        else:
            icon_label.setPixmap(self.icons['neutral'])
        

        filename = os.path.basename(filepath)

        parts = diff.split() 
        if len(parts) > 1:
            if parts[1] =="changes" or parts[1] == "comparable":
                change_count = '0'
            else:
                change_count = parts[1] 
        else:
            change_count = '0'

        text_label = QLabel(f"{change_count} in {filename}")
        text_label.setAlignment(Qt.AlignVCenter)
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(icon_label)
        layout.addWidget(text_label)


        widget.setLayout(layout)
        widget.setMinimumHeight(45)
        return widget

    def update_changes(self):
        self.scroll_area_widget_contents.clear()  
        for i in range(self.window.tab.count()):
            editor = self.window.tab.widget(i)
            if hasattr(editor, 'path'):
                file_path = str(editor.path.as_posix())
                diff = self.vc.get_difference(file_path)
                item = QListWidgetItem(self.scroll_area_widget_contents)
                widget = self.get_unsaved_widget(file_path, diff)
                item.setSizeHint(widget.sizeHint())  
                self.scroll_area_widget_contents.addItem(item)
                self.scroll_area_widget_contents.setItemWidget(item, widget)



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
       