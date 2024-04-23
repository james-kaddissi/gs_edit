import sys
from PyQt5.QtWidgets import QApplication
from gsedit.main import MainWindow
import os

def run():
    app = QApplication(sys.argv)
    window = MainWindow()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            window.file_explorer_frame.file_explorer.set_root_path(path)
        elif os.path.isfile(path):
            window.file_explorer_frame.file_explorer.open_file_in_tab(path)
        else:
            print(f"No such file or directory: {path}")

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
