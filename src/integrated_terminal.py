from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


import os

class IntegratedTerminalTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_style()
        self.setAcceptRichText(False)
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.ouput_triggered)
        self.process.readyReadStandardError.connect(self.error_output_triggered)
        self.process.start("cmd.exe" if os.name == 'nt' else "/bin/bash")
        self.is_command_executing = False
        self.command_start_position = self.textCursor().position()
        self.clicked = pyqtSignal()

    def refresh_style(self):
        self.setStyleSheet(open("./src/css/integratedTerminal.qss", "r").read())

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not self.is_command_executing:
            self.executeCommand()
        elif event.key() == Qt.Key_Backspace:
            if cursor.position() > self.command_start_position:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
            self.keep_cursor_in_command_line()

    def executeCommand(self):
        self.is_command_executing = True
        cursor = self.textCursor()
        cursor.setPosition(self.command_start_position, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        command = cursor.selectedText()
        if command:
            self.process.write((command + "\n").encode())
        else:
            self.command_start_position = self.textCursor().position()
        self.is_command_executing = False

    def ouput_triggered(self):
        data = self.process.readAllStandardOutput().data().decode().strip()
        if data:
            self.append_newline(data)
        self.command_start_position = self.textCursor().position()

    def error_output_triggered(self):
        data = self.process.readAllStandardError().data().decode().strip()
        if data:
            self.append_newline(data)
        self.command_start_position = self.textCursor().position()

    def append_newline(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        if not self.document().lastBlock().text() == "":
            self.insertPlainText("\n")
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def keep_cursor_in_command_line(self):
        if not self.is_command_executing:
            cursor = self.textCursor()
            if cursor.position() < self.command_start_position:
                cursor.setPosition(self.textCursor().position())
                self.setTextCursor(cursor)



class IntegratedTerminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        self.add_new_terminal_tab()
        self.refresh_style()


    def refresh_style(self):
        self.setStyleSheet(open("./src/css/integratedTerminal.qss", "r").read())

    def add_new_terminal_tab(self):
        splitter = QSplitter(Qt.Horizontal)
        terminal = IntegratedTerminalTextEdit()
        splitter.addWidget(terminal)
        self.tab_widget.addTab(splitter, "Terminal")

    def split_terminal_tab(self):
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, QSplitter):
            new_terminal = IntegratedTerminalTextEdit()
            current_widget.addWidget(new_terminal)

    def close_current_terminal(self):
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, QSplitter) and current_widget.count() > 1:
            current_widget.widget(current_widget.count() - 1).deleteLater()
