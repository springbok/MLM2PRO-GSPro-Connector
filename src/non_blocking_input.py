from queue import Queue
from threading import Thread, Event


class NonBlockingInput(Thread):

    def __init__(self, exit_condition):
        Thread.__init__(self, daemon=True)
        self._pause = Event()
        self.exit_condition = exit_condition
        self.input_queue = Queue()
        self.start()
        self.resume()

    def run(self):
        done_queueing_input = False
        while not done_queueing_input:
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            console_input = input()
            self.pause()
            self.input_queue.put(console_input)
            if console_input.strip().upper() == self.exit_condition:
                done_queueing_input = True

    def input_queued(self):
        return_value = False
        if not self.input_queue.empty():
            return_value = True
        return return_value

    def input_get(self):
        return_value = ""
        if not self.input_queue.empty():
            return_value = self.input_queue.get()
        return return_value

    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()
