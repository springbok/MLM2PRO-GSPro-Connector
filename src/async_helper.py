import asyncio

from PySide6.QtCore import QObject


class AsyncHelper(QObject):

    def __init__(self, worker, entry):
        super().__init__()
        self.entry = entry
        self.worker = worker
        if hasattr(self.worker, "start_signal") and isinstance(self.worker.start_signal, Signal):
            self.worker.start_signal.connect(self.on_worker_started)

    def on_worker_started(self):
        asyncio.ensure_future(self.entry())
