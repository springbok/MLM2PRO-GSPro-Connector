import sys
from PySide6 import QtWidgets, QtAsyncio
from src.MainWindow import MainWindow
from src.get_mutex import GetMutex


def main():
    mutex = GetMutex()
    if (app := mutex).IsRunning():
        print("Application is already running")
        sys.exit()

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(app)
    window.show()

    QtAsyncio.run()
