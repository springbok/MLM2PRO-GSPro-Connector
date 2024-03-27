import asyncio
import logging
from threading import Event

from PySide6.QtCore import QObject, Signal
from bleak import BleakScanner, BLEDevice, AdvertisementData


class DeviceScanner(QObject):
    TIMEOUT_SECONDS = 20

    device_update = Signal(object)
    status_update = Signal(str)
    error = Signal(str)

    def __init__(self, launch_minitor_names: list[str]):
        super().__init__()
        self._scanner = BleakScanner(detection_callback=self.__detection_callback)
        self._shutdown = Event()
        self.device = None
        self._scanner_active = False
        self.launch_minitor_names = launch_minitor_names

    def __detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData) -> None:
        print(f'Found Bluetooth device: {device}')
        if device.name and any(device.name.startswith(name) for name in self.launch_minitor_names):
            logging.debug(f"Device found: {device.name} {device.address} {advertisement_data}")
            self.device = device
            self.stop_scanning()

    async def scan(self) -> None:
        if self._scanner_active:
            logging.debug("Already searching for devices.")
            return
        self._scanner_active = True
        logging.debug(f'Searching for following launch monitor names: {self.launch_minitor_names}')
        self.status_update.emit("Scanning...")
        logging.debug('Scanning for Bluetooth devices')
        await self._scanner.start()
        end_time = asyncio.get_event_loop().time() + DeviceScanner.TIMEOUT_SECONDS
        while not self._shutdown.is_set():
            if asyncio.get_event_loop().time() > end_time:
                self.stop_scanning()
                logging.debug('Timeout while scanning for devices, no devices found.')
            await asyncio.sleep(0.1)
        await self._scanner.stop()

    def stop_scanning(self) -> None:
        self._shutdown.set()
        self._scanner_active = False
        logging.debug('Scanning stopped')
