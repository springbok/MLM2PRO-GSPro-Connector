import datetime
import logging
import traceback
from threading import Event
from typing import List, Union

import simplepyble
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication
from simplepyble import Peripheral, Adapter


class BluetoothDeviceScannerSimpleBLE(QObject):
    SCANNER_TIMEOUT = 40
    
    device_found = Signal(object)
    device_not_found = Signal()
    status_update = Signal(str)
    error = Signal(str)


    def __init__(self, launch_minitor_names: list[str]) -> None:
        super().__init__()
        self._launch_minitor_names: List[str] = launch_minitor_names
        self._device: Union[Peripheral, None] = None
        self._adapter: Union[Adapter, None] = None
        self._timeout: datetime = datetime.datetime.now()
        self._is_active: bool = False
        self._rssi_only: bool = False
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._pause = Event()
        self._shutdown = Event()
        self.pause()
        self._thread.started.connect(self.__run)
        self._thread.start()

    @property
    def rssi_only(self, value: bool) -> None:
        self._rssi_only = value

    def __run(self) -> None:
        print('run')
        while not self._shutdown.is_set():
            self._pause.wait()
            # Start new scan, set pause so it will on execute once
            if not self._shutdown.is_set():
                self.pause()
                if self._is_active:
                    logging.debug("Already searching for device.")
                else:
                    try:
                        adapters = simplepyble.Adapter.get_adapters()
                        if len(adapters) <= 0:
                            raise Exception("No Bluetooth adapters found.")
                        self._adapter = adapters[0]
                        msg = f'Found {len(adapters)} Bluetooth adapters. {self._adapter.identifier()}'
                        print(msg)
                        logging.debug(msg)
                        self._adapter.set_callback_on_scan_start(self.__scanning_started)
                        self._adapter.set_callback_on_scan_stop(self.__scanning_finished())
                        self._adapter.set_callback_on_scan_updated(self.__add_device)
                        self._adapter.scan_start()
                        print('aft start scan')
                        self._timeout = datetime.datetime.now() + datetime.timedelta(seconds=BluetoothDeviceScannerSimpleBLE.SCANNER_TIMEOUT)
                    except Exception as e:
                        traceback.print_exc()
                        self.error.emit((e, traceback.format_exc()))

    def __stop_scanning(self) -> None:
        print('stop scanning')
        if self._adapter is not None and self._is_active:
            self._adapter.scan_stop()
            self._is_active = False
        if self._device is None:
            logging.debug('Timeout, no device found')
            self.status_update.emit('Timeout')
            self.device_not_found.emit()

    def __add_device(self, device: Peripheral) -> None:
        now = datetime.datetime.now()
        if now > self._timeout:
            print('stop scan timeout')
            self.__stop_scanning()
        else:
            print(f"Found {device.identifier()} [{device.address()}]")
            print(f'info: {device.identifier()} {device.identifier().startswith("MLM2-") or device.identifier().startswith("BlueZ ")}')
            if device.identifier() and any(device.identifier().startswith(name) for name in self._launch_minitor_names):
                self._device = device
                logging.debug(f'Launch monitor found: {self._device.identifier()} uuid: {device.address()}')
                print(f'Launch monitor found: {self._device.identifier()} uuid: {device.address()}')
                print('emit device found')
                self.status_update.emit('Device found')
                self.device_found.emit(self._device)
                self.__stop_scanning()

    def __scanning_finished(self) -> None:
        print('scanning finished')
        if self._device is None and self._is_active:
            self._is_active = False
            logging.debug('No device found')
            self.status_update.emit('No device found')
            self.device_not_found.emit()

    def __scanning_started(self) -> None:
        print('scanning started')
        logging.debug('Bluetooth device scan started')
        self.status_update.emit("Scanning for device...")
        self._is_active = True
        print('scanning started')
    
    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()

    def shutdown(self):
        print(f'{self.__class__.__name__} shutdown')
        self._shutdown.set()
        self._pause.set()
        self._thread.quit()
        self._thread.wait()
