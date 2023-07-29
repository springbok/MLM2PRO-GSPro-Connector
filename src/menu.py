from dataclasses import dataclass

from src.ui import Color, UI

@dataclass
class MenuOptions:
    EXIT: 'Q'
    DISPLAY_MENU = 'M'
    RESET_ROI = 'R'
    RESET_GSPRO_CONNECTION = 'G'
    TEST_GSPRO_CONNECTION = 'T'
    UNPAUSE_CONNECTOR: 'U'


class Menu:
    def __init__(self):
        self.menu_options = {
            MenuOptions.DISPLAY_MENU: 'Display Menu',
            MenuOptions.RESET_ROI: 'Reset ROI',
            MenuOptions.RESET_GSPRO_CONNECTION: 'Reset GSPro Connection',
            MenuOptions.TEST_GSPRO_CONNECTION: 'Test GSPro Connection',
            MenuOptions.UNPAUSE_CONNECTOR: 'Unpause Connector',
            MenuOptions.EXIT: 'Exit',
        }

    def display(self):
        for key in self.menu_options.keys():
            print(key, '--', self.menu_options[key])

    def process(self, option, process_manager, gspro_connection, screenshot):
        soptions = ', '.join(map(str, list(self.menu_options.keys())))
        if option == MenuOptions.DISPLAY_MENU:
            self.display()
        elif option == MenuOptions.UNPAUSE_CONNECTOR:
            process_manager.restart()
        elif option == MenuOptions.RESET_GSPRO_CONNECTION:
            gspro_connection.reset()
        elif option == MenuOptions.TEST_GSPRO_CONNECTION:
            gspro_connection.check_gspro_status()
        elif option == MenuOptions.RESET_ROI:
            screenshot.load_rois(True)
        else:
            UI.display_message(Color.RED, "", f"Invalid option. Please enter a valid option: {soptions}, press M top display menu")
