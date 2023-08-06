import glob
import json
import os
import logging
import re
from dataclasses import dataclass

from src.appdata import AppDataPaths
from src.menu import MenuOptions
from src.non_blocking_input import NonBlockingInput
from src.ui import UI, Color


@dataclass
class Device:
    id: int
    name: str
    window_rect: { 'left': int, 'top': int, 'right': int, 'bottom': int}
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


class DeviceManager:

    def __init__(self, app_paths: AppDataPaths):
        self.app_paths = app_paths
        self.current_device = None
        # Load standard devices
        self.devices = []
        self.devices.append(Device(1, 'iphone', { 'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'AirPlay', {}, self.app_paths.app_data_path))
        self.devices.append(Device(2, 'ipad', { 'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'AirPlay', {}, self.app_paths.app_data_path))
        self.devices.append(Device(3, 'android', { 'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'EasyCast', {}, self.app_paths.app_data_path))
        # Create files if they don't exist
        self.__create()
        # Load other devices files
        self.__load_other_devices()

    def __create(self):
        for device in self.devices:
            if not os.path.isfile(device.file_path()):
                device.save()

    def __load_other_devices(self):
        # Check directory and load any other device files in format device_<device>.json
        logging.debug(f'Checking for device config files in {self.app_paths.app_data_path}')
        i = len(self.devices)
        for file in glob.glob(f'{self.app_paths.app_data_path}\\device_*.json'):
            res = re.findall("device_(\w+).json", file)
            if not list(filter(lambda d: d.name == res[0], self.devices)):
                i = i + 1
                logging.debug(f'Found additional device config file: {file}')
                self.devices.append(Device(i, res[0], 0, 0, '', {}, self.app_paths.app_data_path))

    def __display_devices(self):
        print('Select the device you want to connect:')
        for device in self.devices:
            print(device.id, '--', device.name)
        print('Q -- Quit')

    def select_device(self):
        self.__display_devices()
        non_block_input = NonBlockingInput(exit_condition=MenuOptions.EXIT)
        done_processing = False
        input_str = ""
        while not done_processing:
            if non_block_input.input_queued():
                input_str = non_block_input.input_get()
                if input_str.strip().upper() == non_block_input.exit_condition.upper():
                    exit()
                else:
                    try:
                        sel = int(input_str)
                        if sel <= 0 or sel > len(self.devices):
                            raise Exception()
                        self.current_device = self.devices[sel-1]
                        self.current_device.load()
                        logging.debug(f'Selected device: {self.current_device.to_json()}')
                    except Exception as e:
                        UI.display_message(Color.RED, "", f"Invalid option. Please enter a valid option or press Q to Quit")
