from bleak import BLEDevice, AdvertisementData

from src.bluetooth.mlm2pro_device import MLM2PRODevice
from src.device_launch_monitor_bluetooth_base import DeviceLaunchMonitorBluetoothBase


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
        mlm2pro_devide = MLM2PRODevice(device, advertised_data)

        #if self.client is not None:
        #    self.client.reset_connection()
        #    self.client = None
        #self.device_worker = WorkerDeviceLaunchMonitorBluetoothMLM2PRO(self.main_window.settings, self.api, device)
        #self.client = BluetoothClient()
        #self.client.connect_client(device)

    def start_message(self) -> str:
        return 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STEADY RED light is showing.'
