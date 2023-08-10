import logging
import os

from src.appdata import AppDataPaths
from src.application import Application
from src.device_manager import DeviceManager
from src.gspro_connection import GSProConnection
from src.menu import Menu, MenuOptions
from src.non_blocking_input import NonBlockingInput
from src.process_manager import ProcessManager
from src.screenshot import Screenshot
from src.settings import Settings
from src.ui import Color, UI


def setup_logging(app_paths):
    level = logging.DEBUG
    path = app_paths.get_log_file_path()
    if os.path.isfile(path):
        os.unlink(path)
    logging.basicConfig(
        format="%(asctime)s,%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=level,
        filename=path,
        encoding='utf-8',
        force=True
    )
    logging.getLogger(__name__)


def main():
    app = Application()
    # Init
    UI.display_message(Color.GREEN, "CONNECTOR ||", 'Initialising...')
    try:
        # Setup appdata dirs & files
        app.app_paths = AppDataPaths()
        app.app_paths.setup()
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Setting up logging...')
        # Setup logger
        setup_logging(app.app_paths)
        UI.display_message(Color.GREEN, "CONNECTOR ||", 'Loading settings...')
        # Load GSPro settings
        app.settings = Settings(app.app_paths)
        # Check for device config files
        app.device_manager = DeviceManager(app.app_paths)
        app.device_manager.select_device()
        if not app.device_manager.exit:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Checking for saved ROI's...")
            # Check if we can read ROI's from file, if not prompt user to specify
            Screenshot(app).load_rois()
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Starting processing threads...")
            # Get GSPro connection
            app.gspro_connection = GSProConnection(app.settings)
            app.gspro_connection.connect()
            # Create process manager to manage all threads
            app.process_manager = ProcessManager(app)
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Connector is ready")
            # Display the menu
            input('Connector is ready, please press enter after taking your first shot.')
            menu = Menu()
            menu.display()
            # Use non blocking key capture
            non_block_input = NonBlockingInput(exit_condition=MenuOptions.EXIT)
            input_str = ""
            # Start process schedule
            app.process_manager.reset_scheduled_time()
            while not done_processing:
                input_str = non_block_input.input_get()
                if len(input_str) > 0:
                    # Process input, check if it's the quit option, if not process the selected option
                    if input_str.strip().upper() == non_block_input.exit_condition.upper():
                        done_processing = True
                    else:
                        menu.process(input_str.upper(), app)
                        non_block_input.resume()
                else:
                    # Check for and process next shot
                    app.process_manager.run()

    except KeyboardInterrupt:
        print("Ctrl-C pressed exiting")
    except Exception as e:
        message = f'Failed to initialise: {format(e)}'
        UI.display_message(Color.RED, "CONNECTOR ||", message)
        logging.info(message)
    finally:
        UI.display_message(Color.GREEN, "CONNECTOR ||", "Shutting down connector...")
        # Stop processes cleanly
        if not app.process_manager is None:
            app.process_manager.shutdown()
        if not app.gspro_connection is None:
            app.gspro_connection.disconnect()
