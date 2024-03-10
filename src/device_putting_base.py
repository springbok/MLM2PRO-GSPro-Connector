import logging
from PySide6.QtCore import Signal
from src import MainWindow
from src.device_base import DeviceBase


class DevicePuttingBase(DeviceBase):

    putt_shot = Signal(object)

    def __init__(self, main_window: MainWindow):
        super(DeviceBase, self).__init__(main_window)
        self.main_window = main_window
        self.putting_settings = main_window.putting_settings

    def setup(self):
        self.start_app()
        self.setup_device_thread()
        self.setup_signals()
        self.device_worker_paused()

    def start_app(self):
        return

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)

    def setup_signals(self):
        self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        self.main_window.putting_settings_form.cancel.connect(self.resume)
        self.main_window.actionPuttingSettings.triggered.connect(self.pause)
        self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)

    def __club_selected(self, club_data):
        if club_data['Player']['Club'] == "PT":
            logging.debug('Putter selected resuming putt processing')
            self.pause()
        else:
            logging.debug('Club other than putter selected pausing putt processing')
            self.resume()

    def device_worker_paused(self):
        msg = 'Start'
        status = 'Not Running'
        color = 'red'
        if self.is_running():
            msg = 'Resume'
            if self.main_window.gspro_connection.connected:
                color = 'orange'
                status = 'Paused'
            else:
                status = 'Waiting GSPro'
                color = 'red'
        self.main_window.putting_server_button.setText(msg)
        self.main_window.putting_server_status_label.setText(status)
        self.main_window.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

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
