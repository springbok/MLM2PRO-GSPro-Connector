import json
import logging
import os
from PySide6.QtWidgets import QMessageBox
from src.ball_data import BallData
from src.device_base import DeviceBase
from src.device_launch_monitor_relay_server_base import DeviceLaunchMonitorRelayServerBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_device_launch_monitor_relay_server import WorkerDeviceLaunchMonitorRelayServer


class DeviceLaunchMonitorRelayServerR10(DeviceLaunchMonitorRelayServerBase):

    app = '\\r10_bt_app\\gspro-r10.exe'
    default_window_name = 'GSP-R10 Connect'

    def __init__(self, main_window):
        DeviceLaunchMonitorRelayServerBase.__init__(self, main_window)
        self.launch_monitor_app = self.app
