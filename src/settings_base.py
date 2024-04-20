import json
import os
import logging


class SettingsBase:

    def __init__(self, path: str, settings_json: json):
        self.path = path
        self.settings_json = settings_json
        self.load()

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

    def create(self):
        if not os.path.isfile(self.path):
            logging.debug(f"File does not exist creating: {self.path}")
            with open(self.path, "w") as file:
                file.write(json.dumps(self.settings_json, indent=4))

    def to_json(self, compact=False):
        exclude = ['path', 'settings_json', 'screenshot_interval']
        if compact:
            return json.dumps(self,
                          default=lambda o: dict((key, value) for key, value in o.__dict__.items() if key not in exclude ),
                          separators= ( ", " , ": " ))
        else:
           return json.dumps(self,
                          default=lambda o: dict((key, value) for key, value in o.__dict__.items() if key not in exclude ),
                          indent=4)

    def save(self):
        with open(self.path, "w") as file:
            file.write(self.to_json())

    def read_json_file(self):
        with open(self.path, 'r') as file:
            data = json.load(file)
        return data