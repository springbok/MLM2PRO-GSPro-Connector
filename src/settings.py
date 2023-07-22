import json
import os
import logging

class Settings:

    def __init__(self):
        self.__load()

    def __load(self):
        path = os.path.join(os.getcwd(), 'settings.json')
        logging.info(f"Loading settings from {path}")
        if os.path.isfile(path):
            with open(os.path.join(os.getcwd(), 'settings.json'), "r") as file:
                lines = file.readlines()
                cleaned_lines = [line.split("//")[0].strip() for line in lines if not line.strip().startswith("//")]
                cleaned_json = "\n".join(cleaned_lines)
                settings = json.loads(cleaned_json)
        else:
            raise RuntimeError(f"Could not open settings file: {path}")
        logging.info(f"Setting: {settings}")
        # Create dynamic attributes
        for key in settings:
            setattr(self, key, settings[key])
