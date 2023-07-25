from multiprocessing import Process
from src.process_message import ProcessMessage

# All code needs to multiprocess safe, so do no use the normal logger for example
# for logging we add a message we want to log to the messaging_queue and the process manager
# will log it for us

class BallData:
    def __init__(self):
        self.speed = 0
        self.spin_axis = 0
        self.total_spin = 0
        self.hla = 0
        self.vla = 0
        self.club_speed = 0


class GSProProcess(Process):

    def __init__(self, settings, shot_queue, messaging_queue, error_count):
        Process.__init__(self)
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.settings = settings
        self.error_count = error_count

    def run(self):
        msg = ProcessMessage(error=False, message=f"Process {self.name}: running", logging=False, ui=True)
        self.messaging_queue.put(repr(msg))
        self.shot_queue.get()
        exit(0)