import logging
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
        self.club = None
        self.worker_started = False
        self._shutdown = Event()
        self._pause = Event()
        self.pause()

    def run(self):
        return

    def shutdown(self):
        # Do shutdown first so it doesn't execute when we resume
        self._shutdown.set()
        # Resume
        self._pause.set()
        self.finished.emit()

    def pause(self):
        self._pause.clear()
        self.paused.emit()

    def resume(self):
        logging.debug(f"{self.__class__.__name__} Resuming Worker worker_started: {self.worker_started}")
        if self.worker_started:
            self._pause.set()
            self.resumed.emit()

    def is_paused(self):
        return not self._pause.is_set()

    def stop(self):
        logging.debug(f"{self.__class__.__name__} Stopping Worker")
        self.worker_started = False
        self.stopped.emit()
        self.pause()

    def start(self):
        self.worker_started = True
        self.running.emit()
        self.resume()

    def is_running(self):
        return self.worker_started

    def ignore_shots_after_restart(self):
        pass

    def club_selected(self, club):
        self.club = club

    def selected_club(self):
        return self.club

    def putter_selected(self):
        return self.selected_club() == 'PT'
