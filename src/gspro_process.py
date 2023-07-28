from threading import Thread

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


class GSProProcess(Thread):

    def __init__(self, settings, shot_queue, messaging_queue, error_count, stop_processing):
        Thread.__init__(self, daemon=True)
        self.shot_queue = shot_queue
        self.messaging_queue = messaging_queue
        self.settings = settings
        self.error_count = error_count
        self.stop_processing = stop_processing

    def run(self):
        while self.stop_processing == 0:
            if not self.shot_queue.empty():
                while not self.shot_queue.empty():
                    shot = self.shot_queue.get()
                    shot = eval(shot)
                msg = ProcessMessage(error=False, message=f"Process {self.name}: running", logging=True, ui=True)
                self.messaging_queue.put(repr(msg))
        self.__shutdown()
        exit(0)

    def __shutdown(self):
        i=1