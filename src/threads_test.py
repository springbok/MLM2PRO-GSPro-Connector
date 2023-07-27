import threading
import queue
import time


class Threadstest:

    def __init__(self):
        self.input_queue = queue.Queue()
        self.t1 = threading.Thread(target=self.read_kbd_input, args=(), daemon=True)
        self.t1.start()
        self.t2 = threading.Thread(target=self.process_queue, args=(), daemon=True)
        self.t2.start()

    def read_kbd_input(self):
        while True:
            for i in range(1, 2):
                #item = Screenshot(self.settings, self.app_paths)
                self.input_queue.put(i)
            time.sleep(1)

    def process_queue(self):
        while True:
            time.sleep(1)
            try:
                item = self.input_queue.get()
            except queue.Empty:
                continue
            else:
                self.input_queue.task_done()
