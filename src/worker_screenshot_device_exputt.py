import logging
import traceback
from threading import Event
from src.putting_settings import PuttingSettings
from src.screenshot_exputt import ScreenshotExPutt
from src.worker_screenshot_device_base import WorkerScreenshotBase
from src.settings import Settings


class WorkerScreenshotDeviceExPutt(WorkerScreenshotBase):

    def __init__(self, settings: Settings, putting_settings: PuttingSettings):
        WorkerScreenshotBase.__init__(self, settings)
        self.putting_rois_reload = True
        self.settings = settings
        self.putting_settings = putting_settings
        self.exputt_screenshot = ScreenshotExPutt(settings)
        self.name = 'WorkerScreenshotDeviceExPutt'

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        # Execute if not shutdown
        while not self._shutdown.is_set():
            Event().wait(self.settings.screenshot_interval/1000)
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            if not self._shutdown.is_set():
                try:
                    self.do_screenshot(self.exputt_screenshot, self.putting_settings, self.putting_rois_reload)
                    self.putting_rois_reload = False
                except Exception as e:
                    if not isinstance(e, ValueError):
                        self.pause()
                    traceback.print_exc()
                    logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
                    self.error.emit((e, traceback.format_exc()))
        self.finished.emit()

    def reload_putting_rois(self):
        if self.putting_settings is not None and self.exputt_screenshot is not None:
            self.putting_settings.load()
            self.putting_rois_reload = True

    def ignore_shots_after_restart(self):
        self.exputt_screenshot.first = True

    def select_putter(self, selected):
        self.putter = selected
        logging.debug(f"webcam self.putter: {self.putter}")

    def resume(self):
        print(f'{self.name} resume self.club: {self.club}')
        if self.club == 'PT':
            super().resume()
