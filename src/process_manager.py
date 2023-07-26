import ctypes
import logging
import multiprocessing
from multiprocessing import Queue
from src.gspro_process import GSProProcess
from src.shot_processing_process import ShotProcessingProcess
from src.ui import UI, Color
# Needed when we convert msg back to an object using eval
from src.process_message import ProcessMessage

class ProcessManager:

    def __init__(self, settings, app_paths, max_processes=2):
        self.app_paths = app_paths
        self.settings = settings
        self.max_processes = max_processes
        # Create a variables that can be shared between all processes
        self.last_shot = multiprocessing.Value(ctypes.c_wchar_p, '')
        self.error_count = multiprocessing.Value(ctypes.c_int, 0)
        self.stop_processing = multiprocessing.Value(ctypes.c_int, 0)
        # Create a queue to store shots to be sent to GSPro
        self.shot_queue = Queue()
        # Create queue for messaging between processes and the manager, contains UI & error messages
        self.messaging_queue = Queue()
        # Create screenshot processes
        self.processes = []
        self.gspro_process = None
        self.error_count_message_displayed = False
        self.__add_screenshot_processes()
        self.__add_gspro_process()

    def run(self):
        if self.error_count.value < 5:
            self.__process_message_queue()
        elif not self.error_count_message_displayed:
            UI.display_message(Color.RED, "CONNECTOR ||", "More than 5 errors detected, stopping processing. Fix issues and then restart the connector.")
            self.error_count_message_displayed = True

    def restart(self):
        self.error_count_message_displayed = False
        self.error_count.value = 0

    def __process_message_queue(self):
        if not self.messaging_queue.empty():
            while not self.messaging_queue.empty():
                msg = self.messaging_queue.get()
                msg = eval(msg)
                if msg.ui:
                    color = Color.GREEN
                    if msg.error:
                        color = Color.RED
                    UI.display_message(Color.GREEN, "CONNECTOR ||", msg.message)
                if msg.logging:
                    logging.debug(msg.message)

    def __add_screenshot_processes(self):
        # Create a new process object & start it
        for x in range(0, self.max_processes):
            process = ShotProcessingProcess(self.last_shot, self.settings, self.app_paths, self.shot_queue, self.messaging_queue, self.error_count, self.stop_processing)
            self.processes.append(process)
            process.start()

    def __add_gspro_process(self):
        self.gspro_process = GSProProcess(self.settings, self.shot_queue, self.messaging_queue, self.error_count, self.stop_processing)
        self.gspro_process.start()

    def shutdown(self):
        # Wait for all processes to finish
        self.stop_processing.value = 1
        for process in self.processes:
            process.join()
        if not self.gspro_process is None:
            self.gspro_process.join()


