from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMessageBox

from src.DevicesForm import DevicesForm
from src.SelectDeviceForm import SelectDeviceForm
from src.custom_exception import WindowNotFoundException, CameraWindowNotFoundException
from src.log_message import LogMessageTypes, LogMessageSystems
from src.screenshot_worker_launch_monitor import ScreenshotWorkerLaunchMonitor
from src import MainWindow

class LaunchMonitorMLM2PRO:

    def __init__(self, main_window: MainWindow):
        self.current_device = None
        self.screenshot_thread = None
        self.main_window = main_window
        self.screenshot_worker = ScreenshotWorkerLaunchMonitor(self.main_window.settings)
        self.devices = DevicesForm(self.main_window.app_paths)
        self.select_device = SelectDeviceForm(main_window=self.main_window)

    def setup(self):
        self.__setup_ui()
        self.__setup_screenshot_thread()
        self.__auto_start()


    def __setup_screenshot_thread(self):
        self.screenshot_thread = QThread()
        self.screenshot_worker.moveToThread(self.screenshot_thread)
        self.screenshot_thread.started.connect(self.screenshot_worker.run)
        self.screenshot_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self.screenshot_worker.bad_shot.connect(self.main_window.bad_shot)
        self.screenshot_worker.same_shot.connect(self.main_window.gspro_connection.club_selecion_worker.run)
        self.screenshot_worker.bad_shot.connect(self.main_window.gspro_connection.club_selecion_worker.run)
        self.screenshot_worker.too_many_ghost_shots.connect(self.__too_many_ghost_shots)
        self.screenshot_worker.error.connect(self.__screenshot_worker_error)
        self.screenshot_worker.paused.connect(self.__screenshot_worker_paused)
        self.screenshot_worker.resumed.connect(self.__screenshot_worker_resumed)
        self.screenshot_thread.start()

    def __too_many_ghost_shots(self):
        self.screenshot_worker.pause()
        QMessageBox.warning(self, "Ghost Shots Detected",
                            "Too many shots were received within a short space of time.\nSet the Camera option in the Rapsodo Range to 'Stationary' for a better result.")

    def __screenshot_worker_error(self, error):
        msg = ''
        if isinstance(error[0], WindowNotFoundException):
            msg = f"Screen capture application ' {self.current_device.window_name}' does not seem to be running.\nPlease start the app, then press the 'Restart' button to restart the connector."
            self.__screenshot_worker_paused()
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
            self.__screenshot_worker_paused()
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        QMessageBox.warning(self, "Connector Error", msg)

    def __screenshot_worker_paused(self):
        self.main_window.connector_status.setText('Not Ready')
        self.main_window.connector_status.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.main_window.restart_button.setEnabled(True)
        self.main_window.pause_button.setEnabled(False)

    def __screenshot_worker_resumed(self):
        self.screenshot_worker.ignore_shots_after_restart()
        self.main_window.connector_status.setText('Ready')
        self.main_window.connector_status.setStyleSheet("QLabel { background-color : green; color : white; }")
        self.main_window.restart_button.setEnabled(False)
        self.main_window.pause_button.setEnabled(True)
