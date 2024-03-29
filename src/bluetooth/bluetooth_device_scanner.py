import asyncio
import logging
from PySide6.QtCore import QObject, Signal
from bleak import BleakScanner, BLEDevice, AdvertisementData

from src.bluetooth.bluetooth_signal import BluetoothSignal


class BluetoothDeviceScanner(QObject):
    TIMEOUT_SECONDS = 20

    device_found = Signal(BLEDevice, AdvertisementData)
    device_not_found = Signal()
    finished = Signal()
    started = Signal(BluetoothSignal)

    def __init__(self, launch_minitor_names: list[str]):
        super().__init__()
        self._scanner = BleakScanner(detection_callback=self.__detection_callback)
        self.device = None
        self._scanner_active = False
        self._scanning = asyncio.Event()
        self.launch_minitor_names = launch_minitor_names

    def __detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData) -> None:
        if self._scanning.is_set():
            print(f'Found Bluetooth device: {device}')
            if device.name and any(device.name.startswith(name) for name in self.launch_minitor_names):
                logging.debug(f"Device found: {device.name} {device.address} {advertisement_data}")
                print(f"Device found: {device.name} {device.address} {advertisement_data}")
                self.device = device
                self._scanning.clear()
                self.device_found.emit(device, advertisement_data)

    async def scan(self) -> None:
        if self._scanner_active:
            logging.debug("Already searching for devices.")
            return
        self.started.emit(BluetoothSignal('Scanning for device...', 'orange', 'No Device', 'red', 'Stop', False))
        self._scanner_active = True
        logging.debug(f'Searching for following launch monitor names: {self.launch_minitor_names}')
        logging.debug('Scanning for Bluetooth devices')
        await self._scanner.start()
        end_time = asyncio.get_event_loop().time() + BluetoothDeviceScanner.TIMEOUT_SECONDS
        self._scanning.set()
        while self._scanning.is_set():
            if asyncio.get_event_loop().time() > end_time:
                self._scanning.clear()
                logging.debug('Timeout while scanning for devices, no devices found.')
            await asyncio.sleep(0.1)
        await self._scanner.stop()
        self._scanner_active = False
        if self.device is None:
            self.device_not_found.emit()
        self.finished.emit()

    async def stop_scanning(self) -> None:
        self._scanning.clear()
        logging.debug('Scanning stopped')
