import json
import os
import logging
import multiline


class Settings:

    def __init__(self, app_paths):
        self.path = app_paths.get_config_path(
            name='settings',
            ext='.json'
        )
        self.settings_json = {
            "GSPRO": {
                "IP_ADDRESS": "127.0.0.1",
                "PORT": 921,
                "API_VERSION": "1",
                "DEVICE_ID": "Rapsodo MLM2PRO",
                "UNITS": "Yards"
            },
            "WINDOW_NAME": "AirPlay",
            "TARGET_WIDTH": 1638,
            "TARGET_HEIGHT": 752,
            "SCREENSHOT_INTERVAL": 500
        }
        self.__create()
        self.__load()

    def __load(self):
        logging.debug(f"Loading settings from {self.path}")
        if os.path.isfile(self.path):
            with open(self.path, "r") as file:
                lines = file.readlines()
                cleaned_lines = [line.split("//")[0].strip() for line in lines if not line.strip().startswith("//")]
                cleaned_json = "\n".join(cleaned_lines)
                settings = json.loads(cleaned_json)
        else:
            raise RuntimeError(f"Could not open settings file: {self.path}")
        logging.debug(f"Setting: {settings}")
        # Create dynamic attributes
        for key in settings:
            setattr(self, key, settings[key])

    def __create(self):
        if not os.path.isfile(self.path):
            logging.debug(f"Settings file does not exist creating: {self.path}")
            with open(self.path, "w") as file:
                file.write(json.dumps(self.settings_json, indent=4))
