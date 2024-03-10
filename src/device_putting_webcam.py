import logging
import os

from PySide6.QtCore import QThread, QObject, Signal
from PySide6.QtWidgets import QMessageBox

from src import MainWindow
from src.ctype_screenshot import ScreenMirrorWindow
from src.custom_exception import PutterNotSelected
from src.device_base import DeviceBase
from src.device_putting_base import DevicePuttingBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.putting_settings import PuttingSettings
from src.worker_device_webcam import WorkerDeviceWebcam


class DevicePuttingWebcam(DevicePuttingBase):

    ball_tracking_app_not_found = Signal()
    webcam_app = 'ball_tracking.exe'

    def __init__(self, main_window: MainWindow):
        DevicePuttingBase.__init__(self, main_window)
        self.device_worker = WorkerDeviceWebcam(self.main_window.settings, self.main_window.putting_settings)
        self.setup()

    def setup_device_thread(self):
        self.http_server_worker.started.connect(self.__server_started)
        self.http_server_worker.stopped.connect(self.__server_stopped)
        self.http_server_worker.error.connect(self.__error)
        self.http_server_worker.putt.connect(self.__putt_shot)
        self.http_server_thread.started.connect(self.http_server_worker.run)
        self.http_server_thread.start()

    def start_app(self):
        if self.putting_settings.webcam['auto_start'] == "Yes" and not self.__find_ball_tracking_app():
            try:
                params = f'-c {self.putting_settings.webcam["ball_color"]} -w {self.putting_settings.webcam["camera"]} {self.putting_settings.webcam["params"]}'
                logging.debug(f'Starting webcam app: {DevicePuttingWebcam.webcam_app} params: {params}')
                os.spawnl(os.P_DETACH, DevicePuttingWebcam.webcam_app, f'{DevicePuttingWebcam.webcam_app} {params}')
            except Exception as e:
                logging.debug(f'Could not start webcam app: {DevicePuttingWebcam.webcam_app} error: {format(e)}')

    def __error(self, error):
        self.error.emit(error)

    def __putt_shot(self, putt):
        self.shot.emit(putt)

    def __find_ball_tracking_app(self):
        running = False
        try:
            ScreenMirrorWindow.find_window(self.putting_settings.webcam['window_name'])
            running = True
        except Exception:
            self.ball_tracking_app_not_found.emit()
            running = False
        return running

    def select_putter(self, selected):
        self.http_server_worker.select_putter(selected)

    def device_worker_error(self, error):
        msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.pause()
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.WEBCAM_PUTTING, msg)
        QMessageBox.warning(self.main_window, "Connector Error", msg)

