from threading import Event
from PySide6.QtCore import QObject, Signal


class WorkerBase(QObject):
    finished = Signal()
    error = Signal(tuple)
    started = Signal()
    paused = Signal()
    resumed = Signal()


    def __init__(self):
        super(WorkerBase, self).__init__()
        self.name = 'WorkerBase'
        self._shutdown = Event()
        self._pause = Event()
        self.pause()

    def run(self):
        return

    def shutdown(self):
        self.resume()
        self._shutdown.set()
        self.finished.emit()

    def pause(self):
        self._pause.clear()
        self.paused.emit()

    def resume(self):
        self._pause.set()
        self.resumed.emit()
