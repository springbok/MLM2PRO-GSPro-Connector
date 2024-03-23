import logging
import os

from src.settings_base import SettingsBase

class MLM2PROBTSettings(SettingsBase):

    def __init__(self, app_paths):
        path = os.getcwd() + '\\mlm2pro_bt_app\\settings.json'
        SettingsBase.__init__(self, path, {})
