from dataclasses import dataclass

from src.settings_base import SettingsBase


@dataclass
class LaunchMonitor:
    MLM2PRO = "Rapsodo MLM2PRO"
    MEVOPLUS = "MEVO+"
    R10 = "R10"


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
                "api_version": "2",
                "device_id": "Rapsodo MLM2PRO",
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
                "r10_connector_ip_address": "127.0.0.1",
                "r10_connector_port": 9234,
                "r10_connector_path": ""
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
        if not hasattr(self, 'r10_connector_ip_address'):
            self.r10_connector_ip_address = "127.0.0.1"
            save = True
        if not hasattr(self, 'r10_connector_port'):
            self.r10_connector_port = 9234
            save = True
        if not hasattr(self, 'r10_connector_path'):
            self.r10_connector_path = ""
            save = True
        if save:
            super().save()

    def local_gspro(self):
        local = False
        if self.ip_address == '127.0.0.1' or self.ip_address == 'localhost':
            local = True
        return local
