from bleak import BLEDevice, AdvertisementData


class BluetoothDevice:

    def __init__(self, device: BLEDevice, advertised_data: AdvertisementData) -> None:
        self.device = device
        self.advertised_data = advertised_data
