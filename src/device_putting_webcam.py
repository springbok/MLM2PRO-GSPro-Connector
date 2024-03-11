import logging
import os
from PySide6.QtWidgets import QMessageBox
from src import MainWindow
from src.ctype_screenshot import ScreenMirrorWindow
from src.device_putting_base import DevicePuttingBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_device_webcam import WorkerDeviceWebcam


class DevicePuttingWebcam(DevicePuttingBase):

    webcam_app = 'ball_tracking.exe'

    def __init__(self, main_window: MainWindow):
        DevicePuttingBase.__init__(self, main_window)
        self.device_worker = WorkerDeviceWebcam(self.main_window.putting_settings)
        self.setup()

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)

    def start_app(self):
        if self.putting_settings.webcam['auto_start'] == "Yes" and not self.__find_ball_tracking_app():
            try:
                params = f'-c {self.putting_settings.webcam["ball_color"]} -w {self.putting_settings.webcam["camera"]} {self.putting_settings.webcam["params"]}'
                logging.debug(f'Starting webcam app: {DevicePuttingWebcam.webcam_app} params: {params}')
                os.spawnl(os.P_DETACH, DevicePuttingWebcam.webcam_app, f'{DevicePuttingWebcam.webcam_app} {params}')
                Event().wait(3)
            except Exception as e:
                logging.debug(f'Could not start webcam app: {DevicePuttingWebcam.webcam_app} error: {format(e)}')

    def __find_ball_tracking_app(self):
        try:
            ScreenMirrorWindow.find_window(self.putting_settings.webcam['window_name'])
            running = True
        except Exception:
            running = False
        return running

    def device_worker_error(self, error):
        msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.pause()
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.WEBCAM_PUTTING, msg)
        QMessageBox.warning(self.main_window, "Webcam Error", msg)

    def club_selected(self, club_data):
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")
        if club_data['Player']['Club'] == "PT":
            self.device_worker.select_putter(True)
            ScreenMirrorWindow.top_window(self.main_window.putting_settings.webcam['window_name'])
        else:
            self.device_worker.select_putter(False)
            ScreenMirrorWindow.not_top_window(self.main_window.putting_settings.webcam['window_name'])
            ScreenMirrorWindow.bring_to_front(self.main_window.settings.grspo_window_name)
        super().club_selected(club_data)


