import asyncio
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
        print(f'detection_callback: {device}')
        if device.name and (device.name.startswith(MLM2PROScanner.MLM2PRO_NAME_PREFIX) or device.name.startswith(MLM2PROScanner.BLUEZ_NAME_PREFIX)):
            print(f"{device.name} {device.address} {advertisement_data}")
            print(f"Device found: {device.name}")
            self.device = device
            self.scanning.clear()

    async def run(self):
        await self._scanner.start()
        self.scanning.set()
        end_time = asyncio.get_event_loop().time() + MLM2PROScanner.timeout_seconds
        while self.scanning.is_set():
            if asyncio.get_event_loop().time() > end_time:
                self.scanning.clear()
                print('Scan has timed out, no device found')
            await asyncio.sleep(0.1)
        await self._scanner.stop()
