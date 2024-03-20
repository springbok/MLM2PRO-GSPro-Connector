import os

from src.settings_base import SettingsBase

class R10BTSettings(SettingsBase):

    def __init__(self, app_paths):
        path = os.getcwd() + '\\r10_bt_app\\settings.json'
        SettingsBase.__init__(self, path, {})

