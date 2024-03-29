class BluetoothSignal:
    def __init__(self, connection_status, connection_color, device_message, device_color, button_message, button_enabled=True):
        self.connection_status = connection_status
        self.connection_color = connection_color
        self.device_message = device_message
        self.device_color = device_color
        self.button_message = button_message
        self.button_enabled = button_enabled

