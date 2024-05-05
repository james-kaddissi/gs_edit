from difflib import HtmlDiff
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import *
import pkgutil
import keyword

from gsedit import vc

import gsedit.gsconfig

from pathlib import Path

from gsedit.language_lexer import JavaScriptLexer, PythonLexer, CLexer, JSONLexer, RustLexer, CppLexer, HTMLLexer, CSSLexer, CSLexer, JavaLexer, TxtLexer, GoLexer, HaskellLexer, RubyLexer
from gsedit.code_completer import Completer
from gsedit.version_control import VersionControlLayout


if TYPE_CHECKING:
    from gsedit.main import MainWindow # prevents circular imports

class TextEditor(QsciScintilla):
    def __init__(self, window, parent = None, path = None, pyf=None, cf=None, jsonf=None, rustf=None, cppf=None, jsf=None, htmlf=None, cssf=None, csf=None, javaf=None, txtf=None, gof=None, hsf=None, rbf=None):
        super(TextEditor, self).__init__(parent)
        self.window = window
        self.vcl = self.window.vc_frame.vclayout
        self.path = path
        self.abs_path = self.path.absolute()
        self.pyf = pyf
        self.cf = cf
        self.jsonf = jsonf
        self.rustf = rustf
        self.cppf = cppf
        self.jsf = jsf
        self.htmlf = htmlf
        self.cssf = cssf
        self.csf = csf
        self.javaf = javaf
        self.txtf = txtf
        self.gof = gof
        self.hsf = hsf
        self.rbf = rbf
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

        self.setCaretForegroundColor(QColor("#5ad8b2"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#121621"))

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
        elif self.jsf:
            self.lexer = JavaScriptLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.htmlf:
            self.lexer = HTMLLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.cssf:
            self.lexer = CSSLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.csf:
            self.lexer = CSLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.javaf:
            self.lexer = JavaLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.txtf:
            self.lexer = TxtLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.gof:
            self.lexer = GoLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.hsf:
            self.lexer = HaskellLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        elif self.rbf:
            self.lexer = RubyLexer(self)
            self.lexer.setDefaultFont(self.window_font)
            self.api = QsciAPIs(self.lexer)
            self.code_completer = Completer(self.abs_path, self.api)
            self.setLexer(self.lexer)
        else:
            self.setPaper(QColor(gsedit.gsconfig.get_color("primary-background")))
            self.setColor(QColor(gsedit.gsconfig.get_color("primary-text")))


        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#7a7e82"))
        self.setMarginsBackgroundColor((QColor("#101316")))
        self.setMarginsFont(self.window_font)

        self.vcdb = vc.create_version_control()
        self.save_initial_version()
    
    def save_initial_version(self):
        if self.path:
            initial_content = self.text()
            self.vcdb.save_version(self.path.as_posix(), initial_content)
    
    def print_edit_history(self):
        if self.path:
            try:
                history = self.vcdb.get_full_history(self.path.as_posix())
                print(f"Edit History for {self.path.name}:")
                for index, version in enumerate(history):
                    print(f"Version {index + 1}:\n{version}\n{'-' * 40}")
            except Exception as e:
                print(f"Failed to retrieve history: {str(e)}")

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

    def get_unsaved_changes(self):
        current_text = self.text()

        initial_content = self.vcdb.get_initial_version(self.path.as_posix())
        if initial_content != current_text:
            return current_text
        else:
            return None

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
        self.vcdb.save_version(self.path.as_posix(), self.text())
        self.vcl.update_changes()
        
    
    