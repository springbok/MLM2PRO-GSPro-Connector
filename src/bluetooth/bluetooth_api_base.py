from PySide6.QtCore import QObject
from bleak.backends.service import BleakGATTService

from src.bluetooth.bluetooth_client import BluetoothClient
from src.bluetooth.bluetooth_device import BluetoothDevice


class BluetoothAPIBase(QObject):
    HEARTBEAT_INTERVAL = 2

    def __init__(self, device: BluetoothDevice) -> None:
        self.device = device
        print(f'BluetoothAPIBase {device}')
        self.client = BluetoothClient(device)
        self.notifications = []
        self.service = None

    async def start(self):
        pass

    async def stop(self):
        pass

    async def _get_service(self, uuid: str) -> BleakGATTService:
        self.service = self.client.bleak_client.services.get_service(uuid)
        return self.service