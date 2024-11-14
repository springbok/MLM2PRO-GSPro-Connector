import logging
from threading import Event
from PySide6.QtCore import Signal
from src.auto_click import clickButton
from src.ctype_screenshot import ScreenMirrorWindow
from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerGSProStart(WorkerBase):
    gspro_started = Signal()


    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.name = 'WorkerGSProStart'

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        interval = 2 # check every 2 seconds
        timeout = False
        running = False
        button_found = False
        count = 0
        logging.debug(f'{self.name} Auto start GSPro, config window: {self.settings.gspro_config_window_name} Play Button: {self.settings.gspro_play_button_label} GSPro API Window: {self.settings.gspro_api_window_name}')
        while not self._shutdown.is_set() and not running and not timeout:
            count = count + interval
            Event().wait(interval)
            if not button_found:
                button_found = clickButton(self.settings.gspro_config_window_name, self.settings.gspro_play_button_label)
            try:
                ScreenMirrorWindow(self.settings.gspro_api_window_name)
                running = True
                self.gspro_started.emit()
            except Exception as e:
                if count >= 180:
                    timeout = True
                    self.error.emit(e)
        self.finished.emit()
