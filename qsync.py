import sys
import asyncio

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qasync import QEventLoop, QApplication, asyncClose, asyncSlot


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())
        self.lbl_status = QLabel("Idle", self)
        self.layout().addWidget(self.lbl_status)

    @asyncClose
    async def closeEvent(self, event):
        print('closeEvent')

    @asyncSlot()
    async def onMyEvent(self):
        print('onMyEvent')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    main_window = MainWindow()
    main_window.show()

    loop = asyncio.get_event_loop()
    with loop:
        loop.run_until_complete(app_close_event.wait())