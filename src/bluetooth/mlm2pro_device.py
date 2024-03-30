from PySide6.QtBluetooth import QBluetoothDeviceInfo
from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase


class MLM2PRODevice(BluetoothDeviceBase):
    def __init__(self, device: QBluetoothDeviceInfo):
        super().__init__(device)
        self.user_token = "0"
        self.ball_type = 2
        self.altitude_metres = 0.0
        self.temperature_celsius = 15.0