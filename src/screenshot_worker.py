import logging
import traceback
from threading import Event
from PySide6.QtCore import QObject, Signal

from src.ball_data import BallData
from src.device import Device
from src.screenshot import Screenshot

class ScreenshotWorker(QObject):
    finished = Signal()
    error = Signal(tuple)
    shot = Signal(object or None)
    bad_shot = Signal(object or None)
    same_shot = Signal()
    started = Signal()
    paused = Signal()
    resumed = Signal()


    def __init__(self, interval: int):
        super(ScreenshotWorker, self).__init__()
        self.device = None
        self.interval = interval
        self.screenshot = Screenshot()
        self.name = 'ScreenshotWorker'
        self._shutdown = Event()
        self._pause = Event()
        self.pause()

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        # Execute if not shutdown
        while not self._shutdown.is_set():
            Event().wait(self.interval/1000)
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            if not self._shutdown.is_set() and not self.device is None:
                try:
                    # Grab sreenshot and process data, checks if this is a new shot
                    self.screenshot.capture_screenshot(self.device)
                    if self.screenshot.screenshot_new:
                        self.screenshot.ocr_image()
                        if self.screenshot.new_shot:
                            if self.screenshot.balldata.good_shot:
                                self.shot.emit(self.screenshot.balldata)
                            else:
                                logging.info(f"Process {self.name} bad shot data: {self.screenshot.balldata.to_json()}, errors: {self.screenshot.balldata.errors}")
                                self.bad_shot.emit(self.screenshot.balldata)
                    else:
                        self.same_shot.emit()
                except Exception as e:
                    if not isinstance(e, ValueError):
                        self.pause()
                    traceback.print_exc()
                    logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
                    self.error.emit((e, traceback.format_exc()))
        self.screenshot.shutdown()
        self.finished.emit()

    def shutdown(self):
        self.resume()
        self._shutdown.set()
        self.finished.emit()

    def pause(self):
        self._pause.clear()
        self.paused.emit()

    def resume(self):
        self._pause.set()
        self.resumed.emit()

    def change_device(self, device: Device):
        self.device = device
        # In case rois were updated
        self.screenshot.update_rois(self.device.rois)
        self.screenshot.resize_window = True

