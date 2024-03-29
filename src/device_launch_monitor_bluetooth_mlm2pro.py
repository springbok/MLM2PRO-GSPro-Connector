import traceback

from bleak import BLEDevice, AdvertisementData

from src.bluetooth.mlm2pro_device import MLM2PRODevice
from src.device_launch_monitor_bluetooth_base import DeviceLaunchMonitorBluetoothBase
from src.bluetooth.mlm2pro_api import MLM2PROAPI

class DeviceLaunchMonitorBluetoothMLM2PRO(DeviceLaunchMonitorBluetoothBase):

    MLM2PRO_NAME_PREFIX = "MLM2-"
    BLUEZ_NAME_PREFIX = "BlueZ "

    def __init__(self, main_window):
        device_names = [DeviceLaunchMonitorBluetoothMLM2PRO.MLM2PRO_NAME_PREFIX,
                        DeviceLaunchMonitorBluetoothMLM2PRO.BLUEZ_NAME_PREFIX]
        #device_names = ['KICKR']
        DeviceLaunchMonitorBluetoothBase.__init__(self, main_window=main_window, device_names=device_names)

    def _device_found(self, device: BLEDevice, advertised_data: AdvertisementData) -> None:
        print(f'_device_found derived: {device.name}')
        super()._device_found(device, advertised_data)
        mlm2pro_device = MLM2PRODevice(device, advertised_data)
        self.api = MLM2PROAPI(mlm2pro_device)
        self._setup_api_signals()
        self._start_api()

    @property
    def _start_message(self) -> str:
        return 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STEADY RED light is showing.'
