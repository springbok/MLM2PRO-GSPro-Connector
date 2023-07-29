import logging

from src.gspro_connect import GSProConnect
from src.ui import UI, Color


class GSProConnection:

    def __init__(self, settings) -> None:
        self.gspro_connection = GSProConnect(
            self.settings.GSPRO['DEVICE_ID'],
            self.settings.GSPRO['UNITS'],
            self.settings.GSPRO['API_VERSION'],
            self.settings.GSPRO['IP_ADDRESS'],
            self.settings.GSPRO['port']
        )


    def connect(self):
        # Connect to GSPro
        try:
            msg = "Connecting to GSPro..."
            logging.info(msg)
            UI.display_message(Color.GREEN, "CONNECTOR ||", msg)
            self.gspro_connection.init_socket()
        except Exception as e:
            UI.display_message(Color.RED, "CONNECTOR ||", f"Error while trying to connect")
        finally:
