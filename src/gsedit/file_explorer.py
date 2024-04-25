from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pathlib import Path
import subprocess, sys, shutil, os

from gsedit.text_editor import TextEditor
from gsedit.popup import PopupMessage

class FileExplorer(QTreeView):
    def __init__(self, tab, add_tab, window):
        super(FileExplorer, self).__init__(None)

        self.tab = tab
        self.add_tab = add_tab
        self.window = window

        self.ui_font = QFont("Consolas", 14) 

        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(os.getcwd())

        self.file_system_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives)
        self.file_system_model.setReadOnly(False)
        
        self.setFocusPolicy(Qt.NoFocus)

        self.setFont(self.ui_font)
        self.setModel(self.file_system_model)
        self.setRootIndex(self.file_system_model.index(os.getcwd()))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        self.clicked.connect(self.file_explorer_clicked)
        self.setIndentation(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        self.last_name = None
        self.rename = False
        self.curr_index = None

        self.itemDelegate().closeEditor.connect(self.close_editor)

    def set_no_root(self):
        # Clear the root path
        self.file_system_model.setRootPath("No Folder Opened")
        self.setRootIndex(QModelIndex()) 
        self.setEnabled(False) 
    
    def open_file_in_tab(self, file_path):
        editor = TextEditor()
        with open(file_path, 'r', encoding='utf-8') as file:
            editor.setText(file.read())
        self.tab.addTab(editor, os.path.basename(file_path))


    def set_root_path(self, path):
        self.file_system_model.setRootPath(path)
        self.setRootIndex(self.file_system_model.index(path))
        self.setEnabled(True)  

    def enable_explorer(self):
        self.setEnabled(True)

    def close_editor(self, editor):
        if self.rename:
            self.renamefn()
    
    def file_explorer_clicked(self, index: QModelIndex):
        path = self.file_system_model.filePath(index)
        p = Path(path)
        if p.is_file():
            self.add_tab(self.window, p)

    def show_menu(self, x):
        i = self.indexAt(x)
        command_menu = QMenu()
        command_menu.addAction("New File")
        command_menu.addAction("New Folder")
        command_menu.addAction("Reveal in File Explorer")
        if i.column() == 0:
            command_menu.addAction("Rename")
            command_menu.addAction("Delete")

        command = command_menu.exec_(self.viewport().mapToGlobal(x))

        if command == None: return
        if command.text() == "Rename": self.rename_command(i)
        elif command.text() == "Delete": self.delete_command(i)
        elif command.text() == "New File": self.newfile_command(i)
        elif command.text() == "New Folder": self.newfolder_command()
        elif command.text() == "Reveal in File Explorer": self.reveal_command(i)
        else: pass

    def renamefn(self):
        name = self.file_system_model.fileName(self.curr_index)
        if self.last_name == name: return
        for i in self.tab.findChildren(TextEditor):
            if i.path.name == self. last_name:
                i.path = i.path.parent / name
                self.tab.setTabText(
                    self.tab.indexOf(i), name
                )
                self.tab.repaint()
                i.abs_path = i.path.absolute()
                self.window.current_file = i.path
                break

    def rename_command(self, i):
        self.edit(i)
        self.last_name = self.file_system_model.fileName(i)
        self.rename = True
        self.curr_index = i
    
    def delete(self, path):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    
    def delete_command(self, i):
        name = self.file_system_model.fileName(i)
        delete_confirm = PopupMessage("Delete", f"Confirm deletion of '{name}'?")
        if delete_confirm == QMessageBox.Yes:
            if self.selectionModel().selectedRows():
                for j in self.selectionModel().selectedRows():
                    path = Path(self.file_system_model.filePath(i))
                    self.delete(path)
                    for k in self.tab.findChildren(TextEditor):
                        if k.path.name == path.name:
                            self.tab.removeTab(self.tab.indexOf(k))
    
    def newfile_command(self, i):
        root = self.file_system_model.rootPath()
        if i.column() != -1 and self.file_system_model.isDir(i):
            self.expand(i)
            root = self.file_system_model.filePath(i)
        
        file_path = Path(self.file_system_model.rootPath()) / 'new file'
        x = 1
        while file_path.exists():
            file_path = Path(file_path.parent / f"new file{x}")
            x += 1
        file_path.touch()
        new_index = self.file_system_model.index(str(file_path.absolute()))
        self.edit(new_index)
    
    def newfolder_command(self):
        folder_path = Path(self.file_system_model.rootPath()) / 'new folder'
        x = 1
        while folder_path.exists():
            folder_path = Path(folder_path.parent / f"new folder{x}")
            x += 1
        i = self.file_system_model.mkdir(self.rootIndex(), folder_path.name)
        self.edit(i)

    def reveal_command(self, i):
        path = os.path.abspath(self.file_system_model.filePath(i))
        directory_check = self.file_system_model.isDir(i)
        if os.name == "nt": # WINDOWS OS
            if directory_check:
                subprocess.Popen(f'explorer "{path}"')
            else:
                subprocess.Popen(f'explorer /select,"{path}"')
        elif os.name == "posix":
            if sys.platform == "darwin": # MAC OS
                if directory_check:
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["open", "-R", path])
            else: # LINUX OS
                subprocess.Popen(["xdg-open", os.path.dirname(path)])
        else:
            raise OSError(f"Unsupported platform {os.name}") # adding support would be easy just add a new elif os.name for that plattform, add a directory_check, and then use the right commands for that OS


    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:
        root = Path(self.file_system_model.rootPath())
        if e.mimeData().hasUrls:
            for url in e.mimeData().urls():
                path = Path(url.toLocalFile())
                if self.file_system_model.isDir(self.indexAt(e.pos())): # Check if the location you're dropping into is a directory and not a file
                    if path.is_dir(): # Check if the item you're dropping is a directory and not a file
                        shutil.copytree(path, root / path.name)
                    else:
                        if root.samefile(self.file_system_model.rootPath()):
                            i: QModelIndex = self.indexAt(e.pos())
                            if i.column() == -1:
                                shutil.move(path, root / path.name)
                            else:
                                folder = Path(self.file_system_model.filePath(i))
                                shutil.move(path, folder / path.name)
                        else:

                            shutil.copy(path, root / path.name)
                else:
                    print("NUH UH")
        e.accept()

        return super().dropEvent(e)
    
class FileExplorerLayout(QVBoxLayout):
    def __init__(self) -> None:
        super(FileExplorerLayout, self).__init__()
        self.initialize_layout()

    def initialize_layout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)