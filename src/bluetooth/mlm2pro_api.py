from src.bluetooth.bluetooth_api_base import BluetoothAPIBase
from src.bluetooth.mlm2pro_device import MLM2PRODevice


class MLM2PROAPI(BluetoothAPIBase):

    def __init__(self, device: MLM2PRODevice):
        super().__init__(device)