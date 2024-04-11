from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path

import os
import subprocess

class MenuBar(QMenuBar):
    def __init__(self, main_window, status_bar, file_explorer) -> None:
        super(MenuBar, self).__init__()
        self.initialize_main_menu_bar()
        self.refresh_style()
        self.window = main_window
        self.status_bar = status_bar
        self.file_explorer = file_explorer

    def refresh_style(self):
        self.setStyleSheet(open("./src/css/menuBar.qss", "r").read())

    def initialize_main_menu_bar(self):

        self.initialize_file_menu()
        self.initialize_edit_menu()
        self.initialize_selection_menu()
        self.initialize_run_menu()
        self.initialize_terminal_menu()
    
    def initialize_file_menu(self):
        self.file_menu = self.addMenu("File")
        self.new_options()
        self.file_menu.addSeparator()
        self.open_options()
        self.file_menu.addSeparator()
        self.save_options()
        self.file_menu.addSeparator()
    
    def initialize_edit_menu(self):
        self.edit_menu = self.addMenu("Edit")
        self.undo_redo_options()
        self.file_menu.addSeparator()
        self.ccp_options()

    def initialize_selection_menu(self):
        self.selection_menu = self.addMenu("Selection")
        self.selecting_options()
    
    def initialize_run_menu(self):
        self.run_menu = self.addMenu("Run")
        self.run_options()

    def initialize_terminal_menu(self):
        self.terminal_menu = self.addMenu("Terminal")
        self.terminal_options()

    def new_options(self): 
        self.new_file_option()
        self.new_folder_option()
        self.new_project_option()
    def new_file_option(self):
        new_file = self.file_menu.addAction("New File")
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.new_file_command)
    def new_folder_option(self): 
        new_folder = self.file_menu.addAction("New Folder")
        new_folder.setShortcut("Ctrl+Alt+N")
        new_folder.triggered.connect(self.new_folder_command)
    def new_project_option(self): 
        new_project = self.file_menu.addAction("New Project")
        new_project.setShortcut("Ctrl+Alt+Win+N")
        new_project.triggered.connect(self.new_project_command)

    def open_options(self): 
        self.open_file_option()
        self.open_folder_option() 
        self.open_project_option()
    def open_file_option(self): 
        open_file = self.file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file_command)
    def open_folder_option(self): 
        open_folder = self.file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+Alt+O")
        open_folder.triggered.connect(self.open_folder_command)
    def open_project_option(self): 
        open_project = self.file_menu.addAction("Open Project")
        open_project.setShortcut("Ctrl+Alt+Win+O")
        open_project.triggered.connect(self.open_project_command)

    def save_options(self): 
        self.save_option()
        self.save_as_option()
        self.save_all_option()
    def save_option(self): 
        save = self.file_menu.addAction("Save")
        save.setShortcut("Ctrl+S")
        save.triggered.connect(self.save_command)
    def save_as_option(self): 
        save_as = self.file_menu.addAction("Save As...")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as_command)
    def save_all_option(self): 
        save_all = self.file_menu.addAction("Save All")
        save_all.setShortcut("Ctrl+K S")
        save_all.triggered.connect(self.save_all_command)
    
    def undo_redo_options(self): 
        self.undo_option()
        self.redo_option()
    def undo_option(self): 
        undo = self.edit_menu.addAction("Undo")
        undo.setShortcut("Ctrl+Z")
        undo.triggered.connect(self.undo_command)
    def redo_option(self): 
        redo = self.edit_menu.addAction("Redo")
        redo.setShortcut("Ctrl+Y")
        redo.triggered.connect(self.redo_command)

    def ccp_options(self): 
        self.cut_option()
        self.copy_option()
        self.paste_option()
    def cut_option(self): 
        cut = self.edit_menu.addAction("Cut")
        cut.setShortcut("Ctrl+X")
        cut.triggered.connect(self.cut_command)
    def copy_option(self): 
        copy = self.edit_menu.addAction("Copy")
        copy.setShortcut("Ctrl+C")
        copy.triggered.connect(self.copy_command)
    def paste_option(self): 
        paste = self.edit_menu.addAction("Paste")
        paste.setShortcut("Ctrl+V")
        paste.triggered.connect(self.paste_command)

    def selecting_options(self):
        self.select_all_option()
    def select_all_option(self):
        select_all = self.selection_menu.addAction("Select All")
        select_all.setShortcut("Ctrl+A")
        select_all.triggered.connect(self.select_all_command)

    def run_options(self):
        self.run_file_option()
        self.run_main_option()
        self.run_in_new_terminal_option()
    def run_file_option(self):
        run_file = self.run_menu.addAction("Run File")
        run_file.triggered.connect(self.run_file_command)
    def run_main_option(self):
        run_main = self.run_menu.addAction("Run Main")
        run_main.triggered.connect(self.run_main_command)
    def run_in_new_terminal_option(self):
        run_in_new_terminal = self.run_menu.addAction("Run in New Terminal")
        run_in_new_terminal.triggered.connect(self.run_in_new_terminal_command)
    
    def terminal_options(self):
        self.toggle_terminal_option()
        self.new_terminal_option()
    def toggle_terminal_option(self):
        toggle_terminal = self.terminal_menu.addAction("Toggle Terminals")
        toggle_terminal.triggered.connect(self.toggle_terminal_command)
    def new_terminal_option(self):
        new_terminal = self.terminal_menu.addAction("New Terminal")
        new_terminal.triggered.connect(self.new_terminal_command)

    def new_file_command(self):
        self.window.add_tab(Path("untitled"), is_new_file=True)
    def new_folder_command(self):
        folder_path = Path(self.file_explorer.file_system_model.rootPath()) / 'new folder'
        x = 1
        while folder_path.exists():
            folder_path = Path(folder_path.parent / f"new folder{x}")
            x += 1
        i = self.file_explorer.file_system_model.mkdir(self.file_explorer.rootIndex(), folder_path.name)
        self.file_explorer.edit(i)
    def new_project_command(self):
        self.status_bar.set_timed_message("Project functionality to be added...", 3000)
    def open_file_command(self):
        new_file, _ = QFileDialog.getOpenFileName(self.window, "Pick A File", "", "All Files [*];;Python Files [*.py]")
        if new_file == '':
            self.status_bar.set_timed_message("Open cancelled.", 2000)
            return
        path = Path(new_file)
        self.window.add_tab(path)
    def open_folder_command(self):
        new_folder = QFileDialog.getExistingDirectory(self.window, "Pick A Folder", "")
        if new_folder:
            self.window.file_explorer_frame.file_explorer.file_system_model.setRootPath(new_folder)
            self.window.file_explorer_frame.file_explorer.setRootIndex(self.window.file_explorer_frame.file_explorer.file_system_model.index(new_folder))
            self.status_bar.set_timed_message(f"Changed folder to {new_folder}", 2000)
    def open_project_command(self):
        self.status_bar.set_timed_message("Project functionality to be added...", 3000)
    def save_command(self):
        if self.window.current_file is None and self.window.tab.count() > 0:
            self.save_as_command()

        save_editor = self.window.tab.currentWidget()
        self.window.current_file.write_text(save_editor.text())
        self.status_bar.set_timed_message(f"Saved {self.window.current_file.name}", 2000)
        save_editor = self.window.tab.currentWidget()
        save_editor.unsaved_changes = False
    def save_as_command(self):
        save_editor = self.window.tab.currentWidget()
        if save_editor is None:
            return

        path_to_file = QFileDialog.getSaveFileName(self.window, "Save As", os.getcwd())[0]
        if path_to_file == '':
            self.status_bar.set_timed_message("Save cancelled.", 2000)
            return
        path = Path(path_to_file)
        path.write_text(save_editor.text())
        self.window.tab.setTabText(self.window.tab.currentIndex(), path.name)
        self.window.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.window.current_file = path
        save_editor.unsaved_changes = False
    def save_all_command(self):
        for i in range(self.window.tab.count()):
            editor = self.window.tab.widget(i)
            if editor.unsaved_changes:
                if self.window.current_file is None:
                    self.save_as_command()
                else:
                    self.save_command()
    def undo_command(self):
        editor = self.window.tab.currentWidget()
        if editor is not None:
            editor.undo()
    def redo_command(self):
        editor = self.window.tab.currentWidget()
        if editor is not None:
            editor.redo()
    def cut_command(self):
        editor = self.window.tab.currentWidget()
        if editor is not None:
            editor.cut()
    def copy_command(self):
        editor = self.window.tab.currentWidget()
        if editor is not None:
            editor.copy()
    def paste_command(self):
        editor = self.window.tab.currentWidget()
        if editor is not None:
            editor.paste()
    def select_all_command(self):
        editor = self.window.tab.currentWidget()
        if editor is not None:
            editor.selectAll()
    def run_file_command(self):
        if self.window.current_file is None:
            self.status_bar.set_timed_message("No file selected.", 2000)
            return

        file_path = Path(self.window.current_file)
        command = None

        if file_path.suffix == ".py":
            command = f'python "{file_path}"\n' 
        elif file_path.suffix == ".c":

            command = f'gcc "{file_path}" -o "{file_path.stem}" && "{file_path.stem}"\n'
        elif file_path.suffix == ".cpp":

            command = f'g++ "{file_path}" -o "{file_path.stem}" && "{file_path.stem}"\n'
        elif file_path.suffix == ".rs":
            cargo_manifest_path = file_path.parent / "Cargo.toml"
            command = f'cargo run --manifest-path "{cargo_manifest_path}"\n'
        else:
            self.status_bar.set_timed_message(f"Running files of type {file_path.suffix} is not supported.", 2000)
            return
        if self.window.main_body_frame.terminal_widget.isVisible():
            self.status_bar.set_timed_message(f"Running in terminal...", 2000)
        else:
            self.window.main_body_frame.terminal_widget.show()
            self.status_bar.set_timed_message(f"Running in opened terminal...", 2000)

        if command:
            terminal_process = self.window.main_body_frame.terminal_widget.terminal.process
            terminal_process.write(command.encode())
            terminal_process.waitForBytesWritten()
        

    def run_main_command(self):
        pass
    def run_in_new_terminal_option(self):
        pass

    def toggle_terminal_command(self):
        self.window.toggle_terminal()

    def new_terminal_command(self):
        self.window.main_body_frame.terminal_widget.add_new_terminal_tab()


    