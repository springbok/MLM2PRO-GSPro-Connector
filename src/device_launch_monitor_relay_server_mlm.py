from src.device_launch_monitor_relay_server_base import DeviceLaunchMonitorRelayServerBase
from src.auto_click import clickButtonByHwnd, searchButton
from threading import Event

class DeviceLaunchMonitorRelayServerMLM(DeviceLaunchMonitorRelayServerBase):

    app = '\\mlm2pro_bt_app\\MLM2PRO-BT-APP.exe'
    default_window_name = 'MLM2PRO Bluetooth Connector'

    def __init__(self, main_window):
        DeviceLaunchMonitorRelayServerBase.__init__(self, main_window)
        self.launch_monitor_app = self.app
