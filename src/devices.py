import glob
import logging
import os
import re

from src.appdata import AppDataPaths
from src.device import Device


class Devices:

    def __init__(self, app_paths: AppDataPaths):
        self.app_paths = app_paths
        self.devices = []
        self.__create_default_devices()
        self.load_devices()

    def load_devices(self):
        logging.debug(f'Checking for device config files in {self.app_paths.app_data_path}')
        self.devices = []
        i = 1
        for file in glob.glob(f'{self.app_paths.app_data_path}\\device_*.json'):
            res = re.findall("device_(\w+).json", file)
            logging.debug(f'Loading device config file: {res[0]}')
            device = Device(i, res[0], '', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, '', {}, self.app_paths.app_data_path, False)
            device.load()
            self.devices.append(device)

    def find_device(self, name):
        devices = list(filter(lambda d: d.name == name, self.devices))
        if len(devices) > 0:
            return devices[0]
        else:
            return None

    def __create_default_devices(self):
        # Check if we should create the default devices, we do this by checking if
        # the file appdata/lock/defaults_created exists
        path = os.path.join(self.app_paths.app_data_path, 'defaults_created')
        if not os.path.exists(path):
            logging.debug(f'Create default device config files in: {self.app_paths.app_data_path}')
            device = Device(1, 'iphone', '', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'AirPlay', {}, self.app_paths.app_data_path, False)
            device.save()
            device = Device(2, 'ipad', '', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'AirPlay', {}, self.app_paths.app_data_path, False)
            device.save()
            device = Device(3, 'android', '', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'EasyCast', {}, self.app_paths.app_data_path, False)
            device.save()
            f = open(path, "w")
            f.write("configs created")
            f.close()

    def save(self):
        for device in self.devices:
            if not os.path.isfile(device.file_path()):
                device.save()
        # Always create the template file
        Device(-1, '', '', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'Window Title', {}, self.app_paths.app_data_path, True).save()

    def as_list(self):
        devices = ['None']
        for device in self.devices:
            devices.append(device.name)
        return devices