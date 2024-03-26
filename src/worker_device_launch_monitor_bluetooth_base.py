import logging
import traceback
from threading import Event

from PySide6.QtBluetooth import QBluetoothDeviceInfo

from src.bluetooth.device_scanner import DeviceScanner
from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerDeviceLaunchMonitorBluetoothBase(WorkerBase):

    def __init__(self, settings: Settings, api, device_names: list[str]):
        WorkerBase.__init__(self)
        self.settings = settings
        self.api = api
        self.device_names = device_names
        self.name = 'WorkerDeviceLaunchMonitorBluetoothBase'
        self.scanner = DeviceScanner(self.device_names)
        self._shutdown = Event()

    def run(self) -> None:
        try:
            self.started.emit()
            self._pause.wait()
            # Scan for devices
            self.scanner.device_update.connect(self.__device_found)
            self.scanner.scan()
            print('after scan')
        except Exception as e:
            logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
            self.error.emit((e, traceback.format_exc()))
        finally:
            pass
        self.finished.emit()
        print('worker finished')

    def __device_found(self, device: QBluetoothDeviceInfo) -> None:
        print('__device_found')
        logging.debug(f'__device_found {device.name()} uuid: {device.address().toString()}')
        while not self._shutdown.is_set():
            Event().wait(1000 / 1000)

    def shutdown(self) -> None:
        super().shutdown()
        #if self.connection:
        #    self.connection.close()
