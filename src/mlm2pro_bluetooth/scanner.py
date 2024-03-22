import asyncio
import struct

from bleak import BleakScanner


class DeviceScanner:
    timeout_seconds = 20

    def __init__(self):
        self._scanner = BleakScanner(detection_callback=self.__detection_callback)
        self.scanning = asyncio.Event()
        self.device = None

    def __detection_callback(self, device, advertisement_data):
        if device is not None and device.name.startswith("MLM2-") or device.name.startswith("BlueZ ") or device.name.startswith("KICKR CORE "):
            print(f"{device.name} {device.address} {advertisement_data}")
            print(f"Device found: {device.name}")
            self.device = device
            self.scanning.clear()

    async def run(self, loop):
        await self._scanner.start()
        self.scanning.set()
        end_time = loop.time() + DeviceScanner.timeout_seconds
        while self.scanning.is_set():
            if loop.time() > end_time:
                self.scanning.clear()
                print('\t\tScan has timed out so we terminate')
            await asyncio.sleep(0.1)
        await self._scanner.stop()
