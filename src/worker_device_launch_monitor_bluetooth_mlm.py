from dataclasses import dataclass

from PySide6.QtCore import Signal
from bleak import BLEDevice

from src.mlm2pro_bluetooth.api import MLM2PROAPI
from src.mlm2pro_bluetooth.client import MLM2PROClient
from src.mlm2pro_bluetooth.scanner import MLM2PROScanner
from src.worker_base import WorkerBase

@dataclass
class BluetoothStatus:
    NOT_CONNECTED = 'Not Connected'
    SCANNING = 'Scanning'
    NO_DEVICE_FOUND = 'No Device Found'


class WorkerDeviceLaunchMonitorBluetoothMLM(WorkerBase):

    no_device_found = Signal(str)
    scanning = Signal(str)

    def __init__(self):
        WorkerBase.__init__(self)
        self.device: BLEDevice = None
        self.mlm2pro_client = None
        self.mlm2pro_api = None
        self.mlm2pro_scanner = MLM2PROScanner()
        self.running = False

    async def __scan_for_mlm2pro(self) -> bool:
        if self.mlm2pro_scanner is None:
            self.mlm2pro_scanner = MLM2PROScanner()
        await self.mlm2pro_scanner.run()
        self.device = self.mlm2pro_scanner.device
        return (self.device is not None)

    async def stop_bluetooth(self) -> None:
        if self.mlm2pro_scanner is not None:
            self.mlm2pro_scanner.scanning.clear()
            self.mlm2pro_scanner = None
        if self.mlm2pro_api is not None:
            await self.mlm2pro_api.stop()
            self.mlm2pro_api = None
        if self.mlm2pro_client is not None:
            await self.mlm2pro_client.stop()
            self.mlm2pro_client = None
        self.running = False

    async def start_bluetooth(self) -> None:
        self.running = True
        print('start scan')
        self.scanning.emit(BluetoothStatus.SCANNING)
        await self.__scan_for_mlm2pro()
        if self.device is None:
            print('no device found')
            self.no_device_found.emit(BluetoothStatus.NO_DEVICE_FOUND)
            self.running = False
        else:
            self.mlm2pro_client = MLM2PROClient(self.device)
            await self.mlm2pro_client.start()
            print(self.mlm2pro_client.is_connected)
            if self.mlm2pro_client.is_connected:
                self.mlm2pro_api = MLM2PROAPI(self.mlm2pro_client)
                await self.mlm2pro_api.start()
                result = await self.mlm2pro_api.auth()
                print(f'result: {result}')
