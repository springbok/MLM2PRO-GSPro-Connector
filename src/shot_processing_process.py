from multiprocessing import Process
from src.process_message import ProcessMessage
from src.screenshot import Screenshot


# All code needs to multiprocess safe, so do no use the normal logger for example
# for logging we add a message we want to log to the messaging_queue and the process manager
# will log it for us

class ShotProcessingProcess(Process):

    def __init__(self, last_shot, settings,
                 apps_paths, shot_queue,
                 messaging_queue, error_count,
                 process_busy, stop_processing,
                 tesserocr_queue):
        Process.__init__(self)
        self.app_paths = apps_paths
        self.settings = settings
        self.last_shot = last_shot
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.error_count = error_count
        self.stop_processing = stop_processing
        self.process_busy = process_busy
        self.tesserocr_queue = tesserocr_queue

    def run(self):
        msg = ProcessMessage(error=False, message=f"Process {self.name}: running", logging=True, ui=False)
        self.messaging_queue.put(repr(msg))
        while self.stop_processing == 0:
            msg = ProcessMessage(error=False, message=f"self.process_busy.value: {self.process_busy.value}", logging=True, ui=True)
            self.messaging_queue.put(repr(msg))
            if self.name in self.process_busy.value:
                api = None
                try:
                    msg = ProcessMessage(error=False, message=f"Process {self.name}: running", logging=True, ui=False)
                    self.messaging_queue.put(repr(msg))
                    # Get screenshot and check if it is different from last shot
                    last_shot = None
                    if len(self.last_shot.value) > 0:
                        last_shot = eval(self.last_shot)
                    # Obtain an api from pool of api's
                    api = self.tesserocr_queue.get()
                    screenshot = Screenshot(self.settings, self.app_paths, api)
                    #self.screenshot.capture_and_process_screenshot(last_shot)
                    # Check if it's a new shot, if so update last shot
                    #if self.screenshot.diff:
                    #    self.last_shot.value = repr(self.screenshot.ball_data)
                    #    self.shot_queue.put(repr(self.screenshot.ball_data))
                except Exception as e:
                    # On error increase error count and add error message to the process message queue
                    self.error_count = self.error_count.value + 1
                    msg = ProcessMessage(error=False, message=f"Process {self.name}: Error: {e}", logging=True, ui=True)
                    self.messaging_queue.put(repr(msg))
                finally:
                    # Flag process as no longer busy
                    self.process_busy.value.replace(f"{self.name} ", '')
                    # Release api
                    if api is not None:
                        self.tesserocr_queue.put(api)
        self.__shutdown()
        exit(0)

    def __shutdown(self):

        i = 1

        #self.screenshot.shutdown_ocr()