import ctypes
from datetime import datetime, timedelta
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
        # Create a queue to store shots to be sent to GSPro
        self.shot_queue = Queue()
        # Create queue for messaging between processes and the manager, contains UI & error messages
        self.messaging_queue = Queue()
        # Create screenshot processes
        self.processes = []
        self.gspro_process = None
        self.reset_scheduled_time()
        self.error_count_message_displayed = False

    def run(self):
        # Check shot queue, process shots and send to GSPro
        self.__start_gspro_process()
        # Start new process checking scheduled_time
        if datetime.now() > self.scheduled_time:
            # Check error count, if > 5 then stop processing
            if self.error_count.value < 5:
                # Add process & start
                self.__start_screenshot_process()
            elif not self.error_count_message_displayed:
                UI.display_message(Color.RED, "CONNECTOR ||", "More than 5 errors detected, stopping processing. Fix issues and then restart the connector.")
                self.error_count_message_displayed = True
            # Display any process messages
            self.__process_message_queue()
            # Reschedule
            self.reset_scheduled_time()

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

    def __start_screenshot_process(self):
        # Clear any completed process objects
        self.__clean()
        # Create a new process object & start it
        if len(self.processes) < self.max_processes:
            process = ShotProcessingProcess(self.last_shot, self.settings, self.app_paths, self.shot_queue, self.messaging_queue, self.error_count)
            self.processes.append(process)
            process.start()
        else:
            logging.debug("Too many processes in the queue, ignoring new processes")

    def __start_gspro_process(self):
        if not self.shot_queue.empty():
            # Delete completed process object if required
            if not self.gspro_process is None:
                if not self.gspro_process.is_alive():
                    del self.gspro_process
                    self.gspro_process = None
            # Create new object & start process
            if self.gspro_process is None:
                self.gspro_process = GSProProcess(self.settings, self.shot_queue, self.messaging_queue, self.error_count)
                self.gspro_process.start()

    def __clean(self):
        i = 0
        # Check for completed processes and delete the object, a process
        # can not be restarted so a new object needs to be created
        for process in self.processes:
            if not process.is_alive() and not process.exitcode is None:
                logging.debug("Delete completed process")
                self.processes.pop(i)
                del process
            i = i + 1

    def reset_scheduled_time(self):
        self.scheduled_time = datetime.now() + timedelta(microseconds=(self.settings.SCREENSHOT_INTERVAL * 1000))

    def shutdown(self):
        # Wait for all processes to finish
        for process in self.processes:
            process.join()
        if not self.gspro_process is None:
            self.gspro_process.join()


