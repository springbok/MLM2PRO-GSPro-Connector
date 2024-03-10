from threading import Event
from PySide6.QtCore import QObject, Signal


class WorkerBase(QObject):
    finished = Signal()
    error = Signal(tuple)
    started = Signal()
    paused = Signal()
    resumed = Signal()
    stopped = Signal()
    running = Signal()


    def __init__(self):
        super(WorkerBase, self).__init__()
        self.name = 'WorkerBase'
        self.worker_started = False
        self._shutdown = Event()
        self._pause = Event()
        self.pause()

    def run(self):
        return

    def shutdown(self):
        print(f'{self.name} shutdown')
        # Do shutdown first so it doesn't execute when we resume
        self._shutdown.set()
        # Resume
        self._pause.set()
        self.finished.emit()

    def pause(self):
        self._pause.clear()
        self.paused.emit()

    def resume(self):
        if self.worker_started:
            self._pause.set()
            self.resumed.emit()

    def is_paused(self):
        return not self._pause.is_set()

    def stop(self):
        self.worker_started = False
        self.stopped.emit()
        self.pause()

    def start(self):
        self.worker_started = True
        self.running.emit()
        self.resume()

    def is_running(self):
        return self.worker_started


