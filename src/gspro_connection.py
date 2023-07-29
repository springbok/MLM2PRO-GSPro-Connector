import logging

from src.gspro_connect import GSProConnect
from src.ui import UI, Color


class GSProConnection:

    def __init__(self, settings) -> None:
        self.gspro_connect = GSProConnect(
            settings.GSPRO['DEVICE_ID'],
            settings.GSPRO['UNITS'],
            settings.GSPRO['API_VERSION'],
            settings.GSPRO['IP_ADDRESS'],
            settings.GSPRO['PORT']
        )
        self.connected = False

    def connect(self):
        # Connect to GSPro
        try:
            msg = "Connecting to GSPro..."
            logging.info(msg)
            UI.display_message(Color.GREEN, "CONNECTOR ||", msg)
            self.gspro_connect.init_socket()
            self.check_gspro_status()
        except Exception as e:
            raise ConnectionError(f"Error while trying to connect to GSPro, make sure GSPro is running. Exception: {e}")
        else:
            self.connected = True

    def reset(self):
        msg = "Resetting GSPro connection..."
        logging.info(msg)
        UI.display_message(Color.GREEN, "CONNECTOR ||", msg)
        self.gspro_connect.terminate_session()
        self.connect()

    def disconnect(self):
        self.gspro_connect.terminate_session()
        self.connected = False

    def check_gspro_status(self):
        msg = "Checking GSPro connection status..."
        logging.info(msg)
        UI.display_message(Color.GREEN, "CONNECTOR ||", msg)
        for attempt in range(10):
            try:
                self.gspro_connect.send_test_signal()
                break
            except Exception as e:
                raise


