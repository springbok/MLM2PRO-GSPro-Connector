from PySide6.QtWidgets import QMessageBox
from src.custom_exception import CameraWindowNotFoundException
from src.device_putting_base import DevicePuttingBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.device_base import DeviceBase
from src.worker_screenshot_device_exputt import WorkerScreenshotDeviceExPutt
from src import MainWindow


class DevicePuttingExPutt(DevicePuttingBase):

    def __init__(self, main_window: MainWindow):
        self.device_worker = WorkerScreenshotDeviceExPutt(self.main_window.settings, self.main_window.putting_settings)
        DeviceBase.__init__(self, main_window)

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self.device_worker.bad_shot.connect(self.main_window.bad_shot)
        self.device_worker.too_many_ghost_shots.connect(self.__too_many_ghost_shots)

    def __setup_signals(self):
        self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        self.main_window.putting_settings_form.cancel.connect(self.resume)
        self.main_window.actionPuttingSettings.triggered.connect(self.pause)

    def __too_many_ghost_shots(self):
        self.pause()
        QMessageBox.warning(self.main_window, "Ghost Shots Detected",
                            "Too many putts were received within a short space of time.")

    def device_worker_error(self, error):
        if isinstance(error[0], CameraWindowNotFoundException):
            msg = f"Windows Camera application ' {self.main_window.putting_settings.exputt['window_name']}' does not seem to be running.\nPlease start the app, then press the 'Start' button to restart the putting."
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.pause()
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.EXPUTT_PUTTING, msg)
        QMessageBox.warning(self.main_window, "ExPutt Error", msg)

    def reload_putting_rois(self):
        self.device_worker.reload_putting_rois()