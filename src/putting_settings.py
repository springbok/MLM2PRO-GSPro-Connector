from dataclasses import dataclass

from src.settings_base import SettingsBase

@dataclass
class PuttingSystems:
    EXPUTT = 'ExPutt'
    WEBCAM = 'Webcam'
    NONE = 'None'


class PuttingSettings(SettingsBase):

    def __init__(self, app_paths):
        SettingsBase.__init__(self,
            app_paths.get_config_path(
                name='putting_settings',
                ext='.json'
            ), {
                "system": "None",
                "webcam": {
                    "camera": 0,
                    "ball_color": "yellow",
                    "window_name": "Putting View: Press q to exit / a for adv. settings",
                    "ip_address": "127.0.0.1",
                    "port": 8888,
                    "auto_start": "Yes",
                    "params": ""
                },
                "exputt": {
                    "window_name": "Camera",
                    "window_rect": {
                        "left": 0,
                        "top": 0,
                        "right": 0,
                        "bottom": 0
                    },
                    "auto_start": "Yes",
                    "rois": {}
                }
            }
        )

    def width(self):
        return self.exputt['window_rect']['right'] - self.exputt['window_rect']['left']

    def height(self):
        return self.exputt['window_rect']['bottom'] - self.exputt['window_rect']['top']
