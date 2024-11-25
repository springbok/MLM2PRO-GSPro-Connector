import subprocess
from PySide6.QtWidgets import QMessageBox
from threading import Event
from src.ctype_screenshot import ScreenMirrorWindow
from src.custom_exception import CameraWindowNotFoundException
from src.device_putting_base import DevicePuttingBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_screenshot_device_exputt import WorkerScreenshotDeviceExPutt


class DevicePuttingExPutt(DevicePuttingBase):

    def __init__(self, main_window):
        DevicePuttingBase.__init__(self, main_window)
        self.device_worker = WorkerScreenshotDeviceExPutt(self.main_window.settings, self.main_window.putting_settings)
        self.setup()

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.bad_shot.connect(self.__bad_shot)
        self.device_worker.too_many_ghost_shots.connect(self.__too_many_ghost_shots)

    def __bad_shot(self, balldata):
        self.main_window.shot_sent(balldata)

    def start_app(self):
        if self.main_window.putting_settings.exputt['auto_start'] == 'Yes':
            try:
                self.main_window.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR,
                                             f'Starting ExPutt')
                ScreenMirrorWindow.find_window(self.main_window.putting_settings.exputt['window_name'])
            except Exception:
                subprocess.run('start microsoft.windows.camera:', shell=True)
                Event().wait(3)

    def __too_many_ghost_shots(self):
        self.pause()
        QMessageBox.warning(self.main_window, "Ghost Shots Detected",
                            "Too many putts were received within a short space of time.")

    def device_worker_error(self, error):
        if isinstance(error[0], CameraWindowNotFoundException):
            msg = f"Windows Camera application ' {self.main_window.putting_settings.exputt['window_name']}' does not seem to be running.\nPlease start the app, then press the 'Start' button to restart the putting."
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.stop()
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.EXPUTT_PUTTING, msg)
        QMessageBox.warning(self.main_window, "ExPutt Error", msg)

    def reload_putting_rois(self):
        if self.device_worker is not None:
            self.device_worker.reload_putting_rois()
