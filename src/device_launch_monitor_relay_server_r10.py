from src.device_launch_monitor_relay_server_base import DeviceLaunchMonitorRelayServerBase


class DeviceLaunchMonitorRelayServerR10(DeviceLaunchMonitorRelayServerBase):

    app = '\\r10_bt_app\\gspro-r10.exe'
    default_window_name = 'GSP-R10 Connect'

    def __init__(self, main_window):
        DeviceLaunchMonitorRelayServerBase.__init__(self, main_window)
        self.launch_monitor_app = self.app
