from typing import Union

from PySide6.QtBluetooth import QBluetoothDeviceInfo
from simplepyble import Peripheral

from src.bluetooth.bluetooth_device_base_qtbluetooth import BluetoothDeviceBaseQtBluetooth
from src.bluetooth.bluetooth_device_base_simpleble import BluetoothDeviceBaseSimpleBLE
from src.bluetooth.mlm2pro_device import TokenExpiryStates, get_device_class
from src.device_launch_monitor_bluetooth_base import DeviceLaunchMonitorBluetoothBase


class DeviceLaunchMonitorBluetoothMLM2PRO(DeviceLaunchMonitorBluetoothBase):

    MLM2PRO_NAME_PREFIX = "MLM2-"
    BLUEZ_NAME_PREFIX = "BlueZ"

    def __init__(self, main_window):
        device_names = [DeviceLaunchMonitorBluetoothMLM2PRO.MLM2PRO_NAME_PREFIX,
                        DeviceLaunchMonitorBluetoothMLM2PRO.BLUEZ_NAME_PREFIX]
        DeviceLaunchMonitorBluetoothBase.__init__(self, main_window=main_window, device_names=device_names)
        self.api = 'x'

    def device_found(self, device: Union[QBluetoothDeviceInfo, Peripheral]) -> None:
        super().device_found(device)
        self._device = None
        if device.__class__ == QBluetoothDeviceInfo:
            device_class = get_device_class(BluetoothDeviceBaseQtBluetooth)
        else:
            print(f'{self.__class__.__name__} create base BluetoothDeviceBaseSimpleBLE')
            device_class = get_device_class(BluetoothDeviceBaseSimpleBLE)
        self._device = device_class(device)
        self._setup_device_signals()
        self._device.connect_device()

    @property
    def start_message(self) -> str:
        return 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STEADY RED light is showing.'

    def _setup_device_signals(self) -> None:
        super()._setup_device_signals()
        self._device.token_expiry.connect(self.__token_expiry_status)
        self._device.launch_monitor_event.connect(self.__launch_monitor_event)

    def __launch_monitor_event(self, event: str) -> None:
        self.main_window.launch_monitor_event_label.setText(f"LM: {event}")
        self.main_window.launch_monitor_event_label.setStyleSheet(f"QLabel {{ background-color : blue; color : white; }}")

    def __token_expiry_status(self, status: TokenExpiryStates, token_expiry_date: str) -> None:
        self.main_window.token_expiry_label.setText(f"Auth: {token_expiry_date}")
        self.main_window.token_expiry_label.setStyleSheet(f"QLabel {{ background-color : {status}; color : white; }}")
