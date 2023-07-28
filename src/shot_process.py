import json
import logging
from threading import Thread, Event

from src.process_message import ProcessMessage
from src.screenshot import Screenshot


# All code needs to multiprocess safe, so do no use the normal logger for example
# for logging we add a message we want to log to the messaging_queue and the process manager
# will log it for us

class ShotProcess(Thread):

    def __init__(self, last_shot, settings,
                 apps_paths, shot_queue,
                 messaging_queue, error_count,
                 tesserocr_queue, lock):
        Thread.__init__(self, daemon=True)
        self.app_paths = apps_paths
        self.settings = settings
        self.last_shot = last_shot
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.error_count = error_count
        self._busy = Event()
        self._shutdown = Event()
        self._execute = Event()
        self.lock = lock
        self.tesserocr_queue = tesserocr_queue
        self.screenshot = Screenshot(self.settings, self.app_paths)

    def run(self):
        # Execute if we are not to shutdown, we are not already busy, and we have been told to execute
        while not self._shutdown.is_set():
            if not self._busy.is_set() and self._execute.is_set():
                api = None
                try:
                    self._busy.set()
                    self._execute.clear()
                    # Obtain an api from pool of api's
                    api = self.tesserocr_queue.get()
                    with self.lock:
                        logging.info(
                            f"Process {self.name} shot data: {json.dumps(self.screenshot.ball_data.__dict__)}")
                        if not self.last_shot is None:
                            logging.info(f"Process {self.name} last shot: {json.dumps(self.last_shot.__dict__)}")
                        self.screenshot.capture_and_process_screenshot(self.last_shot, api)
                        if self.screenshot.diff:
                            msg = ProcessMessage(error=False, message=f"Process {self.name} shot data: {json.dumps(self.screenshot.ball_data.__dict__)}", logging=True, ui=True)
                            self.messaging_queue.put(repr(msg))
                            self.last_shot = self.screenshot.ball_data.__copy__()
                            logging.info(f"Process {self.name} ***** new last shot: {json.dumps(self.last_shot.__dict__)}")
                except Exception as e:
                    # On error increase error count and add error message to the process message queue
                    with self.lock:
                        self.error_count = self.error_count + 1
                    logging.info(f"error count: {self.error_count}")
                    msg = ProcessMessage(error=False, message=f"Process {self.name}: Error: {e}", logging=True, ui=True)
                    self.messaging_queue.put(repr(msg))
                finally:
                    # Flag process as no longer busy
                    self._busy.clear()
                    # Release api and make it available
                    if api is not None:
                        self.tesserocr_queue.put(api)
        exit(0)

    def busy(self):
        return self._busy.is_set()

    def execute(self):
        if not self._execute.is_set() and not self._busy.is_set():
            self._execute.set()

    def shutdown(self):
        self._shutdown.set()