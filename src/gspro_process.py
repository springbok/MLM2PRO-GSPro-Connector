import json
import logging
from threading import Thread, Event
# Required for to reconstruct the object from the queue
from src.ball_data import BallData
from src.gspro_connect import GSProConnect
from src.process_message import ProcessMessage

class GSProProcess(Thread):

    def __init__(self, settings, shot_queue, messaging_queue, gspro_connection):
        Thread.__init__(self, daemon=True)
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.settings = settings
        self.gspro_connection = gspro_connection
        self.error_count = 0
        self._shutdown = Event()

    def run(self):
        while not self._shutdown.is_set():
            if not self.shot_queue.empty():
                try:
                    while not self.shot_queue.empty():
                        shot = self.shot_queue.get()
                        shot = eval(shot)
                        logging.info(f"Process {self.name} retrieved shot data from queue: {json.dumps(self.screenshot.ball_data.__dict__)}")
                except Exception as e:
                    self.error_count = self.error_count + 1
                    msg = ProcessMessage(error=False, message=f"Process {self.name}: Error: {e}", logging=True, ui=True)
                    self.messaging_queue.put(repr(msg))

        exit(0)

    def error_count(self):
        return self.error_count

    def reset_error_count(self):
        self.error_count = 0

    def shutdown(self):
        self._shutdown.set()