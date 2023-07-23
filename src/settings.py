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
        self.settings_json = multiline.loads("""{
    "HOST": "127.0.0.1", 
    "PORT": 921, 

    "WINDOW_NAME": "AirPlay", 
    "TARGET_WIDTH": 1638, 
    "TARGET_HEIGHT": 752, 
    "METRIC": "Yards", 
    "DEBUG": "True", 
    "SCREENSHOT_INTERVAL": 2500 
}""", multiline=True)
        self.__create()
        self.__load()

    def __load(self):
        logging.info(f"Loading settings from {self.path}")
        if os.path.isfile(self.path):
            with open(os.path.join(os.getcwd(), 'settings.json'), "r") as file:
                lines = file.readlines()
                cleaned_lines = [line.split("//")[0].strip() for line in lines if not line.strip().startswith("//")]
                cleaned_json = "\n".join(cleaned_lines)
                settings = json.loads(cleaned_json)
        else:
            raise RuntimeError(f"Could not open settings file: {self.path}")
        logging.info(f"Setting: {settings}")
        # Create dynamic attributes
        for key in settings:
            setattr(self, key, settings[key])

    def __create(self):
        if not os.path.isfile(self.path):
            logging.info(f"Settings file does not exist creating: {self.path}")
            with open(self.path, "w") as file:
                file.write(json.dumps(self.settings_json, indent=4))
