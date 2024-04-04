import logging
from PySide6.QtCore import Signal
from src.device_base import DeviceBase


class DevicePuttingBase(DeviceBase):

    putt_shot = Signal(object)

    def __init__(self, main_window):
        super(DeviceBase, self).__init__(main_window)
        self.main_window = main_window

    def setup(self):
        self.setup_device_thread()
        self.setup_signals()
        self.device_worker_paused()

    def start_app(self):
        return

    def setup_signals(self):
        self.main_window.gspro_connection.club_selected.connect(self.club_selected)
        self.main_window.putting_settings_form.cancel.connect(self.resume)
        self.main_window.actionPuttingSettings.triggered.connect(self.pause)
        self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        self.device_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)

    def club_selected(self, club_data):
        self.device_worker.club_selected(club_data['Player']['Club'])
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")

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
        if self.device_worker is not None:
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

    def resume(self):
        self.reload_putting_rois()
        super().resume()

    def reload_putting_rois(self):
        pass
