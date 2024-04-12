from typing import Optional

from PySide6.QtBluetooth import QBluetoothDeviceInfo

from src.bluetooth.r10_device import R10Device
from src.device_launch_monitor_bluetooth_base import DeviceLaunchMonitorBluetoothBase


class DeviceLaunchMonitorBluetoothR10(DeviceLaunchMonitorBluetoothBase):

    R10_NAME_PREFIX = " R10"

    def __init__(self, main_window):
        device_names = [DeviceLaunchMonitorBluetoothR10.R10_NAME_PREFIX]
        DeviceLaunchMonitorBluetoothBase.__init__(self, main_window=main_window, device_names=device_names)
        self._device: Optional[R10Device] = None

    def device_found(self, device: QBluetoothDeviceInfo) -> None:
        super().device_found(device)
        if self._device is not None:
            self._device.disconnect_device()
            self._device.shutdown()
            self._device = None
        self._device = R10Device(device)
        self._setup_device_signals()
        self._device.connect_device()

    @property
    def start_message(self) -> str:
        return 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STEADY RED light is showing.'
