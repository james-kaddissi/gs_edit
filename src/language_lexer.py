import builtins
import keyword
import re
import types
import json

from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import gsconfig

'''LOGOS is a Rust library for lexers that is SIGNIFICANTLY faster than this abomination. When expanding to Rust, DO THIS FIRST!'''

class GSLexer(QsciLexerCustom):
    def __init__(self, language, editor, path=None, base_config=None):
        super(GSLexer, self).__init__(editor)
        self.editor = editor
        self.language = language
        if path != None:
            self.path = path
        else:
            self.path = "./active-theme.json"
        
        self.tokens: list[str, str] = []
        self.keywords = []
        self.saved_names = []
        if base_config is None:
            base_config = {}
            base_config["text-color"] = "#ffffff"
            base_config["background-color"] = "#0C0C1A"
            base_config["font-family"] = "Consolas"
            base_config["font-size"] = 14

        self.setDefaultColor(QColor(base_config["text-color"]))
        self.setDefaultPaper(QColor(base_config["background-color"]))
        self.setDefaultFont(QFont(base_config["font-family"], base_config["font-size"]))
        
        self._generateThemeItems()
        self._generateTheme()

    def generateKeywords(self, keywords):
        self.keywords = keywords

    def generateSavedNames(self, saved_names):
        self.saved_names = saved_names

    def _generateThemeItems(self):
        self.DEFAULT = 0
        self.KEYWORD = 1
        self.TYPES = 2
        self.STRING = 3
        self.KEYARGS = 4
        self.BRACKETS = 5
        self.COMMENTS = 6
        self.CONSTANTS = 7
        self.FUNCTIONS = 8
        self.CLASSES = 9
        self.FUNCTION_DEF = 10
        self.items = [
            "default",
            "keyword",
            "types",
            "string",
            "keyargs",
            "brackets",
            "comments",
            "constants",
            "functions",
            "classes",
            "function_def"
        ]

        self.available_weights = {
            "thin": QFont.Thin,
            "light": QFont.Light,
            "extraLight": QFont.ExtraLight,
            "normal": QFont.Normal,
            "medium": QFont.Medium,
            "demiBold": QFont.DemiBold,
            "bold": QFont.Bold,
            "extraBold": QFont.ExtraBold,
            "black": QFont.Black
        }

    def _generateTheme(self):
        with open(self.path, "r") as file:
            self.theme = json.load(file)

        syntax_rules = self.theme["active-theme"]["syntax-rules"]

        for i in syntax_rules:
            item = list(i.keys())[0]

            if item not in self.items:
                print(f"You're trying to style for a type that doesn't exist. {item} is not valid!")
                continue
            self.setColor(QColor(i[item]["text-color"]), getattr(self, item.upper()))
            self.setPaper(QColor(i[item]["page-color"]), getattr(self, item.upper()))
            self.setFont(QFont(
                i[item]["font-family"],
                i[item]["font-size"],
                self.available_weights.get(i[item]["font-weight"], QFont.Normal),
                i[item]["italic"],
            ))

        
    def get_lang(self):
        return self.language
    
    def description(self, style: int) -> str:
        if style == self.DEFAULT:
            return "DEFAULT"
        elif style == self.KEYWORD:
            return "KEYWORD"
        elif style == self.TYPES:
            return "TYPES"
        elif style == self.STRING:
            return "STRING"
        elif style == self.KEYARGS:
            return "KEYARGS"
        elif style == self.BRACKETS:
            return "BRACKETS"
        elif style == self.COMMENTS:
            return "COMMENTS"
        elif style == self.CONSTANTS:
            return "CONSTANTS"
        elif style == self.FUNCTIONS:
            return "FUNCTIONS"
        elif style == self.CLASSES:
            return "CLASSES"
        elif style == self.FUNCTION_DEF:
            return "FUNCTION_DEF"

        return ""
    
    def get_token(self, text):
        processed = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")
        self.tokens =  [ (token, len(bytearray(token, "utf-8"))) for token in processed.findall(text)]

    def get_next_token(self, jmp = None):
        if len(self.tokens) > 0:
            if jmp is not None and jmp != 0:
                for _ in range(jmp-1):
                    if len(self.tokens) > 0:
                        self.tokens.pop(0)
            return self.tokens.pop(0)
        else:
            return None

    def see_next(self, i=0):
        try:
            return self.tokens[i]
        except IndexError:
            return ['']

    def space_jump(self, jmp=None):
        i = 0
        token = " "
        if jmp is not None:
            i = jmp
        while token[0].isspace():
            token = self.see_next(i)
            i += 1
        return token, i
        

class PythonLexer(GSLexer):

    def __init__(self, editor):
        super(PythonLexer, self).__init__("Python", editor)
        self.editor = editor
        self.generateKeywords(keyword.kwlist)
        self.generateSavedNames([a for a, b in vars(builtins).items() if isinstance(b, types.BuiltinFunctionType)])

    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]

        self.get_token(active_text)

        is_string = False
        is_comment = False

        if ipos > 0:
            style = self.editor.SendScintilla(self.editor.SCI_GETSTYLEAT, ipos - 1)
            if style == 6:
                is_comment = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token = active_token[0]
            token_length= active_token[1]

            if is_comment:
                self.setStyling(token_length, 6)
                if token.startswith("\n"):
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, 3)
                if token == '"' or token == "'":
                    is_string = False
                continue

            if token == "class":
                act, x = self.space_jump()
                t, _ = self.space_jump(x)
                if act[0].isidentifier() and t[0] in (":", "("):
                    self.setStyling(token_length, 1)
                    _ = self.get_next_token(x)
                    self.setStyling(act[1]+1, 9)
                    continue
                else:
                    self.setStyling(token_length, 1)
                    continue
            elif token == "def":
                act, x = self.space_jump()
                if act[0].isidentifier():
                    self.setStyling(token_length, 1)
                    _ = self.get_next_token(x)
                    self.setStyling(act[1]+1, 10)
                    continue
                else:
                    self.setStyling(token_length, 1)
                    continue
            elif token in self.keywords:
                self.setStyling(token_length, 1)
            elif token.strip() == "." and self.see_next()[0].isidentifier():
                self.setStyling(token_length, 0)
                active_token = self.get_next_token()
                token = active_token[0]
                token_length = active_token[1]
                if self.see_next()[0] == "(":
                    self.setStyling(token_length, 8)
                else:
                    self.setStyling(token_length, 0)
                continue
            elif token.isnumeric() or token == 'self':
                self.setStyling(token_length, 7)
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, 5)
            elif token == '"' or token == "'":
                self.setStyling(token_length, 3)
                is_string = True
            elif token == "#":
                self.setStyling(token_length, 6)
                is_comment = True
            elif token in self.saved_names or token in ['+', '-', '*', '/', '%', '=', '<', '>']:
                self.setStyling(token_length, 2)
            else:
                self.setStyling(token_length, 0)
    