from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from pathlib import Path

from gsedit.text_editor import TextEditor
import gsedit.gsconfig

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

        title_label_unsaved = self.create_header_label("Unsaved Changes:")
        title_label_unsaved.setAlignment(Qt.AlignTop)
        self.addWidget(title_label_unsaved)

        self.list_widget_unsaved = QListWidget()
        self.list_widget_unsaved.setStyleSheet("background-color: #0c0f11; border: none; margin-bottom: -100px")
        self.addWidget(self.list_widget_unsaved)

        title_label_history = self.create_header_label("Edit History:")
        title_label_history.setAlignment(Qt.AlignTop)
        self.addWidget(title_label_history)

        self.list_widget_history = QListWidget()
        self.list_widget_history.setStyleSheet("background-color: #0c0f11; border: none;")
        self.addWidget(self.list_widget_history)

        self.list_widget_history.itemClicked.connect(self.open_version_tab)

    def create_header_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #c1c1c1;
                background-color: #101316;
                padding: 3px;
                border-radius: 3px;
                margin-left: 5px;
                margin-right: 5px;
                text-align: left;
            }
        """)
        return label

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
            if parts[1] == "changes" or parts[1] == "comparable":
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
        self.list_widget_unsaved.clear()
        self.list_widget_history.clear()

        for i in range(self.window.tab.count()):
            editor = self.window.tab.widget(i)
            if hasattr(editor, 'path') and not getattr(editor, 'is_historical', False):
                file_path = editor.abs_path if isinstance(editor.path, Path) else editor.path.path()
                if not os.path.exists(file_path):
                    continue

                diff = self.vc.get_difference(file_path)

                item = QListWidgetItem()
                widget = self.get_unsaved_widget(file_path, diff)
                item.setSizeHint(widget.sizeHint())
                self.list_widget_unsaved.addItem(item)
                self.list_widget_unsaved.setItemWidget(item, widget)

        self.update_edit_history()

    def update_edit_history(self):
        current_editor = self.window.tab.currentWidget()
        if current_editor and hasattr(current_editor, 'path') and not getattr(current_editor, 'is_historical', False):
            file_path = current_editor.abs_path if isinstance(current_editor.path, Path) else current_editor.path.path()
            history = self.vc.get_edit_history(file_path)
            for day, times in history.items():
                day_item = QListWidgetItem(day)
                day_item.setFlags(day_item.flags() & ~Qt.ItemIsSelectable)
                self.list_widget_history.addItem(day_item)
                for time, _ in times.items():
                    time_item = QListWidgetItem(time)
                    time_item.setData(Qt.UserRole, f"{file_path} {time}")
                    self.list_widget_history.addItem(time_item)

    def open_version_tab(self, item):
        data = item.data(Qt.UserRole)
        if data:
            file_path, time = data.split()
            version_title = f"{os.path.basename(file_path)} {time}"
            save_content = self.get_save_content(file_path, time)

            new_editor = TextEditor(self.window, path=Path(file_path), is_historical=True)
            new_editor.setText(save_content)
            self.window.tab.addTab(new_editor, version_title)
            self.window.tab.setCurrentWidget(new_editor)

    def get_save_content(self, file_path, time):
        saves = self.vc.get_saves(file_path)
        for timestamp, content in saves:
            if timestamp.endswith(time):
                return content
        return ""

    def create_editor_with_content(self, content):
        editor = TextEditor(self.window)
        editor.setText(content)
        return editor

    def get_current_file_path(self):
        editor = self.window.tab.currentWidget()
        if editor and hasattr(editor, 'path'):
            return editor.abs_path if isinstance(editor.path, Path) else editor.path.path()
        return None

    def print_unsaved_changes(self):
        current_file_path = self.get_current_file_path()
        if current_file_path:
            diff = self.vc.get_difference(current_file_path)
            unsaved_changes_text = self.get_unsaved_widget(current_file_path, diff)
            self.unsaved_list.addWidget(unsaved_changes_text)
        for i in range(self.window.tab.count()):
            editor = self.window.tab.widget(i)
            if hasattr(editor, 'path'):
                file_path = editor.abs_path if isinstance(editor.path, Path) else editor.path.path()
                diff = self.vc.get_difference(file_path)
                unsaved_changes_text = self.get_unsaved_widget(file_path, diff)
                self.unsaved_list.addWidget(unsaved_changes_text)
