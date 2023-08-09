import json
import logging
import os
from dataclasses import dataclass


@dataclass
class Device:
    id: int
    name: str
    window_rect: {'left': int, 'top': int, 'right': int, 'bottom': int}
    window_name: str
    rois: dict
    path: str

    def width(self):
        return self.window_rect['right'] - self.window_rect['left']

    def height(self):
        return self.window_rect['bottom'] - self.window_rect['top']

    def file_name(self):
        return f'device_{self.name}.json'

    def file_path(self):
        return f'{self.path}\\{self.file_name()}'

    def save(self):
        with open(self.file_path(), "w") as file:
            file.write(self.to_json())

    def load(self):
        logging.debug(f"Loading device settings from {self.file_path()}")
        if os.path.isfile(self.file_path()):
            with open(self.file_path(), "r") as file:
                lines = file.readlines()
                cleaned_lines = [line.split("//")[0].strip() for line in lines if not line.strip().startswith("//")]
                cleaned_json = "\n".join(cleaned_lines)
                settings = json.loads(cleaned_json)
        # Create dynamic attributes
        for key in settings:
            setattr(self, key, settings[key])
        logging.debug(f"Device settings: {self}")

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: dict((key, value) for key, value in o.__dict__.items() if key != 'path' and key != 'id'),
                          indent=4)
