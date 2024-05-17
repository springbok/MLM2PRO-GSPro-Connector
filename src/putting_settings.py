from dataclasses import dataclass

from src.settings_base import SettingsBase

@dataclass
class PuttingSystems:
    EXPUTT = 'ExPutt'
    WEBCAM = 'Webcam'
    NONE = 'None'

@dataclass
class WebcamWindowFocus:
    PUTTING_WINDOW = 'PuttingWindow'
    GSPRO = 'GSPRO'

@dataclass
class WebcamWindowState:
    HIDE = 'Hide'
    MINIMIZE = 'Minimize'
    SEND_TO_BACK = 'SendToBack'
    SHOW = 'Show'

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
                    "width": 640,
                    "params": "",
                    "window_putting_focus": "PuttingWindow",
                    "window_not_putting_state": "SendToBack"
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

    def load(self):
        super().load()
        save = False
        if 'width' not in self.webcam:
            self.webcam['width'] = 640
            save = True
        if 'window_putting_focus' not in self.webcam:
            self.webcam['window_putting_focus'] = WebcamWindowFocus.GSPRO
            save = True
        if 'window_not_putting_state' not in self.webcam:
            self.webcam['window_not_putting_state'] = WebcamWindowState.SEND_TO_BACK
            save = True
        if save:
            super().save()

    def width(self):
        return self.exputt['window_rect']['right'] - self.exputt['window_rect']['left']

    def height(self):
        return self.exputt['window_rect']['bottom'] - self.exputt['window_rect']['top']

    @staticmethod
    def webcam_window_focus_as_list():
        keys = []
        for key in WebcamWindowFocus.__dict__:
            if key != '__' not in key:
                keys.append(getattr(WebcamWindowFocus, key))
        return keys

    @staticmethod
    def webcam_window_state_as_list():
        keys = []
        for key in WebcamWindowState.__dict__:
            if key != '__' not in key:
                keys.append(getattr(WebcamWindowState, key))
        return keys
