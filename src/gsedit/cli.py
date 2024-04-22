import sys
from PyQt5.QtWidgets import QApplication
from gsedit.main import MainWindow

def run():
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        path = sys.argv[1]
        window = MainWindow()

        window.show()
    else:
        window = MainWindow()
        window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
