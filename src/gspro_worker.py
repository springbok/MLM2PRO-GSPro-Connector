import traceback
from PySide6.QtCore import QObject, Signal


class GsproWorker(QObject):
    finished = Signal()
    error = Signal(tuple)
    sent = Signal(object or None)
    progress = Signal(int)
    started = Signal(object)

    def __init__(self, launch_ball):
        super(GsproWorker, self).__init__()
        self.launch_ball = launch_ball

    def run(self, balldata=None):
        if not balldata is None:
            try:
                self.started.emit(balldata)
                self.launch_ball(balldata)
            except Exception as e:
                traceback.print_exc()
                self.error.emit((e, traceback.format_exc()))
            else:
                self.sent.emit(balldata)  # Return the result of the processing
            finally:
                self.finished.emit()  # Done
                