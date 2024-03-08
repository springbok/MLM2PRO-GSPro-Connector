import traceback
from PySide6.QtCore import QObject, Signal

from src.gspro_connect import GSProConnect


class GsproWorker(QObject):
    finished = Signal()
    error = Signal(tuple)
    sent = Signal(object or None)
    progress = Signal(int)
    started = Signal(object)

    def __init__(self, gspro_connection: GSProConnect):
        super(GsproWorker, self).__init__()
        self.gspro_connection = gspro_connection

    def run(self, balldata=None):
        if not balldata is None:
            try:
                self.started.emit(balldata)
                self.gspro_connection.launch_ball(balldata)
            except Exception as e:
                traceback.print_exc()
                self.error.emit((e, traceback.format_exc()))
            else:
                self.sent.emit(balldata)  # Return the result of the processing
            finally:
                self.finished.emit()  # Done
                