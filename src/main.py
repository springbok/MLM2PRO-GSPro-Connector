import logging
import os
from multiprocessing import Queue
from src.appdata import AppDataPaths
from src.menu import Menu
from src.non_blocking_input import NonBlockingInput
from src.process_manager import ProcessManager
from src.settings import Settings
from src.shot_processing_process import ShotProcessingProcess
from src.ui import Color, UI
from datetime import datetime

def check_and_process_shot(queue, settings, app_paths, process_manager):
    logging.debug("Check & process new shot")
    process = ShotProcessingProcess(queue, settings, app_paths)
    process_manager.add(process)

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
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Starting processing threads...")
        # Create shared queue for processes
        queue = Queue()
        # Create process manager
        process_manager = ProcessManager(2)
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Connector is ready")
    except Exception as e:
        message = f'Failed to initialise: {format(e)}'
        UI.display_message(Color.RED, "CONNECTOR ||", message)
        logging.info(message)
    else:
        start_time = datetime.now()
        max_loop_time = 20  # 6 seconds
        menu = Menu()
        menu.display()
        try:
            non_block_input = NonBlockingInput(exit_condition='q')
            done_processing = False
            input_str = ""
            while not done_processing:
                delta = datetime.now() - start_time
                delta = delta.total_seconds()*1000
                if delta > settings.SCREENSHOT_INTERVAL and not done_processing:
                    check_and_process_shot(queue, settings, app_paths, process_manager)
                    start_time = datetime.now()
                if non_block_input.input_queued():
                    input_str = non_block_input.input_get()
                    if input_str.strip() == non_block_input.exit_condition:
                        done_processing = True
                    else:
                        print("{}".format(input_str))
        except Exception as e:
            message = f'Failed to initialise: {format(e)}'
            UI.display_message(Color.RED, "CONNECTOR ||", message)
            logging.info(message)
        finally:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Shutting down connector...")
            process_manager.shutdown()
