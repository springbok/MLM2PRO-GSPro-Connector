from datetime import datetime, timedelta
from multiprocessing import Process

from src.process_message import ProcessMessage
from src.screenshot import Screenshot


# All code needs to multiprocess safe, so do no use the normal logger for example
# for logging we add a message we want to log to the messaging_queue and the process manager
# will log it for us

class ShotProcessingProcess(Process):

    def __init__(self, last_shot, settings, apps_paths, shot_queue, messaging_queue, error_count, stop_processing):
        Process.__init__(self)
        self.app_paths = apps_paths
        self.settings = settings
        self.last_shot = last_shot
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.error_count = error_count
        self.scheduled_time = None
        self.stop_processing = stop_processing
        self.__reset_scheduled_time()
        self.screenshot = Screenshot()

    def run(self):
        while self.stop_processing.value == 0:
            # Stop processing if too many errors
            if self.error_count.value < 5:
                # Start new process checking scheduled_time
                if datetime.now() > self.scheduled_time:
                    try:
                        # Get screenshot and check if it is different from last shot
                        last_shot = None
                        if len(last_shot) > 0:
                            last_shot = eval(self.last_shot)
                        self.screenshot.capture_and_process_screenshot(last_shot)
                        # Check if it's a new shot, if so update last shot
                        if self.screenshot.diff:
                            self.last_shot.value = repr(self.screenshot.ball_data)
                            self.shot_queue.put(repr(self.screenshot.ball_data))
                    except Exception as e:
                        # On error increase error count and add error message to the process message queue
                        self.error_count = self.error_count.value + 1
                        msg = ProcessMessage(error=False, message=f"Process {self.name}: Error: {e}", logging=True, ui=True)
                        self.messaging_queue.put(repr(msg))
                    # Reschedule
                    self.__reset_scheduled_time()
        self.__shutdown()
        exit(0)

    def __reset_scheduled_time(self):
        self.scheduled_time = datetime.now() + timedelta(microseconds=(self.settings.SCREENSHOT_INTERVAL * 1000))

    def __shutdown(self):
        self.screenshot.shutdown_ocr()