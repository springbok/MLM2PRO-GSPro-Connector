import logging
from queue import Queue

import tesserocr

from src.gspro_process import GSProProcess
from src.shot_process import ShotProcess
from src.ui import UI, Color
# Needed when we convert msg back to an object using eval
from src.process_message import ProcessMessage
from datetime import datetime, timedelta

class ProcessManager:

    def __init__(self, settings, app_paths):
        self.app_paths = app_paths
        self.settings = settings
        self.last_shot = None
        self.error_count = 0
        # Create a queue to store shots to be sent to GSPro
        self.shot_queue = Queue()
        # Create queue for messaging between processes and the manager, contains UI & error messages
        self.messaging_queue = Queue()
        # Create a queue to hold tesserocr instances that can be used by processes as
        # PyTessBaseAPI is not pickable so doesn't work with multiprocessing
        self.tesserocr_queue = Queue()
        self.shot_process = None
        self.gspro_process = None
        self.processes_paused = False
        self.scheduled_time = None
        self.reset_scheduled_time()
        self.__initialise_tesserocr_queue()
        self.__create_screenshot_process()
        self.__create_gspro_process()

    def run(self):
        if not self.processes_paused and datetime.now() > self.scheduled_time:
            if self.error_count < 5:
                # Call a process to process a screenshot
                self.__capture_and_process_screenshot()
                # Display and/or log any process messages
                self.__process_message_queue()
            elif not self.processes_paused:
                # More than 5 errors in processes, stop processing until restart by user
                UI.display_message(Color.RED, "CONNECTOR ||", "More than 5 errors detected, stopping processing. Fix issues and then restart the connector.")
                self.processes_paused = True
            # reset scheduled run time
            self.reset_scheduled_time()

    def restart(self):
        self.processes_paused = False
        self.error_count = 0

    def __initialise_tesserocr_queue(self):
        tessdata_path =  self.app_paths.get_config_path(
            name='train',
            ext='.traineddata'
        )
        tesserocr_api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_WORD, lang='train')
        self.tesserocr_queue.put(tesserocr_api)

    def __capture_and_process_screenshot(self):
        if not self.processes_paused:
            # Check for next shot if process available
            if not self.shot_process.busy():
                self.shot_process.execute()
            else:
                logging.debug('Process busy unable to handle screenshot request, reschedule')

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

    def __create_screenshot_process(self):
        # Create a new process object & start it
        self.shot_process = ShotProcess(
            self.last_shot, self.settings,
            self.app_paths, self.shot_queue,
            self.messaging_queue, self.error_count,
            self.tesserocr_queue)
        self.shot_process.start()

    def __create_gspro_process(self):
        self.gspro_process = GSProProcess(
            self.settings, self.shot_queue,
            self.messaging_queue, self.error_count)
        self.gspro_process.start()

    def shutdown(self):
        # Wait for all processes to finish
        if not self.shot_process is None:
            self.shot_process.shutdown()
            self.shot_process.join()
            del self.shot_process
        if not self.gspro_process is None:
            self.gspro_process.shutdown()
            self.gspro_process.join()
            del self.gspro_process
        while not self.tesserocr_queue.empty():
            api = self.tesserocr_queue.get()
            api.End()



