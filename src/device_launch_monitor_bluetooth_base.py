import json
import logging

from PySide6.QtBluetooth import QBluetoothDeviceInfo
from PySide6.QtWidgets import QMessageBox
from src.ball_data import BallData
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_device_launch_monitor_relay_server import WorkerDeviceLaunchMonitorRelayServer


class DeviceLaunchMonitorBluetoothBase(DeviceBase):

    def __init__(self, main_window, api):
        DeviceBase.__init__(self, main_window)
        self.api = api
        self.__setup_signals()
        self.not_connected_status()

    def setup_device_thread(self):
        super().setup_device_thread()
        #self.device_worker.listening.connect(self.__listening)
        #self.device_worker.connected.connect(self.__connected)
        #self.device_worker.finished.connect(self.not_connected_status)
        #self.device_worker.shot_error.connect(self.__send_shot_error)
        #self.device_worker.disconnected.connect(self.__listening)
        #self.device_worker.relay_server_shot.connect(self.__shot_sent)

    def __setup_signals(self):
        self.main_window.start_server_button.clicked.connect(self.server_start_stop)
        #self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        #self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def not_connected_status(self):
        self.__update_ui('Not Connected', 'red', 'No Device', 'red', 'Start', True)

    def __update_ui(self, message, color, status, status_color, button, enabled=True):
        if status is not None:
            self.main_window.server_connection_label.setText(status)
            self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : {status_color}; color : white; }}")
        if button is not None:
            self.main_window.start_server_button.setText(button)
        self.main_window.start_server_button.setEnabled(enabled)
        if message is not None:
            self.main_window.server_status_label.setText(message)
            self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def __shot_sent(self, shot_data):
        data = json.loads(shot_data.decode("utf-8"))
        balldata = BallData()
        balldata.from_gspro(data)
        balldata.club = self.main_window.gspro_connection.current_club
        print(f'balldata: {balldata.to_json()} club: {self.main_window.gspro_connection.current_club}')
        balldata.good_shot = True
        if self.prev_shot is None or self.prev_shot.eq(balldata) > 0:
            self.main_window.shot_sent(balldata)
            self.prev_shot = balldata

    def __gspro_message(self, message):
        self.device_worker.send_msg(message)

    def server_start_stop(self):
        pass

    def setup_worker_signal(self):
        if self.device_worker is not None and self.device_worker.scanner is not None:
            self.device_worker.scanner.status_update.connect(self.__scanning)
            self.device_worker.scanner.device_update.connect(self.__device_found)

    def __scanning(self, status_message):
        self.__update_ui(status_message, 'orange', 'No Device', 'red', 'Stop', False)

    def __device_found(self, device: QBluetoothDeviceInfo):
        self.__update_ui(None, 'orange', device.name(), 'red', 'Stop', False)

    def device_worker_error(self, error):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.RELAY_SERVER, f'Error: {format(error)}')
        QMessageBox.warning(self.main_window, "LM Error", f'{format(error)}')
        self.stop()

    def __listening(self):
        self.main_window.start_server_button.setText('Stop')
        self.main_window.server_status_label.setText('Running')
        self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        self.main_window.server_connection_label.setText(f'Listening {self.main_window.settings.relay_server_ip_address}:{self.main_window.settings.relay_server_port}')
        self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : orange; color : white; }}")

    def __connected(self):
        self.main_window.server_connection_label.setText(f'Connected {self.main_window.settings.relay_server_ip_address}:{self.main_window.settings.relay_server_port}')
        self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")

    def not_connected_status(self):
        status = 'Not Running'
        color = 'red'
        button = 'Start'
        if self.is_running():
            button = 'Stop'
            if self.main_window.gspro_connection.connected:
                color = 'orange'
                status = 'Paused'
            else:
                status = 'Waiting GSPro'
                color = 'red'
        else:
            self.main_window.server_connection_label.setText('No Connection')
            self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : red; color : white; }}")
        self.main_window.start_server_button.setText(button)
        self.main_window.server_status_label.setText(status)
        self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def device_worker_resumed(self):
        self.main_window.start_server_button.setText('Stop')
        msg = 'Running'
        color = 'green'
        if not self.main_window.gspro_connection.connected:
            msg = 'Waiting GSPro'
            color = 'red'
        self.main_window.server_status_label.setText(msg)
        self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def __club_selected(self, club_data):
        self.device_worker.club_selected(club_data['Player']['Club'])
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")

    def __send_shot_error(self, error):
        msg = f"Error while trying to send shot to GSPro.\nMake sure GSPro API Connect is running.\nStart/restart API Connect from GSPro.\nPress 'Connect' to reconnect to GSPro."
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.RELAY_SERVER, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "Relay Send to GSPro Error", msg)
