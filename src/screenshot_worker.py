import logging
import traceback
from threading import Event
from PySide6.QtCore import QObject, Signal
from src.device import Device
from src.screenshot import Screenshot
from src.screenshot_exputt import ScreenshotExPutt
from src.settings import Settings


class ScreenshotWorker(QObject):
    finished = Signal()
    error = Signal(tuple)
    shot = Signal(object or None)
    bad_shot = Signal(object or None)
    same_shot = Signal()
    started = Signal()
    paused = Signal()
    resumed = Signal()
    putting_started = Signal()
    putting_stopped = Signal()


    def __init__(self, settings: Settings):
        super(ScreenshotWorker, self).__init__()
        self.device = None
        self.putter = False
        self.putting_active = False
        self.putting_rois_reload = True
        self.settings = settings
        self.screenshot = Screenshot()
        self.exputt_screenshot = ScreenshotExPutt()
        self.putting_settings = None
        self.name = 'ScreenshotWorker'
        self._shutdown = Event()
        self._pause = Event()
        self.pause()

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        # Execute if not shutdown
        while not self._shutdown.is_set():
            Event().wait(self.settings.screenshot_interval/1000)
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            if not self._shutdown.is_set() and not self.device is None:
                try:
                    if self.putter and self.putting_active:
                        self.__do_screenshot(self.exputt_screenshot, self.putting_settings, self.putting_rois_reload)
                        self.putting_rois_reload = False
                    else:
                        self.__do_screenshot(self.screenshot, self.device, False)
                except Exception as e:
                    if not isinstance(e, ValueError):
                        self.pause()
                    traceback.print_exc()
                    logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
                    self.error.emit((e, traceback.format_exc()))
        self.screenshot.shutdown()
        if not self.exputt_screenshot is None:
            self.exputt_screenshot.shutdown()
        self.finished.emit()

    def __do_screenshot(self, screenshot, settings, rois_setup):
        # Grab sreenshot and process data, checks if this is a new shot
        screenshot.capture_screenshot(settings, rois_setup)
        if screenshot.screenshot_new:
            screenshot.ocr_image()
            if screenshot.new_shot:
                if screenshot.balldata.good_shot:
                    logging.info(f"Process {self.name} good shot send to GSPro")
                    self.shot.emit(screenshot.balldata)
                else:
                    logging.info(
                        f"Process {self.name} bad shot data: {screenshot.balldata.to_json()}, errors: {screenshot.balldata.errors}")
                    self.bad_shot.emit(screenshot.balldata)
            else:
                logging.info(f"Process {self.name} same shot do not send to GSPro")
                self.same_shot.emit()
        else:
            self.same_shot.emit()

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

    def select_putter(self, selected):
        self.putter = selected
        logging.debug(f"exputt self.putter: {self.putter}")

    def set_putting_active(self, active):
        self.putting_active = active
        if active:
            self.putting_started.emit()
        else:
            self.putting_stopped.emit()
        logging.debug(f'self.putting_active: {self.putting_active}')

    def get_putting_active(self):
        return self.putting_active

    def reload_putting_rois(self):
        if not self.putting_settings is None and not self.exputt_screenshot is None:
            self.putting_settings.load()
            self.putting_rois_reload = True
