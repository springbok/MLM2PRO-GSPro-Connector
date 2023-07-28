import ctypes
import logging
import multiprocessing
import os
from multiprocessing import Queue
import queue

import tesserocr

from src.gspro_process import GSProProcess
from src.shot_processing_process import ShotProcessingProcess
from src.ui import UI, Color
# Needed when we convert msg back to an object using eval
from src.process_message import ProcessMessage
from datetime import datetime, timedelta

class ProcessManager:

    def __init__(self, settings, app_paths, max_processes=2):
        self.app_paths = app_paths
        self.settings = settings
        self.max_processes = max_processes
        # Create a variables that can be shared between all processes
        self.last_shot = multiprocessing.Value(ctypes.c_wchar_p, '')
        self.error_count = multiprocessing.Value(ctypes.c_int, 0)
        self.stop_processing = multiprocessing.Value(ctypes.c_int, 0)
        self.process_busy = multiprocessing.Value(ctypes.c_wchar_p, '')
        # Create a queue to store shots to be sent to GSPro
        self.shot_queue = Queue()
        # Create queue for messaging between processes and the manager, contains UI & error messages
        self.messaging_queue = Queue()
        # Create a queue to hold tesserocr instances that can be used by processes as
        # PyTessBaseAPI is not pickable so doesn't work with multiprocessing
        self.tesserocr_queue = Queue()
        # Create screenshot processes
        self.processes = []
        self.gspro_process = None
        self.error_count_message_displayed = False
        self.scheduled_time = None
        self.reset_scheduled_time()
        self.__initialise_tesserocr_queue()
        self.__add_screenshot_processes()
        self.__add_gspro_process()

    def run(self):
        if datetime.now() > self.scheduled_time:
            if self.error_count.value < 5:
                # Call a process to process a screenshot
                self.__capture_and_process_screenshot()
                # Display and/or log any process messages
                self.__process_message_queue()
            elif not self.error_count_message_displayed:
                # More than 5 errors in processes, stop processing until restart by user
                UI.display_message(Color.RED, "CONNECTOR ||", "More than 5 errors detected, stopping processing. Fix issues and then restart the connector.")
                self.error_count_message_displayed = True
            # reset scheduled run time
            self.reset_scheduled_time()

    def restart(self):
        self.error_count_message_displayed = False
        self.error_count.value = 0

    def __initialise_tesserocr_queue(self):
        tesseract_path = os.path.join(os.getcwd(), 'Tesseract-OCR')
        tessdata_path = os.path.join(tesseract_path, 'tessdata')
        #tesseract_library = os.path.join(tesseract_path, 'libtesseract-5.dll')
        tesserocr.tesseract_cmd = tessdata_path
        for x in range(0, self.max_processes):
            tesserocr_api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_WORD, lang='train', path=tesserocr.tesseract_cmd)
        #self.tesserocr_queue.put(tesserocr_api)

    def __capture_and_process_screenshot(self):
        free_process = False
        for process in self.processes:
            print(f"process.name: {process.name} self.process_busy.value: {self.process_busy.value}")
            # Check for available process
            if process.is_alive() and not process.name in self.process_busy.value:
                free_process = True
                # Start screenshot process with specified pid
                self.process_busy.value = f"{self.process_busy.value} {process.name}" 
        if not free_process:
            # Could not any free processes to handle request
            logging.debug('All processes busy unable to handle screenshot request, reschedule')

    def reset_scheduled_time(self):
        self.scheduled_time = datetime.now() + timedelta(microseconds=(self.settings.SCREENSHOT_INTERVAL * 1000))

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
            process = ShotProcessingProcess(
                self.last_shot, self.settings,
                self.app_paths, self.shot_queue,
                self.messaging_queue, self.error_count,
                self.process_busy, self.stop_processing,
                self.tesserocr_queue)
            self.processes.append(process)
            process.start()

    def __add_gspro_process(self):
        # Multiprocess variable to tell the process to start running this gives us control from
        # this manager of when a process starts
        self.gspro_process = GSProProcess(
            self.settings, self.shot_queue,
            self.messaging_queue, self.error_count,
            self.stop_processing)
        self.gspro_process.start()

    def shutdown(self):
        self.stop_processing.value = 1
        # Wait for all processes to finish
        for process in self.processes:
            process.join()
            del process
        if not self.gspro_process is None:
            self.gspro_process.join()
            del self.gspro_process
        while not self.tesserocr_queue.empty():
            api = self.tesserocr_queue.get()
            api.End()



