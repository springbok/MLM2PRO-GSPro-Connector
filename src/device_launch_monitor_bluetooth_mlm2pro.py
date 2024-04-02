from PySide6.QtBluetooth import QBluetoothDeviceInfo

from src.bluetooth.bluetooth_client import BluetoothClient
from src.bluetooth.mlm2pro_device import MLM2PRODevice, TokenExpiryStates
from src.device_launch_monitor_bluetooth_base import DeviceLaunchMonitorBluetoothBase
from src.worker_device_launch_monitor_bluetooth_mlm2pro import WorkerDeviceLaunchMonitorBluetoothMLM2PRO


class DeviceLaunchMonitorBluetoothMLM2PRO(DeviceLaunchMonitorBluetoothBase):

    MLM2PRO_NAME_PREFIX = "MLM2-"
    BLUEZ_NAME_PREFIX = "BlueZ"

    def __init__(self, main_window):
        device_names = [DeviceLaunchMonitorBluetoothMLM2PRO.MLM2PRO_NAME_PREFIX,
                        DeviceLaunchMonitorBluetoothMLM2PRO.BLUEZ_NAME_PREFIX]
        #device_names = ['KICKR']
        DeviceLaunchMonitorBluetoothBase.__init__(self, main_window=main_window, device_names=device_names)
        self.api = 'x'

    def device_found(self, device: QBluetoothDeviceInfo) -> None:
        super().device_found(device)
        if self.device is not None:
            self.device.disc()
            self.device = None
        self.device = MLM2PRODevice(device)
        self._setup_device_signals()
        self.device.connect_device()


        #super().device_found(device)

    @property
    def start_message(self) -> str:
        return 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STEADY RED light is showing.'

    def _setup_device_signals(self) -> None:
        super()._setup_device_signals()
        self.device.token_expiry.connect(self.__token_expiry_status)

    def __token_expiry_status(self, status: TokenExpiryStates, token_expiry_date: str) -> None:
        self.main_window.token_expiry_label.setText(f"3rd Party: {token_expiry_date}")
        self.main_window.token_expiry_label.setStyleSheet(f"QLabel {{ background-color : {status}; color : white; }}")

