import json
import logging
from multiprocessing import Process

from src.screenshot import Screenshot


class ShotProcessingProcess(Process):

    def __init__(self, previous_shot, settings, apps_paths):
        Process.__init__(self)
        logging.debug('Start shot processing')
        self.app_paths = apps_paths
        self.settings = settings
        self.previous_shot = previous_shot

    def run(self):
        logging.debug('Start process to check for a new shot and process it')
        # Get screenshot and check if it is different from last shot
        screenshot = Screenshot()
        screenshot.capture_and_process_screenshot(self.previous_shot)
        # Check if it's a new shot, if so update last shot
        self.previous_shot = json.dumps(screenshot.ball_data.__dict__)
        # Send data to gspro
        exit(0)
