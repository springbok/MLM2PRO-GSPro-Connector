import logging
import os

from src.aqppdata import AppDataPaths
from src.menu import Menu
from src.screenshot import Screenshot
from src.settings import Settings
from src.ui import Color, UI

def setup_logging(settings, app_paths):
    level = logging.DEBUG
    if settings.DEBUG == "False":
        level = logging.CRITICAL + 1
    path = app_paths.get_log_file_path()
    if os.path.isfile(path):
        os.unlink(path)
    logging.basicConfig(
        format="%(asctime)s,%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=level,
        filename=path,
        encoding='utf-8',
        force = True
    )
    logging.getLogger(__name__)

def main(app_paths=None):
    # Init
    UI.display_message(Color.GREEN, "CONNECTOR ||", 'Initialising...')
    try:
        # Setup appdata dirs & files
        app_paths = AppDataPaths()
        app_paths.setup()
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Loading settings...')
        settings = Settings(app_paths)
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Setting up logging...')
        setup_logging(settings, app_paths)
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Loading OCR components...')
        #screenshot = Screenshot(settings)
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Checking for saved ROI's...")
        #screenshot.load_rois(app_paths)
    except Exception as e:
        message = f'Failed to initialise: {format(e)}'
        UI.display_message(Color.RED, "CONNECTOR ||", message)
        logging.info(message)
    else:
        menu = Menu()
        menu.display()
        while(True):
            menu.run()

