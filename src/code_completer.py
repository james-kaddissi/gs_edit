# use jedi module for autocomplete
from jedi import Script
from jedi.api import Completion

from PyQt5.QtCore import *
from PyQt5.Qsci import *

class Completer(QThread):
    def __init__(self, path, ref):
        super(Completer, self).__init__(None)
        self.path = path
        self.ref = ref
        self.collection = None
        self.script = None
        self.ln = 0
        self.char = 0
        self.txt = ""

    def try_complete(self):
        self.script = Script(self.txt, path = self.path)
        self.collection = self.script.complete(self.ln, self.char)
        self.retrieve(self.collection)

        self.final_result.emit()

    def load_references(self, collection):
        self.ref.clear()
        [self.ref.add(i.name) for i in collection]
        self.ref.prepare()

    def retrieve(self, ln, char, txt):
        self.ln = ln
        self.char = char
        self.txt = txt
        self.start()