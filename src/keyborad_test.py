import threading
import queue

from src.threads_test import Threadstest


class NonBlockingInput:

    def __init__(self, exit_condition):
        self.exit_condition = exit_condition
        self.input_queue = queue.Queue()
        self.input_thread = threading.Thread(target=self.read_kbd_input, args=(), daemon=True)
        self.input_thread.start()

    def read_kbd_input(self):
        done_queueing_input = False
        while not done_queueing_input:
            console_input = input()
            self.input_queue.put(console_input)
            if console_input.strip() == self.exit_condition:
                done_queueing_input = True

    def input_queued(self):
        return_value = False
        if self.input_queue.qsize() > 0:
            return_value = True
        return return_value

    def input_get(self):
        return_value = ""
        if self.input_queue.qsize() > 0:
            return_value = self.input_queue.get()
        return return_value

if __name__ == '__main__':

    NON_BLOCK_INPUT = NonBlockingInput(exit_condition='quit')

    DONE_PROCESSING = False
    INPUT_STR = ""
    while not DONE_PROCESSING:
        if NON_BLOCK_INPUT.input_queued():
            INPUT_STR = NON_BLOCK_INPUT.input_get()
            if INPUT_STR.strip() == "quit":
                DONE_PROCESSING = True
            else:
                print("{}".format(INPUT_STR))