import json
import logging
from queue import Queue
from threading import Thread, Event
from src.application import Application
# Required for to reconstruct the object from the queue
from src.ball_data import BallData
from src.process_message import ProcessMessage


class GSProProcess(Thread):

    def __init__(self, application: Application, shot_queue: Queue, messaging_queue: Queue):
        Thread.__init__(self, daemon=True)
        self.application = application
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.num_errors = 0
        self._shutdown = Event()
        self.name = "gspro_process"
        self._pause = Event()
        self.resume()

    def run(self):
        while not self._shutdown.is_set():
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            if not self.shot_queue.empty():
                try:
                    while not self.shot_queue.empty():
                        shot = self.shot_queue.get()
                        logging.info(f"Process {self.name} got shot from queue: {json.dumps(shot)}")
                        shot = BallData(json.loads(shot))
                        logging.info(f"Process {self.name} retrieved shot data from queue sending to gspro: {json.dumps(shot.to_json())}")
                        if self.application.gspro_connection.connected:
                            self.application.gspro_connection.gspro_connect.launch_ball(shot)
                except Exception as e:
                    self.num_errors = self.num_errors + 1
                    msg = ProcessMessage(error=True, message=f"Process {self.name}: Error: {format(e)}", logging=True, ui=True)
                    self.messaging_queue.put(repr(msg))

        exit(0)

    def error_count(self):
        return self.num_errors

    def reset_error_count(self):
        self.num_errors = 0

    def shutdown(self):
        self.resume()
        self._shutdown.set()

    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()
