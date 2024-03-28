from PySide6.QtCore import QObject, Signal
from bleak import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService

from src.bluetooth.bluetooth_client import BluetoothClient
from src.bluetooth.bluetooth_device import BluetoothDevice


class BluetoothAPIBase(QObject):
    HEARTBEAT_INTERVAL = 2

    error = Signal(str)

    def __init__(self, device: BluetoothDevice) -> None:
        super().__init__()
        self.device = device
        print(f'BluetoothAPIBase {device}')
        self.client = BluetoothClient(device)
        self.notifications = []
        self.service = None

    async def start(self):
        pass

    async def stop(self):
        pass

    def _get_service(self, uuid: str) -> BleakGATTService:
        self.service = self.client.get_service(uuid)
        return self.service

    async def _subscribe_to_characteristics(self):
        await self.client.subscribe_to_characteristics(self.notifications, self._notification_handler)

    def _notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        pass

