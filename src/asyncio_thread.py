from PySide6.QtCore import QThread
import asyncio

class AsyncioThread(QThread):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def run(self):
        self.loop.run_forever()