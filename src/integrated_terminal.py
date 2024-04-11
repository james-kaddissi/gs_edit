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

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        parent_widget = self.parent().parent().parent().parent()  
        if isinstance(parent_widget, IntegratedTerminal):
            parent_widget.update_active_terminal(self.parent().parent().currentIndex())

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
        self.splitter = QSplitter(Qt.Horizontal)
        self.tab_widget = QTabWidget()
        self.splitter.addWidget(self.tab_widget)
        self.layout.addWidget(self.splitter)
        self.active_terminal = self.tab_widget
        self.add_new_terminal_tab()
        self.tab_widget.currentChanged.connect(self.update_active_terminal)

    def add_new_terminal_tab(self):
        terminal = IntegratedTerminalTextEdit()
        self.active_terminal.addTab(terminal, "Terminal")
        index = self.tab_widget.indexOf(terminal)
        self.active_terminal.setCurrentIndex(index)


    def update_active_terminal(self, index):
        sender = self.sender()
        if isinstance(sender, QTabWidget):
            print(sender)
            self.active_terminal = sender
        
    def split_terminal_tab(self):
        new_tab_widget = QTabWidget()
        self.splitter.addWidget(new_tab_widget)

        if self.active_terminal.count() < 2:
            self.add_new_terminal_tab()

        for _ in range(self.active_terminal.count() // 2):
            terminal_widget = self.active_terminal.widget(0)
            terminal_index = self.active_terminal.indexOf(terminal_widget)
            self.active_terminal.removeTab(terminal_index)
            new_tab_widget.addTab(terminal_widget, "Terminal")
        
        self.active_terminal = new_tab_widget
        self.active_terminal.currentChanged.connect(self.update_active_terminal)
        self.active_terminal.tabBarClicked.connect(self.update_active_terminal)

        
    def close_current_terminal_tab(self):
        current_index = self.active_terminal.currentIndex()
        if current_index != -1:
            self.active_terminal.removeTab(current_index)
