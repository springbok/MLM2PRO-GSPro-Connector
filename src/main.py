import logging
import os

from src.menu import Menu
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
        encoding='utf-8'
    )

def main():
    # Init
    setup_logging()
    try:
        settings = Settings()
    except Exception as e:
        message = f'Failed to initialise: {format(e)}'
        UI.display_message(Color.RED, "CONNECTOR ||", message)
        logging.info(message)
    else:
        while(True):
            Menu().run()

