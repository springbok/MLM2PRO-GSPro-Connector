import asyncio

from bleak import BLEDevice

from src.mlm2pro_bluetooth.api import MLM2PROAPI
from src.mlm2pro_bluetooth.client import MLM2PROClient
from src.mlm2pro_bluetooth.scanner import MLM2PROScanner


class MLM2PROBluetoothManager:

    def __init__(self):
        self.device: BLEDevice = None
        self.mlm2pro_client = None
        self.mlm2pro_api = None
        self.mlm2pro_scanner = MLM2PROScanner()

    async def scan_for_mlm2pro(self) -> bool:
        if self.mlm2pro_scanner is None:
            self.mlm2pro_scanner = MLM2PROScanner()
        loop = asyncio.get_event_loop()
        await self.mlm2pro_scanner.run()
        self.device = self.mlm2pro_scanner.device
        return (self.device is not None)

    async def stop(self) -> None:
        if self.mlm2pro_scanner is not None:
            self.mlm2pro_scanner.scanning.clear()
            self.mlm2pro_scanner = None
        if self.mlm2pro_api is not None:
            await self.mlm2pro_api.stop()
            self.mlm2pro_api = None
        if self.mlm2pro_client is not None:
            await self.mlm2pro_client.stop()
            self.mlm2pro_client = None

    async def start(self) -> None:
        print('manager start')
        await self.scan_for_mlm2pro()
        if self.device is None:
            raise Exception('MLM2PRO not found, please ensure it is turned on and a steady red light is showing.')
        self.mlm2pro_client = MLM2PROClient(self.device)
        await self.mlm2pro_client.start()
        print(self.mlm2pro_client.is_connected)
        if self.mlm2pro_client.is_connected:
            self.mlm2pro_api = MLM2PROAPI(self.mlm2pro_client)
            await self.mlm2pro_api.start()
            result = await self.mlm2pro_api.auth()
            print(f'result: {result}')
