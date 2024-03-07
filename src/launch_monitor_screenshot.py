from PySide6.QtCore import QThread, QCoreApplication
from PySide6.QtWidgets import QMessageBox

from src.DevicesForm import DevicesForm
from src.SelectDeviceForm import SelectDeviceForm
from src.custom_exception import WindowNotFoundException
from src.launch_monitor_base import LaunchMonitorBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src import MainWindow
from src.screenshot_worker_launch_monitor import ScreenshotWorkerLaunchMonitor


class LaunchMonitorScreenshot(LaunchMonitorBase):

    def __init__(self, main_window: MainWindow):
        LaunchMonitorBase.__init__(self, main_window)
        self.current_device = None
        self.devices = None
        self.select_device = None

    def setup(self):
        super().setup()
        self.launch_monitor_worker = ScreenshotWorkerLaunchMonitor(self.main_window.settings)
        self.devices = DevicesForm(self.main_window.app_paths)
        self.select_device = SelectDeviceForm(main_window=self)
        self.__setup_launch_monitor_thread()
        self.__setup_signals()
        self.__update_selected_mirror_app()

    def __setup_launch_monitor_thread(self):
        self.launch_monitor_thread = QThread()
        self.launch_monitor_worker.moveToThread(self.launch_monitor_thread)
        self.launch_monitor_thread.started.connect(self.launch_monitor_worker.run)
        self.launch_monitor_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self.launch_monitor_worker.bad_shot.connect(self.main_window.bad_shot)
        self.launch_monitor_worker.same_shot.connect(self.main_window.gspro_connection.club_selecion_worker.run)
        self.launch_monitor_worker.bad_shot.connect(self.main_window.gspro_connection.club_selecion_worker.run)
        self.launch_monitor_worker.too_many_ghost_shots.connect(self.__too_many_ghost_shots)
        self.launch_monitor_worker.error.connect(self.__launch_monitor_worker_error)
        self.launch_monitor_worker.paused.connect(self.__launch_monitor_worker_paused)
        self.launch_monitor_worker.resumed.connect(self.__launch_monitor_worker_resumed)
        self.launch_monitor_thread.start()
        super().pause()
        
    def __setup_signals(self):
        self.select_device.selected.connect(self.__device_selected)
        self.select_device.cancel.connect(self.__device_select_cancelled)
        self.main_window.select_device_button.clicked.connect(self.__select_device)


    def __too_many_ghost_shots(self):
        super().pause()
        QMessageBox.warning(self.main_window, "Ghost Shots Detected",
                            "Too many shots were received within a short space of time.\nSet the Camera option in the Rapsodo Range to 'Stationary' for a better result.")

    def __launch_monitor_worker_error(self, error):
        msg = ''
        if isinstance(error[0], WindowNotFoundException):
            msg = f"Screen capture application ' {self.current_device.window_name}' does not seem to be running.\nPlease start the app, then press the 'Restart' button to restart the connector."
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        QMessageBox.warning(self.main_window, "Connector Error", msg)

    def __launch_monitor_worker_paused(self):
        self.main_window.connector_status.setText('Not Ready')
        self.main_window.connector_status.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.main_window.restart_button.setEnabled(True)
        self.main_window.pause_button.setEnabled(False)

    def __launch_monitor_worker_resumed(self):
        self.launch_monitor_worker.ignore_shots_after_restart()
        self.main_window.connector_status.setText('Ready')
        self.main_window.connector_status.setStyleSheet("QLabel { background-color : green; color : white; }")
        self.main_window.restart_button.setEnabled(False)
        self.main_window.pause_button.setEnabled(True)

    def resume(self):
        if not self.current_device is None and self.main_window.gspro_connection.connected:
            super().resume()

    def __device_select_cancelled(self):
        if not self.current_device is None and self.main_window.gspro_connection.connected:
            self.launch_monitor_worker.change_device(self.current_device)
            super().resume()

    def __device_selected(self, device):
        self.current_device = device
        self.__update_selected_mirror_app()
        self.launch_monitor_worker.change_device(device)
        if self.main_window.gspro_connection.connected:
            super().resume()

    def __update_selected_mirror_app(self):
        if not self.current_device is None:
            self.main_window.selected_device.setText(self.current_device.name)
            self.main_window.selected_device.setStyleSheet("QLabel { background-color : green; color : white; }")
            self.main_window.selected_mirror_app.setText(self.current_device.window_name)
            self.main_window.selected_mirror_app.setStyleSheet("QLabel { background-color : green; color : white; }")
        else:
            self.main_window.selected_device.setText('No Device')
            self.main_window.selected_device.setStyleSheet("QLabel { background-color : red; color : white; }")
            self.main_window.selected_mirror_app.setText('No Mirror App')
            self.main_window.selected_mirror_app.setStyleSheet("QLabel { background-color : red; color : white; }")
        QCoreApplication.processEvents()

    def __select_device(self):
        super().pause()
        self.select_device.show()
