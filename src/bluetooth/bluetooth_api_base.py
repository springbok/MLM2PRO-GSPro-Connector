from PySide6.QtCore import QObject

from src.bluetooth.bluetooth_client import BluetoothClient
from src.bluetooth.bluetooth_device import BluetoothDevice


class BluetoothAPIBase(QObject):

    def __init__(self, device: BluetoothDevice) -> None:
        self.device = device
        print(f'BluetoothAPIBase {device}')
        self.client = BluetoothClient(device)

    async def start(self):
        print('aaaa start')
        await self.client.client_connect()

    async def stop(self):
        print('bbbbb stop')
        await self.client.client_disconnect()