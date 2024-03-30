from PySide6.QtBluetooth import QBluetoothDeviceInfo


class BluetoothUtils:

    @staticmethod
    def get_sensor_remote_address(device) -> str:
        sensor_remote_address = ""
        device.remoteAddress().toString()
        return sensor_remote_address

    staticmethod
    def get_sensor_address(sensor: QBluetoothDeviceInfo) -> str:
        sensor_address = sensor.address().toString()
