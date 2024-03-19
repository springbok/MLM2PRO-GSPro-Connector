import os

from src.settings_base import SettingsBase

class MLM2PROBTSettings(SettingsBase):

    def __init__(self, app_paths):
        SettingsBase.__init__(self, os.cwd() + '\\mlm2pro_bt_app\\settings.json', {})


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
        if not hasattr(self, 'relay_server_window_name'):
            self.relay_server_window_name = ""
            save = True
        if save:
            super().save()

    def local_gspro(self):
        local = False
        if self.ip_address == '127.0.0.1' or self.ip_address == 'localhost':
            local = True
        return local
