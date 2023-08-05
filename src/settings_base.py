import json
import os
import logging


class SettingsBase:

    def __init__(self, path, settings):
        self.path = path
        self.settings = settings
        self.__load()

    def __load(self):
        self.__create()
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
            logging.debug(f"File does not exist creating: {self.path}")
            with open(self.path, "w") as file:
                file.write(json.dumps(self.settings, indent=4))
