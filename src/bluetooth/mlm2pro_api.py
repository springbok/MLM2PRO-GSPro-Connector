from src.bluetooth.bluetooth_api_base import BluetoothAPIBase


class MLM2ProAPI(BluetoothAPIBase):

    def __init__(self):
        super().__init__()
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected