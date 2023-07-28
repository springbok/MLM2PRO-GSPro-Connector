from threading import Thread, Event

from src.process_message import ProcessMessage


# All code needs to multiprocess safe, so do no use the normal logger for example
# for logging we add a message we want to log to the shot_queue and the process manager
# will log it for us

class BallData:
    def __init__(self):
        self.speed = 0
        self.spin_axis = 0
        self.total_spin = 0
        self.hla = 0
        self.vla = 0
        self.club_speed = 0
        self.back_spin = 0
        self.side_spin = 0

    def __copy__(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj


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