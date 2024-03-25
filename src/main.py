import asyncio
import sys
from PySide6 import QtWidgets
from qasync import QEventLoop

from src.MainWindow import MainWindow
from src.get_mutex import GetMutex


def main():
    mutex = GetMutex()
    if (app := mutex).IsRunning():
        print("Application is already running")
        sys.exit()

    app = QtWidgets.QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(app)
    window.show()

    with loop:
        loop.run_forever()
