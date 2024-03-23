import os

from src.settings_base import SettingsBase

class R10BTSettings(SettingsBase):

    def __init__(self, app_paths):
        path = os.getcwd() + '\\r10_bt_app\\settings.json'
        SettingsBase.__init__(self, path, {})


    def load(self):
        self.create()
        logging.debug(f"Loading settings from {self.path}")
        if os.path.isfile(self.path):
            with open(self.path, "r") as file:
                lines = file.readlines()
                cleaned_lines = [line.split("//")[0].strip() for line in lines if not line.strip().startswith("//")]
                cleaned_json = "\n".join(cleaned_lines)
                settings = json.loads(cleaned_json)
        else:
            raise RuntimeError(f"Could not open settings file: {self.path}")
        logging.debug(f"Setting in {self.path}: {settings}")
        # Create dynamic attributes
        for key in settings:
            setattr(self, key, settings[key])
