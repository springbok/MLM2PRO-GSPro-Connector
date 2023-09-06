import sys
from PySide6 import QtWidgets
from src.MainWindow import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(app)
    window.show()

    app.exec()