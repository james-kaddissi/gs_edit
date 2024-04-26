from PyQt5.QtWidgets import (
   QFrame, QHBoxLayout, QLabel, QWidget, QMenu, QAction, QMenuBar, QPushButton
)

from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QPixmap, QIcon, QImage

from gsedit.menu_bar import MenuBar

import os

class MenuItems(QWidget):

    def __init__(self, main_window) -> None:
        super().__init__(None)
        self.main_window = main_window

        self.is_menu_open = False
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)

        self.add_menu_bar()

    def add_menu_bar(self):
        menu_bar = MenuBar(self.main_window, self.main_window.bar, self.main_window.file_explorer_frame.file_explorer)
        menu_bar.setMouseTracking(True)

        menu_bar.setMinimumHeight(40)
        self.lay.addWidget(menu_bar)

class TopBar(QFrame):

    def __init__(self, main_window) -> None:
        super().__init__(None)
        self.main_window = main_window
        self.setFixedHeight(40)
        
        main_layout = QHBoxLayout(self)
        self.setMouseTracking(True)  # Enable mouse tracking
        self.drag_position = None
        self.installEventFilter(self) 
        img_logo = QImage(25, 25, QImage.Format.Format_Alpha8)
        img_logo.fill(Qt.GlobalColor.transparent)
        logo = QPixmap.fromImage(img_logo)
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet(f"font-family: Arial; font-size: 16px; font-weight: 500; color: white; margin-left: 10px; border: none;") 
        self.title_lbl.setPixmap(logo)
        # main_layout.addWidget(self.title_lbl, alignment=Qt.AlignmentFlag.AlignLeft) 

        menu = MenuItems(self.main_window)
        main_layout.addWidget(menu, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter) 

        self.top_label = QLabel("")
        self.top_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: white; margin-right: 10px; border: none;") 
        main_layout.addWidget(self.top_label, alignment=Qt.AlignmentFlag.AlignCenter)  

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(4, 0, 4, 0)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        base_path = os.path.dirname(__file__) 
        imageclose_path = os.path.join(base_path, 'images', 'close_icon.png')
        imagemin_path = os.path.join(base_path, 'images', 'min_icon.png')
        imagefull_path = os.path.join(base_path, 'images', 'full_icon.png')


        self._icon_close = QIcon(imageclose_path)
        self._icon_minimize = QIcon(imagemin_path)
        self._icon_restore = QIcon(imagefull_path)   

        self._transparent_bg = "background: transparent; border: none;"

        btn_size = 15

        close_lbl = QPushButton()
        close_lbl.setIcon(self._icon_close)
        close_lbl.setIconSize(QSize(btn_size, btn_size))
        close_lbl.setCursor(Qt.PointingHandCursor)
        close_lbl.clicked.connect(self.main_window.window().close)
        close_lbl.setStyleSheet(self._transparent_bg)


        minimize_lbl = QPushButton()
        minimize_lbl.setIcon(self._icon_minimize)
        minimize_lbl.setIconSize(QSize(btn_size, btn_size))
        minimize_lbl.setCursor(Qt.PointingHandCursor)
        minimize_lbl.clicked.connect(self.main_window.window().showMinimized)
        minimize_lbl.setStyleSheet(self._transparent_bg)
        
        restore_lbl = QPushButton()
        restore_lbl.setIcon(self._icon_restore)
        restore_lbl.setIconSize(QSize(btn_size, btn_size))
        restore_lbl.setCursor(Qt.PointingHandCursor)
        restore_lbl.clicked.connect(self.restore_window)
        restore_lbl.setStyleSheet(self._transparent_bg)
        
        nav_layout.addWidget(minimize_lbl)
        nav_layout.addWidget(restore_lbl)
        nav_layout.addWidget(close_lbl)

        main_layout.addLayout(nav_layout)
        self.refresh_style()
    def refresh_style(self):
        base_path = os.path.dirname(__file__) 
        style_sheet_path = os.path.join(base_path, 'css', 'topBar.qss')
        with open(style_sheet_path, "r") as style_file:
            self.setStyleSheet(style_file.read())         

    def restore_window(self):
        if self.main_window.window().isMaximized():
            self.main_window.window().showNormal() 
        else:
            self.main_window.window().showMaximized()   

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.drag_position = event.globalPos() - self.window().frameGeometry().topLeft()
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self.drag_position = None
                    return True
            elif event.type() == QEvent.MouseMove:
                if event.buttons() == Qt.LeftButton and self.drag_position is not None:
                    newPos = event.globalPos() - self.drag_position
                    self.window().move(newPos)
                    return True
        return super().eventFilter(obj, event)