import os

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Signal

from .main_panel import MainPanel

class MainWindow(QMainWindow):

    windows_closed = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PiVision Lab")
        self.mainPanel = MainPanel()
        self.setCentralWidget(self.mainPanel)
        self.apply_style()

    def stopTimer(self):
        self.mainPanel.timer.stop()
        self.mainPanel.timer.timeout.disconnect()

    def closeEvent(self, event):
        self.mainPanel.timer.stop()
        self.mainPanel.timer.timeout.disconnect()
        self.windows_closed.emit()
        return super().closeEvent(event)
    
    def apply_style(self):
        with open(os.path.join('.', 'style', 'style.qss'), 'r') as file:
            style = file.read()
            self.setStyleSheet(style)
