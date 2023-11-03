from dataclasses import dataclass

from src.settings_base import SettingsBase


@dataclass
class LaunchMonitor:
    MLM2PRO = "Rapsodo MLM2PRO"
    MEVOPLUS = "MEVO+"


class Settings(SettingsBase):

    def __init__(self, app_paths):
        SettingsBase.__init__(self,
            app_paths.get_config_path(
                name='settings',
                ext='.json'
            ), {
                "ip_address": "127.0.0.1",
                "port": 921,
                "api_version": "1",
                "device_id": "Rapsodo MLM2PRO",
                "units": "Yards",
                "gspro_path": "",
                "grspo_window_name": "GSPro",
                "gspro_api_window_name": "APIv1 Connect"
            }
        )
        # Removed this from the settings file, specifies the
        # number of ms between screenshots
        self.screenshot_interval = 250
