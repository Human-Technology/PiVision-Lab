import sys

from PySide6.QtWidgets import QApplication
from view.main_window import MainWindow
from controller.controller import Controller

def main():

    app = QApplication()

    window = MainWindow()

    controller = Controller(window)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()