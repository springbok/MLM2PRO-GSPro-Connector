import logging
import os
from PySide6.QtWidgets import QMessageBox
from src.ctype_screenshot import ScreenMirrorWindow, PuttingWindow, SetForegroundWindow
from src.custom_exception import PutterNotSelected
from src.device_putting_base import DevicePuttingBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.putting_settings import PuttingSettings, WebcamWindowFocus, WebcamWindowState
from src.worker_device_webcam import WorkerDeviceWebcam


class DevicePuttingWebcam(DevicePuttingBase):

    webcam_app = 'ball_tracking.exe'

    def __init__(self, main_window):
        DevicePuttingBase.__init__(self, main_window)
        self.device_worker = WorkerDeviceWebcam(self.main_window.putting_settings)
        self.setup()

    def setup_device_thread(self):
        super().setup_device_thread()

    def start_app(self):
        if self.main_window.putting_settings.webcam['auto_start'] == "Yes" and not self.__find_ball_tracking_app():
            try:
                params = f'-c {self.main_window.putting_settings.webcam["ball_color"]} -w {self.main_window.putting_settings.webcam["camera"]} -r {self.main_window.putting_settings.webcam["width"]} {self.main_window.putting_settings.webcam["params"]}'
                logging.debug(f'Starting webcam app: {DevicePuttingWebcam.webcam_app} params: {params}')
                os.spawnl(os.P_DETACH, DevicePuttingWebcam.webcam_app, f'{DevicePuttingWebcam.webcam_app} {params}')
            except Exception as e:
                logging.debug(f'Could not start webcam app: {DevicePuttingWebcam.webcam_app} error: {format(e)}')

    def __find_ball_tracking_app(self):
        try:
            ScreenMirrorWindow.find_window(self.main_window.putting_settings.webcam['window_name'])
            running = True
        except Exception:
            running = False
        return running

    def device_worker_error(self, error):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.WEBCAM_PUTTING, f'Putting Error: {format(error)}')
        if not isinstance(error, ValueError) and not isinstance(error, PutterNotSelected):
            QMessageBox.warning(self.main_window, "Putting Error", f'{format(error)}')
            self.stop()

    def club_selected(self, club_data):
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")
        putting_window = PuttingWindow(self.main_window.putting_settings.webcam['window_name'],
                                       self.main_window.settings.grspo_window_name)
        if club_data['Player']['Club'] == "PT":
            if self.main_window.putting_settings.webcam['window_putting_focus'] == WebcamWindowFocus.PUTTING_WINDOW:
                putting_window.top_and_focused()
            elif self.main_window.putting_settings.webcam['window_putting_focus'] == WebcamWindowFocus.GSPRO:
                putting_window.top_not_focused()
        else:
            if self.main_window.putting_settings.webcam['window_not_putting_state'] == WebcamWindowState.HIDE:
                putting_window.hide()
            #elif self.main_window.putting_settings.webcam['window_not_putting_state'] == WebcamWindowState.MINIMIZE:
            #    putting_window.minimize()
            elif self.main_window.putting_settings.webcam['window_not_putting_state'] == WebcamWindowState.SEND_TO_BACK:
                putting_window.send_to_back()
            ScreenMirrorWindow.bring_to_front(self.main_window.settings.grspo_window_name)
        super().club_selected(club_data)



