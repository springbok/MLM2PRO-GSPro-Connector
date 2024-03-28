from bleak import BLEDevice, AdvertisementData
from src.bluetooth.bluetooth_device import BluetoothDevice
from src.bluetooth.bluetooth_utils import BluetoothUtils


class MLM2PRODevice(BluetoothDevice):

    def __init__(self, device: BLEDevice, advertised_data: AdvertisementData) -> None:
        super().__init__(device, advertised_data)
        self.altitude_metres = 0.0
        self.temperature_celsius = 15.0

    def get_initial_parameters(self, token_input):
        self.user_token = token_input
        print("GetInitialParameters: UserToken: " + self.user_token)

        # Generate required byte arrays
        air_pressure_bytes = BluetoothUtils.get_air_pressure_bytes(0.0)
        temperature_bytes = BluetoothUtils.get_temperature_bytes(self.temperature_celsius)
        long_to_uint_to_byte_array = BluetoothUtils.long_to_uint_to_byte_array(int(self.user_token), True)

        # Concatenate all byte arrays
        concatenated_bytes = bytearray([1, 2, 0, 0]) + air_pressure_bytes + temperature_bytes + long_to_uint_to_byte_array + bytearray([0, 0])

        print("GetInitialParameters: ByteArrayReturned: " + BluetoothUtils.byte_array_to_hex_string(concatenated_bytes))
        return concatenated_bytes
