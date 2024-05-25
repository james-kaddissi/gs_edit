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


import gsedit.gsconfig

from pathlib import Path

from gsedit.language_lexer import JavaScriptLexer, PythonLexer, CLexer, JSONLexer, RustLexer, CppLexer, HTMLLexer, CSSLexer, CSLexer, JavaLexer, TxtLexer, GoLexer, HaskellLexer, RubyLexer
from gsedit.code_completer import Completer


if TYPE_CHECKING:
    from gsedit.main import MainWindow # prevents circular imports
    from gsedit.version_control import VersionControlLayout

class TextEditor(QsciScintilla):
    def __init__(self, window, parent = None, path = None, pyf=None, cf=None, jsonf=None, rustf=None, cppf=None, jsf=None, htmlf=None, cssf=None, csf=None, javaf=None, txtf=None, gof=None, hsf=None, rbf=None, is_historical=False):
        super(TextEditor, self).__init__(parent)
        self.window = window
        self.vcl = self.window.vc_frame.vclayout
        self.is_historical = is_historical

        if self.is_historical:
            if isinstance(path, Path):
                path = str(path)
            self.path = QDir(path) if path else QDir("Untitled")
            self.file_path = QDir.toNativeSeparators(self.path.path()) if path else "New File"
            self.abs_path = self.path.absolutePath()
        else:
            self.path = path if path else Path("Untitled")
            self.file_path = str(self.path) if path else "New File"
            self.abs_path = str(self.path.resolve())

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

        self.vc = self.window.get_version_control()
        QTimer.singleShot(10, self.save_initial_version) 
        self.initializing = True
        QTimer.singleShot(10, self.finalize_initialization)
    
    def finalize_initialization(self):
        self.initializing = False

    def save_initial_version(self):
        if self.path:
            initial_content = self.text()
            self.vc.add_save(self.path.as_posix(), initial_content)

    def save_version(self):
        if self.path:
            content = self.text()
            self.vc.add_save(self.path.as_posix(), content)
            self.unsaved_changes = False

    @property
    def unsaved_changes(self):
        return self._unsaved_changes
    
    @unsaved_changes.setter
    def unsaved_changes(self, i):
        ci = self.window.tab.currentIndex()
        current_tab_text = self.window.tab.tabText(ci)

        if i:
            if not current_tab_text.startswith("*"):
                self.window.tab.setTabText(ci, "*" + current_tab_text)
        else:
            if current_tab_text.startswith("*"):
                self.window.tab.setTabText(ci, current_tab_text[1:])

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
        super().keyPressEvent(e)
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
        
        
    def on_cursor_position_changed(self, ln, char):
        if self.pyf:
            self.code_completer.retrieve(ln + 1, char, self.text())
    
    def text_change(self):
        if not self.initializing:
            self.unsaved_changes = True
            current_text = self.text()
            self.vc.add_change(self.path.as_posix(), current_text)
        
    
    