from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
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
        self.setSpacing(10)

        title_label = self.create_header_label("Unsaved Changes:")
        self.addWidget(title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #0c0f11")
        self.scroll_area_widget_contents = QListWidget()
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.addWidget(self.scroll_area)

        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setMinimumHeight(200)

        history_title_label = self.create_header_label("Edit History:")
        self.addWidget(history_title_label)

        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setStyleSheet("background-color: #0c0f11")
        self.history_scroll_area_widget_contents = QListWidget()
        self.history_scroll_area.setWidget(self.history_scroll_area_widget_contents)
        self.addWidget(self.history_scroll_area)

        self.history_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.history_scroll_area.setMinimumHeight(200)

        self.history_scroll_area_widget_contents.itemClicked.connect(self.open_version_tab)

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
        self.scroll_area_widget_contents.clear()
        for i in range(self.window.tab.count()):
            editor = self.window.tab.widget(i)
            if hasattr(editor, 'path') and not getattr(editor, 'is_historical', False):
                file_path = editor.abs_path if isinstance(editor.path, Path) else editor.path.path()
                if not os.path.exists(file_path):
                    continue
                diff = self.vc.get_difference(file_path)
                item = QListWidgetItem(self.scroll_area_widget_contents)
                widget = self.get_unsaved_widget(file_path, diff)
                item.setSizeHint(widget.sizeHint())
                self.scroll_area_widget_contents.addItem(item)
                self.scroll_area_widget_contents.setItemWidget(item, widget)
        
        self.update_edit_history()

    def update_edit_history(self):
        self.history_scroll_area_widget_contents.clear()
        current_editor = self.window.tab.currentWidget()
        if current_editor and hasattr(current_editor, 'path') and not getattr(current_editor, 'is_historical', False):
            file_path = current_editor.abs_path if isinstance(current_editor.path, Path) else current_editor.path.path()
            history = self.vc.get_edit_history(file_path)
            for day, times in history.items():
                day_item = QListWidgetItem(day)
                day_item.setFlags(day_item.flags() & ~Qt.ItemIsSelectable)
                self.history_scroll_area_widget_contents.addItem(day_item)
                for time, _ in times.items():
                    time_item = QListWidgetItem(time)
                    time_item.setData(Qt.UserRole, f"{file_path} {time}")
                    self.history_scroll_area_widget_contents.addItem(time_item)

    def open_version_tab(self, item):
        data = item.data(Qt.UserRole)
        if data:
            file_path, time = data.split()
            version_title = f"{os.path.basename(file_path)} {time}"

            save_content = self.get_save_content(file_path, time)

            pyf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("python")))
            cf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("c")))
            jsonf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("json")))
            rustf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("rust")))
            cppf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("cpp")))
            jsf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("javascript")))
            htmlf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("html")))
            cssf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("css")))
            csf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("cs")))
            javaf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("java")))
            txtf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("text")))
            gof = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("go")))
            hsf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("haskell")))
            rbf = file_path.endswith(tuple(gsedit.gsconfig.get_consideration("ruby")))

            new_editor = TextEditor(self.window, path=Path(file_path), is_historical=True,
                                    pyf=pyf, cf=cf, jsonf=jsonf, rustf=rustf, cppf=cppf, jsf=jsf,
                                    htmlf=htmlf, cssf=cssf, csf=csf, javaf=javaf, txtf=txtf,
                                    gof=gof, hsf=hsf, rbf=rbf)
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
