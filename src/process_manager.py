import ctypes
import datetime
import json
import logging
import multiprocessing
from multiprocessing import Queue
from src.gspro_process import GSProProcess
from src.shot_processing_process import ShotProcessingProcess
from src.ui import UI, Color


class ProcessManager:

    def __init__(self, settings, app_paths, max_processes=2):
        self.max_processes = max_processes
        # Create a variables that can be shared between all processes
        self.previous_shot = multiprocessing.Value(ctypes.c_wchar_p, '')
        self.error_count = multiprocessing.Value(ctypes.c_int, 0)
        # Create a queue to store shots to be sent to GSPro
        self.shot_queue = Queue()
        # Create queue for messaging between processes and the manager, contains UI & error messages
        self.messaging_queue = Queue()
        # Create screenshot processes
        self.processes = []
        for x in range(0, self.max_processes):
            self.processes.append(ShotProcessingProcess(self.previous_shot, settings, app_paths, self.shot_queue, self.messaging_queue, self.error_count))
        # Create process to send data to GSPro
        self.gspro_process = GSProProcess(settings, self.shot_queue, self.messaging_queue, self.error_count)
        self.scheduled_time = datetime.now() + datetime.timedelta(milliseconds=settings.SCREENSHOT_INTERVAL)
        self.error_count_message_displayed = False

    def run(self):
        # Start new process checking scheduled_time
        if self.scheduled_time > datetime.now():
            # Check error count, if > 5 then stop processing
            if self.error_count < 5:
                free_process = False
                for process in self.processes:
                    # Check for available process
                    if not process.is_alive():
                        free_process = True
                        # Start screenshot process
                        process.start()
                if not free_process:
                    # Could not any free processes to handle request
                    logging.debug('All processes busy unable to handle screenshot request, reschedule')
                # Check shot queue, process shots and send to GSPro
                if not self.shot_queue.empty() and not self.gspro_process.is_alive():
                    self.gspro_process.start()
            elif not self.error_count_message_displayed:
                UI.display_message(Color.RED, "CONNECTOR ||", "More than 5 errors detected, stopping processing. Fix issues and then restart the connector.")
                self.error_count_message_displayed = True
            # Display any process messages
            self.__display_ui_messages()
            # Reschedule
            self.scheduled_time = datetime.now() + datetime.timedelta(milliseconds=self.settings.SCREENSHOT_INTERVAL)

    def restart(self):
        self.error_count_message_displayed = False
        self.error_count = 0

    def __display_ui_messages(self):
        if not self.messaging_queue.empty():
            while not self.messaging_queue.empty():
                msg = self.messaging_queue.get()
                msg = json.loads(msg)
                color = Color.GREEN
                if msg.error:
                    color = Color.RED
                UI.display_message(Color.GREEN, "CONNECTOR ||", msg.message)

    def shutdown(self):
        # Wait for all processes to finish
        for process in self.processes:
            process["process"].join()
        self.gspro_process.join()


