import logging
import traceback
from threading import Event
from src.device import Device
from src.screenshot import Screenshot
from src.worker_screenshot_device_base import WorkerScreenshotBase
from src.settings import Settings


class WorkerScreenshotDeviceLaunchMonitor(WorkerScreenshotBase):

    def __init__(self, settings: Settings):
        WorkerScreenshotBase.__init__(self, settings)
        self.device = None
        self.screenshot = Screenshot(settings)
        self.shot_count = 0
        self.name = 'WorkerScreenshotDeviceLaunchMonitor'

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        # Execute if not shutdown
        while not self._shutdown.is_set():
            Event().wait(self.settings.screenshot_interval/1000)
            # When _pause is clear we wait(suspended) if set we process
            self._pause.wait()
            # Make sure putter not selected
            if self.selected_club() == 'PT':
                self.pause()
                continue
            if not self._shutdown.is_set() and self.device is not None:
                try:
                    self.do_screenshot(self.screenshot, self.device, False)
                except Exception as e:
                    if not isinstance(e, ValueError):
                        self.pause()
                    traceback.print_exc()
                    logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
                    self.error.emit((e, traceback.format_exc()))
        self.finished.emit()

    def change_device(self, device: Device):
        self.device = device
        # In case rois were updated
        self.screenshot.update_rois(self.device.rois)
        self.screenshot.resize_window = True

    def ignore_shots_after_restart(self):
        self.screenshot.first = True

    def club_selected(self, club):
        super().club_selected(club)
        self.screenshot.selected_club = club
        if self.putter_selected():
            logging.debug('Putter selected pausing shot processing')
            self.pause()
        else:
            self.resume()
            logging.debug('Club other than putter selected resuming shot processing')
