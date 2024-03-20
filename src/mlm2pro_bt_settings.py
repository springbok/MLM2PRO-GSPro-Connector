import logging
import os

from src.settings_base import SettingsBase

class MLM2PROBTSettings(SettingsBase):

    def __init__(self, app_paths):
        path = os.getcwd() + '\\mlm2pro_bt_app\\settings.json'
        SettingsBase.__init__(self, path, {})

    def load(self):
        self.create()
        logging.debug(f"Loading settings from {self.path}")
        if os.path.isfile(self.path):
            settings = self.read_json_file()
        else:
            raise RuntimeError(f"Could not open settings file: {self.path}")
        logging.debug(f"Setting in {self.path}: {settings}")
        # Create dynamic attributes
        for key in settings:
            setattr(self, key, settings[key])
