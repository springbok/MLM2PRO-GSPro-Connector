from PySide6.QtWidgets import QMessageBox

from src.device_launch_monitor_bluetooth_base import DeviceLaunchMonitorBluetoothBase
from src.worker_device_launch_monitor_bluetooth_mlm2pro import WorkerDeviceLaunchMonitorBluetoothMLM2PRO


class DeviceLaunchMonitorBluetoothMLM2PRO(DeviceLaunchMonitorBluetoothBase):

    def __init__(self, main_window):
        DeviceLaunchMonitorBluetoothBase.__init__(self, main_window=main_window, api='', )

    def server_start_stop(self):
        if self.device_worker is None:
            QMessageBox.warning(self.main_window, "Prepare Launch Monitor", 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STREADY RED light is showing.')
            self.device_worker = WorkerDeviceLaunchMonitorBluetoothMLM2PRO(self.main_window.settings, self.api)
            self.setup_device_thread()
            self.device_worker.start()
            self.setup_worker_signal()
        else:
            self.device_worker.stop()
            self.shutdown()
            self.not_connected_status()
