import logging
from dataclasses import dataclass
from src.application import Application
from src.screenshot import Screenshot
from src.ui import Color, UI


@dataclass
class MenuOptions:
    EXIT = "Q"
    DISPLAY_MENU = "M"
    RESET_ROI = "R"
    RESET_GSPRO_CONNECTION = "G"
    TEST_GSPRO_CONNECTION = "T"
    UNPAUSE_CONNECTOR = "U"
    CHANGE_DEVICE = "C"
    DISPLAY_VERSION = "V"


class Menu:
    def __init__(self):
        self.menu_options = {
            MenuOptions.DISPLAY_MENU: 'Display Menu',
            MenuOptions.RESET_ROI: 'Reset ROI',
            MenuOptions.RESET_GSPRO_CONNECTION: 'Reset GSPro Connection',
            MenuOptions.TEST_GSPRO_CONNECTION: 'Test GSPro Connection',
            MenuOptions.UNPAUSE_CONNECTOR: 'Unpause Connector',
            MenuOptions.CHANGE_DEVICE: 'Change Connected Device',
            MenuOptions.DISPLAY_VERSION: 'Display Connector Version',
            MenuOptions.EXIT: 'Exit',
        }

    def display(self):
        for key in self.menu_options.keys():
            print(key, '--', self.menu_options[key])

    def process(self, option, application: Application):
        try:
            # Pause processing
            application.process_manager.pause()
            option = option.upper()
            logging.info(f"menu selection: {option}")
            soptions = ', '.join(map(str, list(self.menu_options.keys())))
            if option == MenuOptions.DISPLAY_MENU:
                self.display()
            elif option == MenuOptions.UNPAUSE_CONNECTOR:
                i=1
            elif option == MenuOptions.RESET_GSPRO_CONNECTION:
                application.gspro_connection.reset()
            elif option == MenuOptions.TEST_GSPRO_CONNECTION:
                application.gspro_connection.check_gspro_status()
            elif option == MenuOptions.RESET_ROI:
                Screenshot(application).load_rois(True)
            elif option == MenuOptions.CHANGE_DEVICE:
                application.device_manager.select_device()
            elif option == MenuOptions.DISPLAY_VERSION:
                print(f'Version {Application.version}')
                print(f'Connected Device: {application.device_manager.current_device.name}')
            else:
                UI.display_message(Color.RED, "", f"Invalid option. Please enter a valid option: {soptions}, press M top display menu")
        except:
            raise
        finally:
            application.process_manager.restart()
