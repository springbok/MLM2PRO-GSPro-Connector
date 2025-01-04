import logging
from PySide6.QtWidgets import QMessageBox
from src.DevicesForm import DevicesForm
from src.SelectDeviceForm import SelectDeviceForm
from src.custom_exception import WindowNotFoundException
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.settings import LaunchMonitor
from src.worker_screenshot_device_launch_monitor import WorkerScreenshotDeviceLaunchMonitor


class DeviceLaunchMonitorScreenshot(DeviceBase):

    def __init__(self, main_window):
        DeviceBase.__init__(self, main_window)
        self.current_device = None        
        self.devices = None
        self.select_device = None
        self.device_worker = WorkerScreenshotDeviceLaunchMonitor(self.main_window.settings)
        self.devices = DevicesForm(self.main_window.app_paths)
        self.select_device = SelectDeviceForm(self.main_window)
        self.setup_device_thread()
        self.__setup_signals()
        self.__update_selected_mirror_app()
        self.device_worker_paused()
        self.__display_training_file()

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self.device_worker.bad_shot.connect(self.__bad_shot)
        self.device_worker.too_many_ghost_shots.connect(self.__too_many_ghost_shots)

    def __bad_shot(self, balldata):
        self.main_window.shot_sent(balldata)

    def __setup_signals(self):
        self.select_device.selected.connect(self.__device_selected)
        self.select_device.cancel.connect(self.__device_select_cancelled)
        self.main_window.select_device_button.clicked.connect(self.__select_device)
        self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        self.main_window.putting_settings_form.cancel.connect(self.resume)
        self.main_window.actionPuttingSettings.triggered.connect(self.pause)
        self.main_window.actionDevices.triggered.connect(self.__devices)

    def __club_selected(self, club_data):
        self.device_worker.club_selected(club_data['Player']['Club'])
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")

    def __too_many_ghost_shots(self):
        self.pause()
        QMessageBox.warning(self.main_window, "Ghost Shots Detected",
                            "Too many shots were received within a short space of time.\nSet the Camera option in the Rapsodo Range to 'Stationary' for a better result.")

    def device_worker_error(self, error):
        if isinstance(error[0], WindowNotFoundException):
            msg = f"Screen capture application ' {self.current_device.window_name}' does not seem to be running.\nPlease start the app, then press the 'Restart' button to restart the connector."
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        QMessageBox.warning(self.main_window, "Connector Error", msg)

    def device_worker_paused(self):
        status = 'Not Running'
        color = 'red'
        restart = False
        if self.is_running():
            if self.main_window.gspro_connection.connected:
                color = 'orange'
                status = 'Paused'
                if self.device_worker.selected_club() != "PT":
                    restart = True
            else:
                status = 'Waiting GSPro'
                color = 'red'
                restart = False
        self.main_window.connector_status.setText(status)
        self.main_window.connector_status.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
        self.main_window.restart_button.setEnabled(restart)
        self.main_window.pause_button.setEnabled(False)
        if self.device_worker is not None:
            self.device_worker.ignore_shots_after_restart()

    def update_mevo_mode(self):
        if self.main_window.settings.device_id == LaunchMonitor.MEVOPLUS:
            self.main_window.mode_label.setText(f"Offline Mode: {self.main_window.settings.mevo_plus['offline_mode']}")
            self.main_window.mode_label.setStyleSheet(
                f"QLabel {{ background-color : blue; color : white; }}")
        else:
            self.main_window.mode_label.setText('')
            self.main_window.mode_label.setStyleSheet(
                f"QLabel {{ background-color : white; color : white; }}")

    def __display_training_file(self):
        train_file = 'train'
        if self.main_window.settings.device_id == LaunchMonitor.MEVOPLUS:
            train_file = 'mevo'
        elif self.main_window.settings.device_id == LaunchMonitor.FSKIT:
            train_file = 'fskit'
        elif self.main_window.settings.device_id == LaunchMonitor.TRACKMAN:
            train_file = 'trackman'
        elif self.main_window.settings.device_id == LaunchMonitor.TRUGOLF_APOGEE:
            train_file = 'apex'
        elif self.main_window.settings.device_id == LaunchMonitor.UNEEKOR:
            train_file = 'uneekor'
        elif self.main_window.settings.device_id == LaunchMonitor.SKYTRAKPLUS:
            train_file = 'skytrak'
        elif self.main_window.settings.device_id == LaunchMonitor.R50:
            train_file = 'r50'
        elif self.main_window.settings.device_id == LaunchMonitor.XSWINGPRO:
            train_file = 'xswingpro'
        elif self.main_window.settings.device_id == LaunchMonitor.SQUARE:
            train_file = 'square'
        elif self.main_window.settings.device_id == LaunchMonitor.SC4:
            train_file = 'voicecaddiesc4'
        self.main_window.ocr_training_file_label.setText(f"OCR File: {train_file}")
        self.main_window.ocr_training_file_label.setStyleSheet(f"QLabel {{ background-color : blue; color : white; }}")
        self.update_mevo_mode()

    def device_worker_resumed(self):
        msg = 'Running'
        color = 'green'
        restart = False
        pause = True
        if not self.main_window.gspro_connection.connected:
            msg = 'Waiting GSPro'
            color = 'red'
            pause = False
        # self.device_worker.ignore_shots_after_restart()
        self.main_window.connector_status.setText(msg)
        self.main_window.connector_status.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
        self.main_window.restart_button.setEnabled(restart)
        self.main_window.pause_button.setEnabled(pause)

    def __device_select_cancelled(self):
        if not self.current_device is None and self.main_window.gspro_connection.connected:
            self.device_worker.change_device(self.current_device)
            self.resume()

    def __device_selected(self, device):
        self.current_device = device
        self.__update_selected_mirror_app()
        self.device_worker.change_device(device)
        if self.is_running():
            if self.is_paused():
                self.resume()
        else:
            self.start()
        self.device_worker.club_selected(self.main_window.gspro_connection.current_club)


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

    def __select_device(self):
        self.pause()
        self.select_device.show()

    def shutdown(self):
        super().shutdown()
        self.select_device.shutdown()

    def __devices(self):
        self.devices.show()