class BluetoothUtils:

    @staticmethod
    def get_sensor_remote_address(device) -> str:
        sensor_remote_address = ""
        device.remoteAddress().toString()
        return sensor_remote_address