from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import *

import pkgutil
import keyword

import gsconfig

from pathlib import Path

from language_lexer import PythonLexer, CLexer, JSONLexer, RustLexer, CppLexer
from code_completer import Completer


if TYPE_CHECKING:
    from main import MainWindow # prevents circular imports

class TextEditor(QsciScintilla):
    def __init__(self, window, parent = None, path = None, pyf=None, cf=None, jsonf=None, rustf=None, cppf=None):
        super(TextEditor, self).__init__(parent)
        self.window = window
        self.path = path
        self.abs_path = self.path.absolute()
        self.pyf = pyf
        self.cf = cf
        self.jsonf = jsonf
        self.rustf = rustf
        self.cppf = cppf
        self.setUtf8(True)

        self.window_font = QFont("Fire Code")
        self.window_font.setPointSize(12)

        self.setFont(self.window_font)
        
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.textChanged.connect(self.text_change)

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)

        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        self.setCaretForegroundColor(QColor("#dedcdc"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#2c312d"))

        self.setEolMode(QsciScintilla.EolWindows)
        self.setEolVisibility(False)

        self._unsaved_changes = False
        self.first_access = True

        # syntax highlighting
        self.lexer = PythonLexer(self)
        self.lexer.setDefaultFont(self.window_font)

        if self.pyf:
            self.lexer = PythonLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.cf:
            self.lexer = CLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.jsonf:
            self.lexer = JSONLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.rustf:
            self.lexer = RustLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.cppf:
            self.lexer = CppLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        else:
            self.setPaper(QColor(gsconfig.get_color("primary-background")))
            self.setColor(QColor(gsconfig.get_color("primary-text")))


        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsForegroundColor(QColor("white"))
        self.setMarginsBackgroundColor((QColor("#0C0C1A")))
        self.setMarginsFont(self.window_font)
    
    @property
    def unsaved_changes(self):
        return self._unsaved_changes
    
    @unsaved_changes.setter
    def unsaved_changes(self, i):
        ci = self.window.tab.currentIndex()
        if i:
            self.window.tab.setTabText(ci, "*"+self.path.name)
            self.window.setWindowTitle(f"*{self.path.name} - {self.window.app_title}")
        else:
            if self.window.tab.tabText(ci).startswith("*"):
                self.window.tab.setTabText(ci, self.window.tab.tabText(ci)[1:])
                self.window.tab.setWindowTitle(self.window.windowTitle()[1:])
        self._unsaved_changes = i

    def comment_shortcut(self, txt):
        sep = txt.split('\n')
        sep.pop()
        clines = []
        for i in sep:
            if i.startswith('#'):
                clines.append(i.lstrip().replace("# ", "", 1))
            else:
                clines.append("# "+ i)
        clines.append("")
        return '\n'.join(clines)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Space:
            if self.pyf:
                cursor_position = self.getCursorPosition()
                self.code_completer.retrieve(cursor_position[0] + 1, cursor_position[1], self.text())
                self.autoCompleteFromAPIs()
                return
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_X: # Ctrl + X
            if not self.hasSelectedText():
                i, j = self.getCursorPosition()
                self.setSelection(i, 0, i, self.lineLength(i))
                self.cut()
                return
        if e.modifiers() == Qt.ControlModifier and e.text() == "/": # Ctrl + /
            if self.hasSelectedText():
                i, j, k, l = self.getSelection()
                self.setSelection(i, 0, k, self.lineLength(k)) 
                selected_text = self.selectedText()
                new_text = self.comment_shortcut(selected_text) 

                adjustment = 2 if selected_text[0] != "#" else -2  

                self.replaceSelectedText(new_text)
                self.setSelection(i, j, k, l + adjustment) 
            else:
                i, j = self.getCursorPosition()
                self.setSelection(i, 0, i, self.lineLength(i))
                self.replaceSelectedText(self.comment_shortcut(self.selectedText()))
                self.setSelection(-1, -1, -1, -1)
                self.setCursorPosition(i, j)
            return    
        return super().keyPressEvent(e)
        
    def on_cursor_position_changed(self, ln, char):
        if self.pyf:
            self.code_completer.retrieve(ln + 1, char, self.text())

    def text_change(self):
        if not self.unsaved_changes and not self.first_access:
            self.unsaved_changes = True
        if self.first_access:
            self.first_access = False
    
    