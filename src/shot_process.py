import json
import logging
from queue import Queue
from threading import Thread, Event
from src.application import Application
from src.process_message import ProcessMessage
from src.screenshot import Screenshot


class ShotProcess(Thread):

    def __init__(self,
                 application: Application,
                 shot_queue: Queue,
                 messaging_queue: Queue,
                 tesserocr_queue: Queue):
        Thread.__init__(self, daemon=True)
        self.application = application
        self.last_shot = None
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.num_errors = 0
        self._busy = Event()
        self._shutdown = Event()
        self._execute = Event()
        self.tesserocr_queue = tesserocr_queue
        self.screenshot = Screenshot(self.application)
        self.name = "shot_process"
        self._pause = Event()
        self.resume()

    def run(self):
        # Execute if not shutdown, we are not already busy, and we have been told to execute
        while not self._shutdown.is_set():
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
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
                        logging.info(f"Process {self.name} shot data: {self.screenshot.ball_data.to_json()}")
                        self.last_shot = self.screenshot.ball_data.__copy__()
                        self.shot_queue.put(self.screenshot.ball_data.to_json())
                except Exception as e:
                    self.num_errors = self.num_errors + 1
                    msg = ProcessMessage(error=True, message=f"Process {self.name}: Error: {format(e)}", logging=True, ui=True)
                    logging.debug(f"{msg}")
                    self.messaging_queue.put(repr(msg))
                finally:
                    # Flag process as no longer busy
                    self._busy.clear()
                    # Release api and make it available
                    if api is not None:
                        self.tesserocr_queue.put(api)

        exit(0)

    def error_count(self):
        return self.num_errors

    def reset_error_count(self):
        self.num_errors = 0

    def busy(self):
        return self._busy.is_set()

    def execute(self):
        if not self._execute.is_set() and not self._busy.is_set():
            self._execute.set()

    def shutdown(self):
        self.resume()
        self._shutdown.set()

    def pause(self):
        self._pause.clear()

    def resume(self):
        # Reload device settings in case of a change
        self.screenshot.reload_device_settings()
        self._pause.set()
