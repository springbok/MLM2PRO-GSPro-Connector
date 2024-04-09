import datetime
import logging
import traceback
from threading import Event
from typing import List, Union

import simplepyble
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication
from simplepyble import Peripheral, Adapter


class BluetoothClientSimpleBLE(QObject):
    SCANNER_TIMEOUT = 40
    
    connected = Signal()
    disconnected = Signal()
    error = Signal(tuple)


    def __init__(self, device: Peripheral) -> None:
        super().__init__()
        self._ble_device: Peripheral = device
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._pause = Event()
        self._shutdown = Event()
        self.pause()
        self._thread.started.connect(self.__run)
        self._thread.start()

    def __run(self) -> None:
        print('run')
        while not self._shutdown.is_set():
            self._pause.wait()
            # Start new scan, set pause so it will on execute once
            if not self._shutdown.is_set():
                self.pause()
                try:
                    print(f'Connecting to {self._ble_device.identifier()}')
                    self._ble_device.set_callback_on_connected(self.__connected)
                    self._ble_device.set_callback_on_disconnected(self.__disconnected)
                    self._ble_device.connect()
                except Exception as e:
                    traceback.print_exc()
                    self.error.emit((e, traceback.format_exc()))

    def __connected(self) -> None:
        msg = f'Connected to {self._ble_device.identifier()} {self._ble_device.address()}'
        print(msg)
        logging.debug(msg)
        Event().wait(1)
        self.connected.emit()

    def __disconnected(self) -> None:
        msg = f'Disconnected'
        print(msg)
        logging.debug(msg)
        self.disconnected.emit()

    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()

    def shutdown(self):
        print('client shutdown')
        self._shutdown.set()
        self._pause.set()
        self._thread.quit()
        self._thread.wait()
        self._thread.deleteLater()
        print('after client shutdown')
