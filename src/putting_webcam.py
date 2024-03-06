import logging
import os

from PySide6.QtCore import QThread, QObject, Signal
from src.ctype_screenshot import ScreenMirrorWindow
from src.putting_settings import PuttingSettings
from src.server_putting_webcam import PuttingRequestHandler, PuttingWebcamWorker


class PuttingWebcam(QObject):

    putt_shot = Signal(object)
    started = Signal()
    stopped = Signal()
    error = Signal(object)
    ball_tracking_app_not_found = Signal()
    webcam_app = 'ball_tracking.exe'

    def __init__(self, settings: PuttingSettings):
        super(PuttingWebcam, self).__init__()
        self.worker = None
        self.thread = QThread()
        self.running = None
        self.settings = settings
        self.http_server_thread = None
        self.http_server_worker = None

    def start_server(self):
        self.http_server_thread = QThread()
        self.http_server_worker = PuttingWebcamWorker(self.settings)
        self.http_server_worker.moveToThread(self.http_server_thread)
        self.http_server_worker.started.connect(self.__server_started)
        self.http_server_worker.stopped.connect(self.__server_stopped)
        self.http_server_worker.error.connect(self.__error)
        self.http_server_worker.putt.connect(self.__putt_shot)
        self.http_server_thread.started.connect(self.http_server_worker.run)
        self.http_server_thread.start()
        self.start_putting_app()

    def start_putting_app(self):
        if self.settings.webcam['auto_start'] == "Yes" and not self.__find_ball_tracking_app():
            try:
                params = f'-c {self.settings.webcam["ball_color"]} -w {self.settings.webcam["camera"]} {self.settings.webcam["params"]}'
                logging.debug(f'Starting webcam app: {PuttingWebcam.webcam_app} params: {params}')
                os.spawnl(os.P_DETACH, PuttingWebcam.webcam_app, f'{PuttingWebcam.webcam_app} {params}')
            except Exception as e:
                logging.debug(f'Could not start webcam app: {PuttingWebcam.webcam_app} error: {format(e)}')

    def __server_started(self):
        self.running = True
        self.started.emit()

    def __server_stopped(self):
        self.running = False
        self.stopped.emit()

    def __error(self, error):
        self.error.emit(error)

    def __putt_shot(self, putt):
        self.putt_shot.emit(putt)

    def shutdown(self):
        self.running = False
        self.http_server_worker.stop()
        self.http_server_thread.quit()
        self.http_server_thread.wait()

    def __find_ball_tracking_app(self):
        running = False
        try:
            ScreenMirrorWindow.find_window(self.settings.webcam['window_name'])
            running = True
        except Exception:
            self.ball_tracking_app_not_found.emit()
            running = False
        return running

    def select_putter(self, selected):
        self.http_server_worker.select_putter(selected)
