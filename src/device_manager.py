import glob
import os
import logging
import re
from src.appdata import AppDataPaths
from src.device import Device
from src.menu import MenuOptions
from src.non_blocking_input import NonBlockingInput
from src.ui import UI, Color


class DeviceManager:

    def __init__(self, app_paths: AppDataPaths):
        self.app_paths = app_paths
        self.current_device = None
        self.exit = False
        # Load standard devices
        self.devices = []
        self.devices.append(Device(1, 'iphone', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'AirPlay', {}, self.app_paths.app_data_path))
        self.devices.append(Device(2, 'ipad', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'AirPlay', {}, self.app_paths.app_data_path))
        self.devices.append(Device(3, 'android', {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}, 'EasyCast', {}, self.app_paths.app_data_path))
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
        if not self.current_device is None:
            print(f'Connected Device: {self.current_device.name}')
        print('Select the device you want to connect:')
        for device in self.devices:
            print(device.id, '--', device.name)
        if not self.current_device is None:
            print('Q -- Keep selected device')
        else:
            print('Q -- Quit')

    def select_device(self):
        self.__display_devices()
        non_block_input = NonBlockingInput(exit_condition=MenuOptions.EXIT)
        done_processing = False
        input_str = ""
        try:
            while not done_processing:
                input_str = non_block_input.input_get()
                if len(input_str) > 0:
                    logging.debug(f'key pressed: {input_str}')
                    non_block_input.pause()
                    if input_str.strip().upper() == non_block_input.exit_condition.upper():
                        if not self.current_device is None:
                            # We already selected a device previously so exit menu
                            done_processing = True
                            print(f'Keeping current device: {self.current_device.name}')
                        else:
                            # We've not yet selected a device so exit app
                            self.exit = True
                            done_processing = True
                    else:
                        done_processing = True
                        try:
                            sel = int(input_str)
                            if sel <= 0 or sel > len(self.devices):
                                raise Exception()
                            self.current_device = self.devices[sel-1]
                            self.current_device.load()
                            print(f'Changed to device: {self.current_device.name}')
                            logging.debug(f'Selected device: {self.current_device.to_json()}')
                        except Exception:
                            UI.display_message(Color.RED, "", f"Invalid option. Please enter a valid option or press Q to Quit")

        except KeyboardInterrupt:
            logging.debug("Ctrl-C pressed exiting device manager")
            self.exit = True
            raise
        except Exception:
            raise
