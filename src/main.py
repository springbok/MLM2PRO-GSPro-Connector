import logging
import os
from src.menu import Menu
from src.screenshot import Screenshot
from src.settings import Settings
from src.ui import Color, UI

def setup_logging():
    path = os.path.join(os.getcwd(), 'debug.log')
    if os.path.isfile(path):
        os.unlink(path)
    logging.basicConfig(
        format="%(asctime)s,%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.DEBUG,
        filename=path,
        encoding='utf-8',
        force = True
    )

def main():
    # Init
    UI.display_message(Color.GREEN, "CONNECTOR ||", 'Initialising...')
    setup_logging()
    try:
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Loading settings...')
        settings = Settings()
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Loading OCR components...')
        screenshot = Screenshot(settings)
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Checking for saved ROI's...")
        screenshot.load_rois()
    except Exception as e:
        message = f'Failed to initialise: {format(e)}'
        UI.display_message(Color.RED, "CONNECTOR ||", message)
        logging.info(message)
    else:
        while(True):
            Menu().run()

