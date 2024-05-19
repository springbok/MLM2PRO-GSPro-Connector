import logging
import os

from PySide6.QtWidgets import QMessageBox
from src.ctype_screenshot import ScreenMirrorWindow
from src.custom_exception import PutterNotSelected
from src.device_putting_base import DevicePuttingBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.putting_settings import WebcamWindowFocus, WebcamWindowState
from src.window_control import WindowControl
from src.worker_device_webcam import WorkerDeviceWebcam


class DevicePuttingWebcam(DevicePuttingBase):

    webcam_app = 'ball_tracking.exe'

    def __init__(self, main_window):
        DevicePuttingBase.__init__(self, main_window)
        self.device_worker = WorkerDeviceWebcam(self.main_window.putting_settings)
        self._putting_window = None
        self._gspro_window = None
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
        if self._putting_window is None or self._putting_window.hwnd != ScreenMirrorWindow.find_window(self.main_window.putting_settings.webcam['window_name']):
            self._putting_window = WindowControl(self.main_window.putting_settings.webcam['window_name'])
        if self._gspro_window is None or self._gspro_window.hwnd != ScreenMirrorWindow.find_window(self.main_window.settings.grspo_window_name):
            self._gspro_window = WindowControl(self.main_window.settings.grspo_window_name)
        if club_data['Player']['Club'] == "PT":
            self._putting_window.top_most()
            if self.main_window.putting_settings.webcam['window_putting_focus'] == WebcamWindowFocus.GSPRO:
                self._gspro_window.set_focus_to_window()
        else:
            self._putting_window.send_to_back()
            if self.main_window.putting_settings.webcam['window_not_putting_state'] == WebcamWindowState.HIDE:
                self._putting_window.hide()
            elif self.main_window.putting_settings.webcam['window_not_putting_state'] == WebcamWindowState.MINIMIZE:
                self._putting_window.minimize()
            elif self.main_window.putting_settings.webcam['window_not_putting_state'] == WebcamWindowState.SEND_TO_BACK:
                self._putting_window.send_to_back()
            self._gspro_window.set_focus_to_window()
        super().club_selected(club_data)



