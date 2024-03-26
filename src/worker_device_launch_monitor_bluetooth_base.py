import logging
import traceback
from threading import Event
from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerDeviceLaunchMonitorBluetoothBase(WorkerBase):

    def __init__(self, settings: Settings, api):
        WorkerBase.__init__(self)
        self.settings = settings
        self.api = api
        self.name = 'WorkerDeviceLaunchMonitorBluetoothBase'
        self._shutdown = Event()

    def run(self) -> None:
        try:
            self.started.emit()
            self._pause.wait()
            while not self._shutdown.is_set():
                Event().wait(1000 / 1000)
        except Exception as e:
            logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
            self.error.emit((e, traceback.format_exc()))
        finally:
            pass
        self.finished.emit()

    def shutdown(self):
        super().shutdown()
        #if self.connection:
        #    self.connection.close()
