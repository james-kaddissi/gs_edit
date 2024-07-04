import builtins
import keyword
import re
import types
import json
import os

from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import gsedit.gsconfig


class GSLexer(QsciLexerCustom):
    def __init__(self, language, editor, path=None, base_config=None):
        super(GSLexer, self).__init__(editor)
        self.editor = editor
        self.language = language
        if path != None:
            self.path = path
        else:
            self.path = "./active-theme.json"
        base_path = os.path.dirname(__file__)
        config_path = os.path.join(base_path, 'active-theme.json')
        with open(config_path, "r") as file:
            self.theme = json.load(file)
        self.tokens: list[str, str] = []
        self.keywords = []
        self.saved_names = []
        if base_config is None:
            base_config = {}
            base_config["text-color"] = self.theme["active-theme"]["syntax-rules"][0]["default"]["text-color"]
            base_config["background-color"] = self.theme["active-theme"]["syntax-rules"][0]["default"]["page-color"]
            base_config["font-family"] = self.theme["active-theme"]["syntax-rules"][0]["default"]["font-family"]
            base_config["font-size"] = self.theme["active-theme"]["syntax-rules"][0]["default"]["font-size"]

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
        self.PREPROCESSOR = 11
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
            "function_def",
            "preprocessor"
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
        base_path = os.path.dirname(__file__)
        config_path = os.path.join(base_path, 'active-theme.json')
        with open(config_path, "r") as file:
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
        elif style == self.PREPROCESSOR:
            return "PREPROCESSOR"

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
        
class RustLexer(GSLexer):
    def __init__(self, editor):
        super(RustLexer, self).__init__("Rust", editor)
        self.editor = editor
        self.generateKeywords([
            "as", "break", "const", "continue", "crate", "else", "enum", "extern", "false",
            "fn", "for", "if", "impl", "in", "let", "loop", "match", "mod", "move", "mut", "pub",
            "ref", "return", "self", "Self", "static", "struct", "super", "trait", "true", "type",
            "unsafe", "use", "where", "while", "async", "await", "dyn"
        ])
        self.generateSavedNames([
            "Vec", "String", "HashMap", "Result", "Option", "println", "macro_rules"
        ])
    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_attribute = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if is_attribute:
                self.setStyling(token_length, self.KEYARGS) 
                if token.endswith("]"):
                    is_attribute = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue  # Consumes the line as a comment
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
                if token.startswith("["):
                    is_attribute = True
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit() or token.startswith("0x"):
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

class CppLexer(GSLexer):
    def __init__(self, editor):
        super(CppLexer, self).__init__("C++", editor)
        self.editor = editor
        self.generateKeywords([
            "auto", "bool", "break", "case", "catch", "char", "class", "const", "constexpr",
            "continue", "default", "delete", "do", "double", "else", "enum", "explicit", "export",
            "extern", "false", "float", "for", "friend", "goto", "if", "inline", "int", "long",
            "mutable", "namespace", "new", "noexcept", "nullptr", "operator", "private", "protected",
            "public", "register", "reinterpret_cast", "return", "short", "signed", "sizeof", "static",
            "struct", "switch", "template", "this", "throw", "true", "try", "typedef", "typeid",
            "typename", "union", "unsigned", "using", "virtual", "void", "volatile", "wchar_t", "while"
        ])
        self.generateSavedNames([
            "std", "cout", "cin", "vector", "string", "map", "set", "iostream"
        ])
    
    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_preprocessor = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/"):
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if is_preprocessor:
                self.setStyling(token_length, self.PREPROCESSOR)
                if token.startswith("\n"):
                    is_preprocessor = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token == "#":
                self.setStyling(token_length, self.PREPROCESSOR)
                is_preprocessor = True
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue  # Consumes the line as a comment
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)
    
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
    
class CLexer(GSLexer):
    def __init__(self, editor):
        super(CLexer, self).__init__("C", editor)
        self.editor = editor
        self.generateKeywords([
            "auto", "break", "case", "char", "const", "continue", "default", "do",
            "double", "else", "enum", "extern", "float", "for", "goto", "if", 
            "inline", "int", "long", "register", "restrict", "return", "short", 
            "signed", "sizeof", "static", "struct", "switch", "typedef", "union", 
            "unsigned", "void", "volatile", "while", "_Bool", "_Complex", "_Imaginary"
        ])
        self.generateSavedNames([
            "printf", "scanf", "strcpy", "strncpy", "strcat", "strncat", "malloc", 
            "free", "memset", "memcpy"
        ])

    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_preprocessor = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token = active_token[0]
            token_length= active_token[1]

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/"):
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token == '"' or token == "'":
                    is_string = False
                continue

            if is_preprocessor:
                self.setStyling(token_length, self.PREPROCESSOR)
                if token.startswith("\n"):
                    is_preprocessor = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token == "#":
                self.setStyling(token_length, self.PREPROCESSOR)
                is_preprocessor = True
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                # Eat up the rest of the line as a comment
                nxt_token, jmp = self.see_next(), 1
                while nxt_token[0] != "\n":
                    nxt_token, jmp = self.see_next(jmp), jmp + 1
                self.get_next_token(jmp) # Skip to the end of line
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token == '"' or token == "'":
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

class JavaScriptLexer(GSLexer):
    def __init__(self, editor):
        super(JavaScriptLexer, self).__init__("JavaScript", editor)
        self.generateKeywords([
            "break", "case", "catch", "class", "const", "continue", "debugger", "default", "delete",
            "do", "else", "export", "extends", "finally", "for", "function", "if", "import",
            "in", "instanceof", "let", "new", "return", "super", "switch", "this", "throw",
            "try", "typeof", "var", "void", "while", "with", "yield", "async", "await"
        ])
        self.generateSavedNames([
            "Array", "Date", "eval", "function", "hasOwnProperty", "Infinity", "isNaN", "isFinite", 
            "Number", "Object", "parseFloat", "parseInt", "String", "Boolean", "RegExp", "Error",
            "console", "window", "document"
        ])

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                self.skip_to_end_of_line()
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

    def skip_to_end_of_line(self):
        text = self.editor.text()
        pos = self.currentPosition
        while pos < len(text) and text[pos] != '\n':
            pos += 1
        self.setStyling(pos - self.currentPosition, self.COMMENTS)
        self.currentPosition = pos


class JSONLexer(GSLexer):
    def __init__(self, editor):
        super(JSONLexer, self).__init__("JSON", editor)
        self.generateSavedNames([
            "true",
            "false"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)
        is_string = False
        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            tok: str = curr_token[0]
            tok_len: int = curr_token[1]

            if is_string:
                self.setStyling(curr_token[1], self.STRING)
                if tok == '"' or tok == "'":
                    is_string = False
                continue
            elif tok.isnumeric():
                self.setStyling(tok_len, self.CONSTANTS)
                continue
            elif tok in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(tok_len, self.BRACKETS)
                continue
            elif tok == '"' or tok == "'":
                self.setStyling(tok_len, self.STRING)
                is_string = True
                continue
            elif tok in self.saved_names:
                self.setStyling(tok_len, self.TYPES)
                continue
            else:
                self.setStyling(tok_len, self.DEFAULT)

class HTMLLexer(GSLexer):
    def __init__(self, editor):
        super(HTMLLexer, self).__init__("HTML", editor)
        self.generateKeywords([
            "<!DOCTYPE", "<html", "<head", "<title", "<body", "<header", "<footer", 
            "<div", "<span", "<h1", "<h2", "<h3", "<h4", "<h5", "<h6", "<p", "<a", 
            "<img", "<table", "<tr", "<td", "<th", "<ul", "<li", "<ol", "<link", "<meta", 
            "<style", "<script"
        ])
        self.generateSavedNames([
            "class", "id", "href", "src", "alt", "rel", "type", "charset"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("-->"):
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token.startswith("<!--"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("</"):
                self.setStyling(token_length, self.KEYWORD)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token in self.saved_names:
                self.setStyling(token_length, self.KEYARGS)
            else:
                self.setStyling(token_length, self.DEFAULT)

class CSSLexer(GSLexer):
    def __init__(self, editor):
        super(CSSLexer, self).__init__("CSS", editor)
        self.generateKeywords([
            "color", "background", "border", "width", "height", "margin", "padding", 
            "font", "text", "display", "position", "top", "bottom", "left", "right",
            "align", "justify", "flex", "grid", "transition", "animation", "transform"
        ])
        self.generateSavedNames([
            "px", "em", "vh", "vw", "rem", "%", "inherit", "initial", "unset"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token == "*/":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token in self.saved_names:
                self.setStyling(token_length, self.CONSTANTS)
            else:
                self.setStyling(token_length, self.DEFAULT)

class CSLexer(GSLexer):
    def __init__(self, editor):
        super(CSLexer, self).__init__("C#", editor)
        self.generateKeywords([
            "abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "checked",
            "class", "const", "continue", "decimal", "default", "delegate", "do", "double",
            "else", "enum", "event", "explicit", "extern", "false", "finally", "fixed", "float",
            "for", "foreach", "goto", "if", "implicit", "in", "int", "interface", "internal",
            "is", "lock", "long", "namespace", "new", "null", "object", "operator", "out", 
            "override", "params", "private", "protected", "public", "readonly", "ref",
            "return", "sbyte", "sealed", "short", "sizeof", "stackalloc", "static",
            "string", "struct", "switch", "this", "throw", "true", "try", "typeof",
            "uint", "ulong", "unchecked", "unsafe", "ushort", "using", "virtual", "void",
            "volatile", "while"
        ])
        self.generateSavedNames([
            "Console", "Math", "DateTime", "List", "Dictionary", "HashSet", "String", "Integer", "Char"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False
        is_preprocessor = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token == "*/":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if is_preprocessor:
                self.setStyling(token_length, self.PREPROCESSOR)
                if token == "\n":
                    is_preprocessor = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("#"):
                self.setStyling(token_length, self.PREPROCESSOR)
                is_preprocessor = True
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.skip_to_end_of_line()
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

    def skip_to_end_of_line(self):
        text = self.editor.text()
        pos = self.currentPosition
        while pos < len(text) and text[pos] != '\n':
            pos += 1
        self.setStyling(pos - self.currentPosition, self.COMMENTS)
        self.currentPosition = pos
class JavaLexer(GSLexer):
    def __init__(self, editor):
        super(JavaLexer, self).__init__("Java", editor)
        self.generateKeywords([
            "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class",
            "const", "continue", "default", "do", "double", "else", "enum", "extends", "final",
            "finally", "float", "for", "if", "goto", "implements", "import", "instanceof", "int",
            "interface", "long", "native", "new", "package", "private", "protected", "public",
            "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this",
            "throw", "throws", "transient", "try", "void", "volatile", "while"
        ])
        self.generateSavedNames([
            "System", "Math", "String", "Integer", "Character", "Boolean", "Byte", "Double", "Float", "Long"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False
        is_annotation = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token == "*/":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if is_annotation:
                self.setStyling(token_length, self.PREPROCESSOR)
                if token == "\n":
                    is_annotation = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("@"):
                self.setStyling(token_length, self.PREPROCESSOR)
                is_annotation = True
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.skip_to_end_of_line()
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

    def skip_to_end_of_line(self):
        text = self.editor.text()
        pos = self.currentPosition
        while pos < len(text) and text[pos] != '\n':
            pos += 1
        self.setStyling(pos - self.currentPosition, self.COMMENTS)
        self.currentPosition = pos
class TxtLexer(GSLexer):
    def __init__(self, editor):
        super(TxtLexer, self).__init__("Text", editor)

    def styleText(self, start, end):
        self.startStyling(start)
        # For plain text, we do not apply any syntax highlighting.
        self.setStyling(end - start, self.DEFAULT)
class HaskellLexer(GSLexer):
    def __init__(self, editor):
        super(HaskellLexer, self).__init__("Haskell", editor)
        self.generateKeywords([
            "case", "class", "data", "default", "deriving", "do", "else", "if", "import",
            "in", "infix", "infixl", "infixr", "instance", "let", "module", "newtype", "of",
            "then", "type", "where", "_", "as", "qualified", "hiding"
        ])
        self.generateSavedNames([
            "Int", "Char", "Map", "Maybe", "Either", "List", "IO", "True", "False", "print", "putStrLn"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token == "-}":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token.startswith("{-"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token == "--":
                self.skip_to_end_of_line()
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit() or token in ["True", "False"]:
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

    def skip_to_end_of_line(self):
        text = self.editor.text()
        pos = self.currentPosition
        while pos < len(text) and text[pos] != '\n':
            pos += 1
        self.setStyling(pos - self.currentPosition, self.COMMENTS)
        self.currentPosition = pos

class GoLexer(GSLexer):
    def __init__(self, editor):
        super(GoLexer, self).__init__("Go", editor)
        self.generateKeywords([
            "break", "case", "chan", "const", "continue", "default", "defer", "else", "fallthrough",
            "for", "func", "go", "goto", "if", "import", "interface", "map", "package", "range",
            "return", "select", "struct", "switch", "type", "var"
        ])
        self.generateSavedNames([
            "fmt", "println", "print", "int", "string", "float64", "bool", "true", "false", "nil"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token == "*/":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.skip_to_end_of_line()
            elif token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit() or token in ["true", "false", "nil"]:
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

    def skip_to_end_of_line(self):
        text = self.editor.text()
        pos = self.currentPosition
        while pos < len(text) and text[pos] != '\n':
            pos += 1
        self.setStyling(pos - self.currentPosition, self.COMMENTS)
        self.currentPosition = pos

class RubyLexer(GSLexer):
    def __init__(self, editor):
        super(RubyLexer, self).__init__("Ruby", editor)
        self.generateKeywords([
            "BEGIN", "END", "alias", "and", "begin", "break", "case", "class", "def", "defined?",
            "do", "else", "elsif", "end", "ensure", "false", "for", "if", "in", "module", "next",
            "nil", "not", "or", "redo", "rescue", "retry", "return", "self", "super", "then",
            "true", "undef", "unless", "until", "when", "while", "yield"
        ])
        self.generateSavedNames([
            "Array", "Float", "Integer", "String", "nil?", "puts", "print", "p", "gets", "chomp", "join"
        ])

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text()[start:end]
        self.get_token(text)

        is_string = False
        is_comment = False
        is_symbol = False

        while True:
            curr_token = self.get_next_token()
            if curr_token is None:
                break
            token, token_length = curr_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token == "=end":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if is_symbol:
                self.setStyling(token_length, self.CONSTANTS)
                if token in [":"]:
                    is_symbol = False
                continue

            if token.startswith("=begin"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token == "#":
                self.skip_to_end_of_line()
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token == ":":
                self.setStyling(token_length, self.CONSTANTS)
                is_symbol = True
            elif token.isdigit() or token in ["true", "false", "nil"]:
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

    def skip_to_end_of_line(self):
        text = self.editor.text()
        pos = self.currentPosition
        while pos < len(text) and text[pos] != '\n':
            pos += 1
        self.setStyling(pos - self.currentPosition, self.COMMENTS)
        self.currentPosition = pos

class KotlinLexer(GSLexer):
    def __init__(self, editor):
        super(KotlinLexer, self).__init__("Kotlin", editor)
        self.editor = editor
        self.generateKeywords([
            "as", "break", "class", "continue", "do", "else", "false", "for", "fun", "if", "in", "interface",
            "is", "null", "object", "package", "return", "super", "this", "throw", "true", "try", "typealias",
            "val", "var", "when", "while", "by", "catch", "constructor", "delegate", "dynamic", "field",
            "file", "finally", "get", "import", "init", "param", "property", "receiver", "set", "setparam",
            "where"
        ])
        self.generateSavedNames([
            "Array", "Boolean", "Byte", "Char", "Double", "Float", "Int", "Long", "Short", "String", "println"
        ])

    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_kdoc = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_kdoc:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/"):
                    is_kdoc = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("/**"):
                    is_kdoc = True
                else:
                    is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)

class PHPLexer(GSLexer):
    def __init__(self, editor):
        super(PHPLexer, self).__init__("PHP", editor)
        self.editor = editor
        self.generateKeywords([
            "abstract", "and", "array", "as", "break", "callable", "case", "catch", "class", "clone", "const",
            "continue", "declare", "default", "do", "echo", "else", "elseif", "empty", "enddeclare", "endfor",
            "endforeach", "endif", "endswitch", "endwhile", "extends", "final", "for", "foreach", "function",
            "global", "goto", "if", "implements", "include", "include_once", "instanceof", "insteadof", "interface",
            "isset", "list", "namespace", "new", "or", "print", "private", "protected", "public", "require",
            "require_once", "return", "static", "switch", "throw", "trait", "try", "unset", "use", "var", "while", "xor"
        ])
        self.generateSavedNames([
            "__construct", "__destruct", "__call", "__callStatic", "__get", "__set", "__isset", "__unset", "__sleep",
            "__wakeup", "__toString", "__invoke", "__set_state", "__clone", "__debugInfo"
        ])

    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_php = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token == "<?php":
                self.setStyling(token_length, self.KEYWORD)
                is_php = True
                continue

            if is_php:
                if token in self.keywords:
                    self.setStyling(token_length, self.KEYWORD)
                elif token.startswith("/*"):
                    self.setStyling(token_length, self.COMMENTS)
                    is_comment = True
                elif token == "//":
                    self.setStyling(token_length, self.COMMENTS)
                    continue
                elif token in ["(", ")", "{", "}", "[", "]"]:
                    self.setStyling(token_length, self.BRACKETS)
                elif token in ['"', "'"]:
                    self.setStyling(token_length, self.STRING)
                    is_string = True
                elif token.isdigit():
                    self.setStyling(token_length, self.CONSTANTS)
                elif token in self.saved_names:
                    self.setStyling(token_length, self.FUNCTIONS)
                else:
                    self.setStyling(token_length, self.DEFAULT)
            else:
                self.setStyling(token_length, self.DEFAULT)
class SwiftLexer(GSLexer):
    def __init__(self, editor):
        super(SwiftLexer, self).__init__("Swift", editor)
        self.editor = editor
        self.generateKeywords([
            "associatedtype", "class", "deinit", "enum", "extension", "fileprivate", "func", "import", "init", 
            "inout", "internal", "let", "open", "operator", "private", "protocol", "public", "static", "struct", 
            "subscript", "typealias", "var", "break", "case", "continue", "default", "defer", "do", "else", "fallthrough", 
            "for", "guard", "if", "in", "repeat", "return", "switch", "where", "while", "as", "Any", "catch", 
            "false", "is", "nil", "rethrows", "super", "self", "Self", "throw", "throws", "true", "try"
        ])
        self.generateSavedNames([
            "Array", "Bool", "Character", "Double", "Float", "Int", "Optional", "String", "Dictionary", "Set", "print"
        ])

    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_multiline_string = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    if token_length == 1:
                        is_string = False
                elif token.startswith('"""'):
                    is_multiline_string = True
                    is_string = False
                continue

            if is_multiline_string:
                self.setStyling(token_length, self.STRING)
                if token.endswith('"""'):
                    is_multiline_string = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)
class TypeScriptLexer(GSLexer):
    def __init__(self, editor):
        super(TypeScriptLexer, self).__init__("TypeScript", editor)
        self.editor = editor
        self.generateKeywords([
            "abstract", "any", "as", "asserts", "bigint", "boolean", "break", "case", "catch", "class", "const",
            "continue", "debugger", "declare", "default", "delete", "do", "else", "enum", "export", "extends",
            "false", "finally", "for", "from", "function", "get", "if", "implements", "import", "in", "infer",
            "instanceof", "interface", "is", "keyof", "let", "module", "namespace", "never", "new", "null",
            "number", "object", "private", "protected", "public", "readonly", "require", "return", "set", "static",
            "string", "super", "switch", "symbol", "this", "throw", "true", "try", "type", "typeof", "undefined",
            "unique", "unknown", "var", "void", "while", "with", "yield"
        ])
        self.generateSavedNames([
            "Array", "Boolean", "Date", "Error", "Function", "JSON", "Math", "Number", "Object", "RegExp",
            "String", "Promise", "console", "window", "document"
        ])

    def styleText(self, ipos, epos):
        self.startStyling(ipos)

        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            else:
                self.setStyling(token_length, self.DEFAULT)
class JSXLexer(JavaScriptLexer):
    def __init__(self, editor):
        super(JSXLexer, self).__init__(editor)
        self.editor = editor
        self.generateKeywords(self.keywords)
        self.generateSavedNames(self.saved_names)

    def styleText(self, ipos, epos):
        self.startStyling(ipos)
        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_jsx = False
        jsx_tag = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if jsx_tag:
                self.setStyling(token_length, self.CONSTANTS)
                if token == '>':
                    jsx_tag = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            elif token == '<':
                self.setStyling(token_length, self.CONSTANTS)
                jsx_tag = True
            else:
                self.setStyling(token_length, self.DEFAULT)
class TSXLexer(TypeScriptLexer):
    def __init__(self, editor):
        super(TSXLexer, self).__init__(editor)
        self.editor = editor
        self.generateKeywords(self.keywords)
        self.generateSavedNames(self.saved_names)

    def styleText(self, ipos, epos):
        self.startStyling(ipos)
        active_text = self.editor.text()[ipos:epos]
        self.get_token(active_text)

        is_string = False
        is_comment = False
        is_tsx = False
        tsx_tag = False

        while True:
            active_token = self.get_next_token()
            if active_token is None:
                break
            token, token_length = active_token

            if is_comment:
                self.setStyling(token_length, self.COMMENTS)
                if token.startswith("*/") or token == "\n":
                    is_comment = False
                continue

            if is_string:
                self.setStyling(token_length, self.STRING)
                if token in ['"', "'"]:
                    is_string = False
                continue

            if tsx_tag:
                self.setStyling(token_length, self.CONSTANTS)
                if token == '>':
                    tsx_tag = False
                continue

            if token in self.keywords:
                self.setStyling(token_length, self.KEYWORD)
            elif token.startswith("/*"):
                self.setStyling(token_length, self.COMMENTS)
                is_comment = True
            elif token == "//":
                self.setStyling(token_length, self.COMMENTS)
                continue
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_length, self.BRACKETS)
            elif token in ['"', "'"]:
                self.setStyling(token_length, self.STRING)
                is_string = True
            elif token.isdigit():
                self.setStyling(token_length, self.CONSTANTS)
            elif token in self.saved_names:
                self.setStyling(token_length, self.FUNCTIONS)
            elif token == '<':
                self.setStyling(token_length, self.CONSTANTS)
                tsx_tag = True
            else:
                self.setStyling(token_length, self.DEFAULT)

