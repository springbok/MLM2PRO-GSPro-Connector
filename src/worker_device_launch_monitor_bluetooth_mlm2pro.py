import logging
import traceback
from threading import Event
from src.screenshot_exputt import ScreenshotExPutt
from src.worker_device_launch_monitor_bluetooth_base import WorkerDeviceLaunchMonitorBluetoothBase
from src.settings import Settings


class WorkerDeviceLaunchMonitorBluetoothMLM2PRO(WorkerDeviceLaunchMonitorBluetoothBase):
    MLM2PRO_NAME_PREFIX = "MLM2-"
    BLUEZ_NAME_PREFIX = "BlueZ"

    def __init__(self, settings: Settings, api):
        #device_name = [WorkerDeviceLaunchMonitorBluetoothMLM2PRO.MLM2PRO_NAME_PREFIX,
        #                WorkerDeviceLaunchMonitorBluetoothMLM2PRO.BLUEZ_NAME_PREFIX]
        device_name = ['KICKR']
        WorkerDeviceLaunchMonitorBluetoothBase.__init__(self, settings, api, device_name)
        self.putting_rois_reload = True
        self.settings = settings
        self.name = 'WorkerDeviceLaunchMonitorBluetoothMLM2PRO'
