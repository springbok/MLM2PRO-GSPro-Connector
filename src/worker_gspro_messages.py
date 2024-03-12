import json
import logging
import re
import traceback
from threading import Event
from PySide6.QtCore import Signal
from src.gspro_connect import GSProConnect
from src.worker_screenshot_device_base import WorkerScreenshotBase


class WorkerGSProMessages(WorkerScreenshotBase):
    player_info = 201
    club_selected = Signal(object)
    gspro_message = Signal(object)

    def __init__(self, gspro_connection: GSProConnect):
        super(WorkerScreenshotBase, self).__init__()
        self.gspro_connection = gspro_connection
        self.name = 'WorkerGSProMessages'

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        # Execute if not shutdown
        while not self._shutdown.is_set():
            Event().wait(250/1000)
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            if not self._shutdown.is_set() and self.gspro_connection is not None and self.gspro_connection.connected():
                try:
                    message = self.gspro_connection.check_for_message()
                    if len(message) > 0:
                        logging.debug(f'{self.name}: GSPro received data: {message}')
                        self.gspro_message.emit(message)
                        self.__process_message(message)
                except Exception as e:
                    if not isinstance(e, ValueError):
                        self.pause()
                    traceback.print_exc()
                    logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
                    self.error.emit((e, traceback.format_exc()))
        self.finished.emit()

    def __process_message(self, message):
        messages = {}
        json_messages = re.split('(\{.*?\})(?= *\{)', message.decode("utf-8"))
        for json_message in json_messages:
            if len(json_message) > 0:
                logging.debug(f'__process_message json_message: {json_message}')
                msg = json.loads(json_message)
                messages[str(msg['Code'])] = msg
                # Check if club selection message
                if msg['Code'] == WorkerGSProMessages.player_info:
                    self.club_selected.emit(msg)
        return messages
