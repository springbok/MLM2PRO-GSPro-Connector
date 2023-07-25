import json
import logging
from multiprocessing import Process

from src.process_message import ProcessMessage
from src.screenshot import Screenshot

class ShotProcessingProcess(Process):

    def __init__(self, previous_shot, settings, apps_paths, shot_queue, messaging_queue, error_count):
        Process.__init__(self)
        logging.debug('Start shot processing')
        self.app_paths = apps_paths
        self.settings = settings
        self.previous_shot = previous_shot
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.error_count = error_count

    def run(self):
        msg = ProcessMessage(error=False, message=f"Process {self.name}: runnins")
        self.messaging_queue.put(json.dumps(msg.__dict__))
        return

        screenshot = Screenshot()
        try:
            logging.debug('Start process to check for a new shot and process it')
            # Get screenshot and check if it is different from last shot
            screenshot.capture_and_process_screenshot(self.previous_shot)
            # Check if it's a new shot, if so update last shot
            self.previous_shot = json.dumps(screenshot.ball_data.__dict__)
        except Exception as e:
            # On error increase error count and add error message to the process message queue
            self.error_count = self.error_count + 1
            msg = ProcessMessage(error=True, message=f"Process {self.name}: Error: {e}")
            self.messaging_queue.put(json.dumps(msg.__dict__))
        finally:
            # Check for any UI messages to display, if so add to process message queue
            if not screenshot.message is None:
                msg = ProcessMessage(error=False, message=screenshot.message)
                self.messaging_queue.put(json.dumps(msg.__dict__))
            exit(0)