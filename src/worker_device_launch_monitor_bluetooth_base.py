import logging
import traceback
from threading import Event

from PySide6.QtBluetooth import QBluetoothDeviceInfo

from src.bluetooth.bluetooth_client import BluetoothClient
from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerDeviceLaunchMonitorBluetoothBase(WorkerBase):

    def __init__(self, settings: Settings, api, device: QBluetoothDeviceInfo):
        WorkerBase.__init__(self)
        self.settings = settings
        self.api = api
        self.device = device
        self.name = 'WorkerDeviceLaunchMonitorBluetoothBase'
        self.client = BluetoothClient()
        self._shutdown = Event()

    def run(self) -> None:
        try:
            self.started.emit()
            self._pause.wait()
            print('connecting to device')
            self.client.connect_client(self.device)
            while not self._shutdown.is_set():
                # When _pause is clear we wait(suspended) if set we process
                self._pause.wait()
                Event().wait(1)
        except Exception as e:
            logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
            self.error.emit((e, traceback.format_exc()))
        finally:
            print('reset client')
            self.client.reset_connection()
        self.finished.emit()
        print('worker finished')

    def shutdown(self) -> None:
        super().shutdown()
        # if self.connection:
        #     self.connection.close()
