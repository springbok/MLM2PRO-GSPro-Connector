import logging
from typing import List

import simplepyble
from PySide6.QtCore import QObject, Signal, QTimer


class BluetoothDeviceScannerSimpleBLE(QObject):
    SCANNER_TIMEOUT = 40000

    device_found = Signal(object)
    device_not_found = Signal()
    status_update = Signal(str)
    error = Signal(str)

    def __init__(self, launch_minitor_names: list[str]) -> None:
        super().__init__()
        self.launch_minitor_names: List[str] = launch_minitor_names
        self.scan_timer = QTimer()
        self.device = None
        self._adapter = None
        self._is_active: bool = False

    def scan(self) -> None:
        if self._is_active:
            logging.debug("Already searching for device.")
        else:
            try:
                adapters = simplepyble.Adapter.get_adapters()
                if len(adapters) <= 0:
                    raise Exception("No Bluetooth adapters found.")
                self._adapter = adapters[0]
                self._adapter.set_callback_on_scan_start(self.__scanning_started)
                self._adapter.set_callback_on_scan_stop(self.__scanning_finished())
                self._adapter.set_callback_on_scan_found(self.__add_device)
                self._adapter.scan_for(BluetoothDeviceScannerSimpleBLE.SCANNER_TIMEOUT)
            except Exception as e:
                self.__handle_scan_error(format(e))

    def stop_scanning(self) -> None:
        if self._adapter is not None and self._is_active:
            self._adapter.scan_stop()
        if self.device is None:
            logging.debug('Timeout, no device found')
            self.status_update.emit('Timeout')
            self.device_not_found.emit()

    def __add_device(self, device) -> None:
        print(f'info: {device.identifier()} {device.identifier().startswith("MLM2-") or device.identifier().startswith("BlueZ ")}')
        if device.identifier() and any(device.identifier().startswith(name) for name in self.launch_minitor_names):
            self.device = device
            self._adapter.scan_stop()
            logging.debug(f'Launch monitor found: {self.device.identifier()} uuid: {device.address()}')
            print(f'Launch monitor found: {self.device.identifier()} uuid: {device.address()}')
            self.status_update.emit('Device found')
            self.device_found.emit(self.device)

    def __handle_scan_error(self, error) -> None:
        logging.debug(f'Error while scanning for device {error}')
        self.error.emit(error)

    def __scanning_finished(self) -> None:
        self._is_active = False
        if self.device is None:
            logging.debug('No device found')
            self.status_update.emit('No device found')
            self.device_not_found.emit()

    def __scanning_started(self) -> None:
        logging.debug('Bluetooth device scan started')
        self.status_update.emit("Scanning for device...")
        self._is_active = True
        print('scanning started')