import asyncio
import logging

from bleak import BleakScanner, BLEDevice, AdvertisementData


class MLM2PROScanner:
    timeout_seconds = 20
    MLM2PRO_NAME_PREFIX = "MLM2-"
    BLUEZ_NAME_PREFIX = "BlueZ"

    def __init__(self):
        self._scanner = BleakScanner(detection_callback=self.__detection_callback)
        self.scanning = asyncio.Event()
        self.device = None

    def __detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        print(f'Found Bluetooth device: {device}')
        if device.name and (device.name.startswith(MLM2PROScanner.MLM2PRO_NAME_PREFIX) or device.name.startswith(MLM2PROScanner.BLUEZ_NAME_PREFIX)):
            logging.debug(f"Device found: {device.name} {device.address} {advertisement_data}")
            self.device = device
            self.scanning.clear()

    async def run(self):
        logging.debug('Scanning for Bluetooth devices')
        await self._scanner.start()
        self.scanning.set()
        end_time = asyncio.get_event_loop().time() + MLM2PROScanner.timeout_seconds
        while self.scanning.is_set():
            if asyncio.get_event_loop().time() > end_time:
                self.scanning.clear()
                logging.debug('Timeout while scanning for MLM2PRO device, no devices found.')
            await asyncio.sleep(0.5)
        await self._scanner.stop()
