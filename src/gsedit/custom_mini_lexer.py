from PyQt5.QtGui import QColor, QFont
from PyQt5.Qsci import QsciScintilla
from gsedit.language_lexer import PythonLexer

class SimpleScintillaEditor(QsciScintilla):
    def __init__(self, theme_data, parent=None):
        super().__init__(parent)
        self.theme_data = theme_data
        self.setup_editor()

    def setup_editor(self):
        font = QFont("Fire Code")
        font.setPointSize(10)
        self.setFont(font)

        self.setText("""
# Sample code snippet
def hello_world():
    print("Hello, World!")
    
for i in range(10):
    if i % 2 == 0:
        print(f"Even number: {i}")
    else:
        print(f"Odd number: {i}")
""")

        self.lexer = PythonLexer(self)
        self.lexer.setDefaultFont(font)
        self.setLexer(self.lexer)
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#7a7e82"))
        self.setMarginsBackgroundColor(QColor(self.theme_data['active-theme']['syntax-rules'][0]['default']['page-color']))
        self.setMarginsFont(font)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)
        self.setCaretForegroundColor(QColor("#5ad8b2"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#121621"))
        self.setEolMode(QsciScintilla.EolWindows)
        self.setEolVisibility(False)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

    def keyPressEvent(self, e):
        super().keyPressEvent(e)

    def refreshLexer(self, theme_data):
        for i, rule in enumerate(theme_data['active-theme']['syntax-rules']):
            for key, value in rule.items():
                if 'text-color' in value:
                    color = QColor(value['text-color'])
                    self.lexer.setColor(color, i)









