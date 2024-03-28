from bleak import BLEDevice, AdvertisementData
from src.bluetooth.bluetooth_device import BluetoothDevice


class MLM2PRODevice(BluetoothDevice):

    def __init__(self, device: BLEDevice, advertised_data: AdvertisementData) -> None:
        super().__init__(device, advertised_data)
        self.altitude_metres = 0.0
        self.temperature_celsius = 15.0
