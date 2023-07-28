import logging
import os
from src.appdata import AppDataPaths
from src.menu import Menu
from src.non_blocking_input import NonBlockingInput
from src.process_manager import ProcessManager
from src.screenshot import Screenshot
from src.settings import Settings
from src.ui import Color, UI

def setup_logging(app_paths):
    level = logging.DEBUG
    #if settings.DEBUG == "False":
    #    level = logging.CRITICAL + 1
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
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Setting up logging...')
        setup_logging(app_paths)
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Loading settings...')
        settings = Settings(app_paths)
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Checking for saved ROI's...")
        Screenshot(settings, app_paths).load_rois()
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Starting processing threads...")
        # Create process manager specify the max processes allowed to run at the same time
        process_manager = ProcessManager(settings, app_paths)
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Connector is ready")
    except Exception as e:
        message = f'Failed to initialise: {format(e)}'
        UI.display_message(Color.RED, "CONNECTOR ||", message)
        logging.info(message)
    else:
        # Display the menu
        menu = Menu()
        menu.display()
        try:
            # Use non blocking key capture
            non_block_input = NonBlockingInput(exit_condition='q')
            done_processing = False
            input_str = ""
            # Start process schedule
            process_manager.reset_scheduled_time()
            while not done_processing:
                process_manager.run()
                if non_block_input.input_queued():
                    input_str = non_block_input.input_get()
                    # Process input, check if it's the quit option, if not process the selected option
                    if input_str.strip() == non_block_input.exit_condition:
                        done_processing = True
                    else:
                        menu.process(input_str.upper(), process_manager)

        except Exception as e:
            message = f'Failed to initialise: {format(e)}'
            UI.display_message(Color.RED, "CONNECTOR ||", message)
            logging.info(message)
        finally:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Shutting down connector...")
            # Stop processes cleanly
            process_manager.shutdown()
