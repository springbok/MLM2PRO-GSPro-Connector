import traceback
from threading import Event

from PySide6.QtCore import QObject, Signal


class WorkerThread(QObject):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object or None)
    progress = Signal(int)
    started = Signal()
    paused = Signal()
    resumed = Signal()

    def __init__(self, fn, *args, **kwargs):
        super(WorkerThread, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._pause = Event()
        self.resume()

    def run(self):
        self._pause.wait()
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.started.emit()
            result = self.fn(
                *self.args, **self.kwargs
            )
        except Exception as e:
            traceback.print_exc()
            self.error.emit((e, traceback.format_exc()))
        else:
            self.result.emit(result)  # Return the result of the processing
        finally:
            self.finished.emit()  # Done

    def pause(self):
        self._pause.clear()
        self.paused.emit()

    def resume(self):
        self._pause.set()
        self.resumed.emit()
