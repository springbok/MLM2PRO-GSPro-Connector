from PySide6.QtBluetooth import QBluetoothDeviceInfo
from src.worker_device_launch_monitor_bluetooth_base import WorkerDeviceLaunchMonitorBluetoothBase
from src.settings import Settings


class WorkerDeviceLaunchMonitorBluetoothMLM2PRO(WorkerDeviceLaunchMonitorBluetoothBase):

    def __init__(self, settings: Settings, api, device: QBluetoothDeviceInfo):
        WorkerDeviceLaunchMonitorBluetoothBase.__init__(self, settings, api, device)
        self.name = 'WorkerDeviceLaunchMonitorBluetoothMLM2PRO'
