from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os

class IntegratedTerminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.layout = QVBoxLayout(self)
        self.output = QTextEdit(self, readOnly=True)
        self.input = QLineEdit(self)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.input.returnPressed.connect(self.execute_command)
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.process.start("cmd.exe" if os.name == 'nt' else "/bin/bash")

    def execute_command(self):
        command = self.input.text() + "\n"
        self.process.write(command.encode())
        self.input.clear()

    def onReadyReadStandardOutput(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output.append(data)
