import traceback
from PySide6.QtCore import Signal

from src.gspro_connect import GSProConnect
from src.worker_base import WorkerBase


class WorkerGspro(WorkerBase):
    sent = Signal(object or None)

    def __init__(self, gspro_connection: GSProConnect):
        super().__init__()
        self.gspro_connection = gspro_connection

    def run(self, balldata=None):
        if balldata is not None:
            try:
                self.started.emit()
                self.gspro_connection.launch_ball(balldata)
            except Exception as e:
                traceback.print_exc()
                self.error.emit((e, traceback.format_exc()))
            else:
                self.sent.emit(balldata)  # Return the result of the processing
            finally:
                self.finished.emit()  # Done
                