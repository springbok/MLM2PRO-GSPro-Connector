import json
import logging
from threading import Thread, Event
from src.process_message import ProcessMessage
from src.screenshot import Screenshot

class ShotProcess(Thread):

    def __init__(self, last_shot, settings,
                 apps_paths, shot_queue,
                 messaging_queue, tesserocr_queue):
        Thread.__init__(self, daemon=True)
        self.app_paths = apps_paths
        self.settings = settings
        self.last_shot = None
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.error_count = 0
        self._busy = Event()
        self._shutdown = Event()
        self._execute = Event()
        self.tesserocr_queue = tesserocr_queue
        self.screenshot = Screenshot(self.settings, self.app_paths)

    def run(self):
        # Execute if not shutdown, we are not already busy, and we have been told to execute
        while not self._shutdown.is_set():
            if not self._busy.is_set() and self._execute.is_set():
                api = None
                try:
                    self._busy.set()
                    self._execute.clear()
                    # Obtain an api from pool of api's
                    api = self.tesserocr_queue.get()
                    # Grab sreenshot and process data, checks if this is a new shot
                    self.screenshot.capture_and_process_screenshot(self.last_shot, api)
                    if self.screenshot.new_shot:
                        # New shot so place shot data in shot queue for processing
                        logging.info(f"Process {self.name} shot data: {json.dumps(self.screenshot.ball_data.__dict__)}")
                        self.last_shot = self.screenshot.ball_data.__copy__()
                        self.shot_queue.put(repr(self.last_shot))
                except Exception as e:
                    self.error_count = self.error_count + 1
                    msg = ProcessMessage(error=False, message=f"Process {self.name}: Error: {e}", logging=True, ui=True)
                    self.messaging_queue.put(repr(msg))
                finally:
                    # Flag process as no longer busy
                    self._busy.clear()
                    # Release api and make it available
                    if api is not None:
                        self.tesserocr_queue.put(api)
        exit(0)

    def error_count(self):
        return self.error_count

    def reset_error_count(self):
        self.error_count = 0

    def busy(self):
        return self._busy.is_set()

    def execute(self):
        if not self._execute.is_set() and not self._busy.is_set():
            self._execute.set()

    def shutdown(self):
        self._shutdown.set()