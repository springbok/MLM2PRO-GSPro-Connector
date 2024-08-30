from dataclasses import dataclass

from src.settings_base import SettingsBase


@dataclass
class LaunchMonitor:
    MLM2PRO = "Rapsodo MLM2PRO"
    MLM2PRO_BT = 'Rapsodo MLM2PRO BT'
    R10_BT = "Garmin R10 BT"
    FSKIT = "Fullswing Kit"
    MEVOPLUS = "MEVO+"
    TRACKMAN = "Trackman"
    TRUGOLF_APOGEE = "TruGolf Apogee"
    RELAY_SERVER = "Relay Server"


class Settings(SettingsBase):
    version = "2"

    def __init__(self, app_paths):
        SettingsBase.__init__(self,
            app_paths.get_config_path(
                name='settings',
                ext='.json'
            ), {
                "ip_address": "127.0.0.1",
                "port": 921,
                "api_version": "1",
                "device_id": "Rapsodo MLM2PRO BT",
                "units": "Yards",
                "gspro_path": "",
                "grspo_window_name": "GSPro",
                "gspro_api_window_name": "APIv1 Connect",
                "gspro_config_window_name": "GSPro Configuration",
                "gspro_play_button_label": "Play!",
                "default_device": "None",
                "create_debug_images": "No",
                "colour_threshold": 180,
                "zoom_images": "No",
                "relay_server_ip_address": "127.0.0.1",
                "relay_server_port": 9234,
                'auto_start_all_apps': 'No'
            }
        )
        # Removed this from the settings file, specifies the
        # number of ms between screenshots
        self.screenshot_interval = 250

    def load(self):
        super().load()
        save = False
        if not hasattr(self, 'gspro_config_window_name'):
            self.gspro_config_window_name = "GSPro Configuration"
            save = True
        if not hasattr(self, 'gspro_play_button_label'):
            self.gspro_play_button_label = "Play!"
            save = True
        if not hasattr(self, 'create_debug_images'):
            self.create_debug_images = "No"
            save = True
        if not hasattr(self, 'zoom_images'):
            self.zoom_images = "No"
            save = True
        if not hasattr(self, 'colour_threshold'):
            self.colour_threshold = 180
            save = True
        if not hasattr(self, 'settings_version'):
            self.settings_version = Settings.version
            save = True
        if not hasattr(self, 'relay_server_ip_address'):
            self.relay_server_ip_address = "127.0.0.1"
            save = True
        if not hasattr(self, 'relay_server_port'):
            self.relay_server_port = 9234
            save = True
        if not hasattr(self, 'auto_start_all_apps'):
            value = 'No'
            if hasattr(self, 'default_device') and self.default_device != 'None':
                value = 'Yes'
            self.auto_start_all_apps = value
            save = True
        if not hasattr(self, 'web_api'):
            self.web_api = {
                "url": "https://mlm.rapsodo.com/api/simulator/user/",
                "secret": "b78d7771e5fa9a0fdb59e818bf5ff557d98e3775489fd6a9c9d961637ed3ee7054a6d387f681078ea8c5c8bbd257fb24f3f778b8b7bd820c410d43e3db284030c9b5802d9190dc2f68c5874f71294a6d",
                "token": "",
                "user_id": 0,
                "token_expiry": 0,
                "device_id": 0
            }
            save = True
        if not hasattr(self, 'r10_bluetooth'):
            self.r10_bluetooth = {
                "device_name": "Approach R10",
                "altitude": 0,
                "humidity": 0.5,
                "temperature": 60,
                "air_density": 1.225,
                "tee_distance": 7
            }
            save = True
        if not hasattr(self, 'mevo_plus'):
            self.mevo_plus = {
                "offline_mode": "Yes"
            }
            save = True
        if save:
            super().save()

    def local_gspro(self):
        local = False
        if self.ip_address == '127.0.0.1' or self.ip_address == 'localhost':
            local = True
        return local
