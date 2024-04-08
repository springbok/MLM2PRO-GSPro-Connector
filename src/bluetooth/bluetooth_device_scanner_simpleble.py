import logging
from typing import List

import simplepyble
from PySide6.QtCore import QRunnable, QTimer, QObject
from simplepyble import Peripheral, Adapter

from src.bluetooth.bluetooth_device_scanner_signals import BluetoothDeviceScannerSignals


class BluetoothDeviceScannerSimpleBLE(QObject):
    SCANNER_TIMEOUT = 40000

    def __init__(self, launch_minitor_names: list[str]) -> None:
        super().__init__()
        self.signals = BluetoothDeviceScannerSignals()
        self._launch_minitor_names: List[str] = launch_minitor_names
        self._device: Peripheral = None
        self._adapter: Adapter = None
        self._is_active: bool = False
        self._scan_timer = QTimer()

    def scan(self) -> None:
        print('run')
        if self._is_active:
            logging.debug("Already searching for device.")
        else:
            try:
                adapters = simplepyble.Adapter.get_adapters()
                if len(adapters) <= 0:
                    raise Exception("No Bluetooth adapters found.")
                self._adapter = adapters[0]
                print(f'Found {len(adapters)} Bluetooth adapters. {self._adapter.identifier()}')
                self._adapter.set_callback_on_scan_start(self.__scanning_started)
                self._adapter.set_callback_on_scan_stop(self.__scanning_finished())
                self._adapter.set_callback_on_scan_updated(self.__add_device)
                self._adapter.scan_start()
                self._scan_timer.setSingleShot(True)
                self._scan_timer.setInterval(BluetoothDeviceScannerSimpleBLE.SCANNER_TIMEOUT)
                self._scan_timer.timeout.connect(self.stop_scanning)
                self._scan_timer.start()
            except Exception as e:
                self.__handle_scan_error(format(e))

    def stop_scanning(self) -> None:
        print('stop scanning')
        if self._adapter is not None and self._is_active:
            self._adapter.scan_stop()
        if self._device is None:
            logging.debug('Timeout, no device found')
            self.signals.status_update.emit('Timeout')
            self.signals.device_not_found.emit()

    def __add_device(self, device: Peripheral) -> None:
        print(f"Found {device.identifier()} [{device.address()}]")
        print(f'info: {device.identifier()} {device.identifier().startswith("MLM2-") or device.identifier().startswith("BlueZ ")}')
        if device.identifier() and any(device.identifier().startswith(name) for name in self._launch_minitor_names):
            self._device = device
            self._adapter.scan_stop()
            logging.debug(f'Launch monitor found: {self._device.identifier()} uuid: {device.address()}')
            print(f'Launch monitor found: {self._device.identifier()} uuid: {device.address()}')
            self.signals.status_update.emit('Device found')
            self.signals.device_found.emit(self._device)

    def __handle_scan_error(self, error) -> None:
        logging.debug(f'Error while scanning for device {error}')
        self.signals.error.emit(error)

    def __scanning_finished(self) -> None:
        print('scanning finished')
        if self._device is None and self._is_active:
            self._is_active = False
            logging.debug('No device found')
            self.signals.status_update.emit('No device found')
            self.signals.device_not_found.emit()
        self._scan_timer.stop()

    def __scanning_started(self) -> None:
        print('scanning started')
        logging.debug('Bluetooth device scan started')
        self.signals.status_update.emit("Scanning for device...")
        self._is_active = True
        print('scanning started')