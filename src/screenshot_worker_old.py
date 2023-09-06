import traceback
from threading import Event
from PySide6.QtCore import QObject, Signal, QTimer
from src.device import Device
from src.screenshot import Screenshot


class ScreenshotWorker(QObject):
    finished = Signal()
    error = Signal(tuple)
    shot = Signal(object or None)
    started = Signal()

    def __init__(self, tesserocr_queue, device: Device, interval: int):
        super(ScreenshotWorker, self).__init__()
        self.device = device
        self.interval = interval
        self.num_errors = 0
        self._busy = Event()
        self._shutdown = Event()
        self._execute = Event()
        self.tesserocr_queue = tesserocr_queue
        self.screenshot = Screenshot()
        self._pause = Event()
        self.resume()

    def run(self):
        self.started.emit()
        while not self._shutdown.is_set():
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            api = None
            try:
                # Obtain an api from pool of api's
                api = self.tesserocr_queue.get()
                # Grab sreenshot and process data, checks if this is a new shot
                self.screenshot.capture_and_process_screenshot(self.last_shot, api, self.device)
                if self.screenshot.new_shot:
                    self.last_shot = self.screenshot.ball_data.__copy__()
                    self.result.emit(self.last_shot)
                self.num_errors = 0
                QTimer.sleep(self.interval)
            except Exception as e:
                self.num_errors = self.num_errors + 1
                traceback.print_exc()
                self.error.emit((e, traceback.format_exc()))
            finally:
                # Release api and make it available
                if api is not None:
                    self.tesserocr_queue.put(api)
        self.finished.emit()

    def error_count(self):
        return self.num_errors

    def shutdown(self):
        self.resume()
        self._shutdown.set()

    def pause(self):
        self._pause.clear()

    def resume(self):
        self.num_errors = 0
        self._pause.set()

    def change_device(self, device):
        self.device = device
