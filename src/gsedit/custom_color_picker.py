from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QApplication
from PyQt5.QtGui import QFont, QColor

class ColorPickerButton(QWidget):
    def __init__(self, parent=None):
        super(ColorPickerButton, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.color_label = QLabel(self)
        self.color_label.setText("Color Picker")
        self.color_label.setStyleSheet("background-color: red; color: white;")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setFixedSize(70, 30)
        font_size = 7 
        font = QFont()
        font.setPointSize(font_size)
        self.color_label.setFont(font)
        
        self.color_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.color_label.mousePressEvent = self.start_color_picker

    def start_color_picker(self, event):
        self.grabMouse()
        self.setCursor(Qt.CrossCursor)
        self.color_label.setText("Picking...")

    def mouseMoveEvent(self, event):
        screen = QApplication.primaryScreen()
        color = screen.grabWindow(QApplication.desktop().winId(), event.globalX(), event.globalY(), 1, 1).toImage().pixel(0, 0)
        color = QColor(color)
        hex_color = color.name()
        print(hex_color)
        self.color_label.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 5px;")
        self.color_label.setText(hex_color)
        self.update()

    def mousePressEvent(self, event):
        screen = QApplication.primaryScreen()
        color = screen.grabWindow(QApplication.desktop().winId(), event.globalX(), event.globalY(), 1, 1).toImage().pixel(0, 0)
        color = QColor(color)
        hex_color = color.name()
        clipboard = QApplication.clipboard()
        clipboard.setText(hex_color)
        self.releaseMouse()
        self.setCursor(Qt.ArrowCursor)
        self.color_label.setText(f"Copied: {hex_color}")
        self.color_label.setStyleSheet(f"background-color: {hex_color}; color: white;")

