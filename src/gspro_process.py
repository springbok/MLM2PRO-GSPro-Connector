from threading import Thread, Event
# Required for to reconstruct the object from the queue
from src.ball_data import BallData
from src.process_message import ProcessMessage


# All code needs to multiprocess safe, so do no use the normal logger for example
# for logging we add a message we want to log to the shot_queue and the process manager
# will log it for us


class GSProProcess(Thread):

    def __init__(self, settings, shot_queue, messaging_queue, error_count):
        Thread.__init__(self, daemon=True)
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.settings = settings
        self.error_count = error_count
        self._shutdown = Event()

    def run(self):
        while not self._shutdown.is_set():
            if not self.shot_queue.empty():
                while not self.shot_queue.empty():
                    shot = self.shot_queue.get()
                    shot = eval(shot)
                msg = ProcessMessage(error=False, message=f"Process {self.name}: running", logging=True, ui=True)
                self.messaging_queue.put(repr(msg))
        exit(0)

    def shutdown(self):
        self._shutdown.set()