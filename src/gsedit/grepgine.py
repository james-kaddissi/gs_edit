# This Grepgine is brought to you buy Fuzzy Search!
import os
import re
from pathlib import Path
from PyQt5.QtCore import QObject

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import gsedit.gsconfig

class GrepListItem(QListWidgetItem):
    def __init__(self, name, path, ln,  endln, lntxt):
        self.name = name
        self.path = path
        self.ln = ln
        self.endln = endln
        self.lntxt = lntxt
        self.formatText = f'In {self.name}: on line {self.ln}:{self.endln} = {self.lntxt} \./'
        super().__init__(self.formatText)

    def __str__(self):
        return self.formatText

    def __repr__(self):
        return self.formatText
    

class Grepgine(QThread):
    final_result = pyqtSignal(list)

    def __init__(self):
        super(Grepgine, self).__init__(None)

        self.content = []
        self.path = None
        self.txt = None
        self.in_project = None

    def nav(self, path, dir_ignore: list, grep_ignore):
        for root, folders, files in os.walk(path, topdown=True):
            folders[:] = [i for i in folders if i not in dir_ignore]
            files[:] = [i for i in files if Path(i).suffix not in grep_ignore]
            yield root, folders, files

    def binary_check(self, path):
        with open(path, 'rb') as f:
            return b'\0' in f.read(1024)

    def grep(self):
        self.content = []
        dir_ignore = set(["gsconfig", "venv", ".idea", "__pycache__", ".git", ".svn", "hg", ".bzr"])
        if self.in_project:
            dir_ignore.remove("venv")
        grep_ignore = set([".qm", ".png", ".jpg", ".exe", ".pyc", ".svg", ".dll"])

        for root, folders, files in self.nav(self.path, dir_ignore, grep_ignore):
            if len(self.content) > 20000:
                break
            for i in files:
                path = os.path.join(root, i)
                if self.binary_check(path):
                    break

                try:
                    with open(path, 'r', encoding='utf8') as file:
                        try:
                            cont = re.compile(self.txt, re.IGNORECASE)
                            for j, k in enumerate(file):
                                if l := cont.search(k):
                                    prep = GrepListItem(
                                        i,
                                        path,
                                        j,
                                        l.end(),
                                        k[l.start():].strip()[:200]
                                    )
                                    self.content.append(prep)
                        except re.error as err:
                            if gsconfig.get_config("debugMode"):
                                print(err)
                            
                except:
                    if gsconfig.get_config("debugMode"):
                        print(err)
                    continue
        self.final_result.emit(self.content)

    def activate(self):
        self.grep()

    def modify(self, txt, path, in_project):
        self.txt = txt
        self.path = path
        self.in_project = in_project
        self.activate()