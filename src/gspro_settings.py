from src.settings_base import SettingsBase


class GSProSettings(SettingsBase):

    def __init__(self, app_paths):
        SettingsBase.__init__(self,
            app_paths.get_config_path(
                name='gspro_settings',
                ext='.json'
            ), {
                "ip_address": "127.0.0.1",
                "port": 921,
                "api_version": "1",
                "device_id": "Rapsodo MLM2PRO",
                "units": "Yards",
            }
        )
        # Removed this from the settings file, specifies the
        # number of ms between screenshots
        self.screenshot_interval = 500
