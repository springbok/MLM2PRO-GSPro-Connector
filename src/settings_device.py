from src.settings_base import SettingsBase


class SettingsDevice(SettingsBase):

    def __init__(self, path, window_name, width, height):
        SettingsBase.__init__(self,
            path, {
                "window_name": window_name,
                "target_width": width,
                "target_height": height
            }
        )
