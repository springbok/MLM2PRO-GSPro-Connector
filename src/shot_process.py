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
                 tesserocr_queue):
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
        self.tesserocr_queue = tesserocr_queue

    def run(self):
        # Execute if we are not to shutdown, we are not already busy, and we have been told to execute
        while not self._shutdown.is_set():
            if not self._busy.is_set() and self._execute.is_set():
                api = None
                try:
                    self._busy.set()
                    self._execute.clear()
                    msg = ProcessMessage(error=False, message=f"----Process {self.name}: running", logging=True, ui=False)
                    self.messaging_queue.put(repr(msg))
                    # Get screenshot and check if it is different from last shot
                    last_shot = None
                    if len(self.last_shot) > 0:
                        last_shot = eval(self.last_shot)
                    # Obtain an api from pool of api's
                    #api = self.tesserocr_queue.get()
                    #screenshot = Screenshot(self.settings, self.app_paths, api)
                    #self.screenshot.capture_and_process_screenshot(last_shot)
                    # Check if it's a new shot, if so update last shot
                    #if self.screenshot.diff:
                    #    self.last_shot = repr(self.screenshot.ball_data)
                    #    self.shot_queue.put(repr(self.screenshot.ball_data))
                except Exception as e:
                    # On error increase error count and add error message to the process message queue
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

    def busy(self):
        return self._busy.is_set()

    def execute(self):
        if not self._execute.is_set() and not self._busy.is_set():
            self._execute.set()

    def shutdown(self):
        self._shutdown.set()