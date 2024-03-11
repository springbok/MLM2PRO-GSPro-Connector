import logging
import os
from PySide6.QtWidgets import QMessageBox
from src import MainWindow
from src.ctype_screenshot import ScreenMirrorWindow
from src.custom_exception import PutterNotSelected
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_device_r10 import WorkerDeviceR10


class DeviceLaunchMonitorR10(DeviceBase):

    webcam_app = 'ball_tracking.exe'

    def __init__(self, main_window: MainWindow):
        DeviceBase.__init__(self, main_window)
        self.device_worker = WorkerDeviceR10(self.main_window.putting_settings)

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self.device_worker.listening.connect(self.__listening)
        self.device_worker.connected.connect(self.__connected)

    def setup(self):
        self.setup_device_thread()
        self.setup_signals()
        self.device_worker_paused()

    def start_app(self):
        if len(self.main_window.settings.r10_connector_path.strip()) > 0:
            try:
                logging.debug(f'Starting R10 connector: {self.main_window.settings.r10_connector_path}')
                os.spawnl(os.P_DETACH, self.main_window.settings.r10_connector_path)
            except Exception as e:
                logging.debug(f'Could not start R10 connector app: {self.main_window.settings.r10_connector_path} error: {format(e)}')

    def device_worker_error(self, error):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.R10, f'Error: {format(error)}')
        QMessageBox.warning(self.main_window, "R10 Error", f'{format(error)}')
        self.stop()

    def __listening(self):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.R10, 'Listening')
        self.main_window.r10_status_label.setText('Listening')
        self.main_window.r10_status_label.setStyleSheet("QLabel { background-color : green; color : white; }")

    def __connected(self):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.R10, 'Connected')
        self.main_window.r10_status_label.setText('Connected')
        self.main_window.r10_status_label.setStyleSheet("QLabel { background-color : green; color : white; }")


    def device_worker_paused(self):
        msg = 'Start'
        status = 'Not Running'
        color = 'red'
        enabled = True
        if self.is_running():
            msg = 'Stop'
            if self.main_window.gspro_connection.connected:
                color = 'orange'
                status = 'Paused'
            else:
                status = 'Waiting GSPro'
                color = 'red'
        self.main_window.putting_server_button.setEnabled(enabled)
        self.main_window.putting_server_button.setText(msg)
        self.main_window.putting_server_status_label.setText(status)
        self.main_window.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
        self.device_worker.ignore_shots_after_restart()

    def device_worker_resumed(self):
        self.main_window.putting_server_button.setText('Stop')
        msg = 'Running'
        color = 'green'
        if not self.main_window.gspro_connection.connected:
            msg = 'Waiting GSPro'
            color = 'red'
        self.main_window.putting_server_status_label.setText(msg)
        self.main_window.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
