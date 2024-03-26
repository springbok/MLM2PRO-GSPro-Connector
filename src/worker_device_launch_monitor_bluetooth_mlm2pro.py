import logging
import traceback
from threading import Event
from src.screenshot_exputt import ScreenshotExPutt
from src.worker_device_launch_monitor_bluetooth_base import WorkerDeviceLaunchMonitorBluetoothBase
from src.settings import Settings


class WorkerDeviceLaunchMonitorBluetoothMLM2PRO(WorkerDeviceLaunchMonitorBluetoothBase):

    def __init__(self, settings: Settings, api):
        WorkerDeviceLaunchMonitorBluetoothBase.__init__(self, settings, api)
        self.putting_rois_reload = True
        self.settings = settings
        self.name = 'WorkerDeviceLaunchMonitorBluetoothMLM2PRO'
