import json
import logging

from PySide6.QtBluetooth import QBluetoothDeviceInfo
from PySide6.QtWidgets import QMessageBox
from src.ball_data import BallData
from src.bluetooth.bluetooth_device_scanner import BluetoothDeviceScanner
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems


class DeviceLaunchMonitorBluetoothBase(DeviceBase):

    def __init__(self, main_window, device_names: list[str]):
        DeviceBase.__init__(self, main_window)
        self.device = None
        self.device_names = device_names
        self.scanner = BluetoothDeviceScanner(self.device_names)
        self.__setup_signals()
        self.__not_connected_status()

    def setup_device_thread(self) -> None:
        super().setup_device_thread()
        #self.device_worker.listening.connect(self.__listening)
        #self.device_worker.connected.connect(self.__connected)
        #self.device_worker.finished.connect(self.__not_connected_status)
        #self.device_worker.shot_error.connect(self.__send_shot_error)
        #self.device_worker.disconnected.connect(self.__listening)
        #self.device_worker.BLUETOOTH_shot.connect(self.__shot_sent)

    def __setup_signals(self) -> None:
        self.main_window.start_server_button.clicked.connect(self.__server_start_stop)
        # Scanner signals
        self.scanner.status_update.connect(self.__status_update)
        self.scanner.device_found.connect(self.device_found)
        self.scanner.device_not_found.connect(self.__device_not_found)
        self.scanner.error.connect(self.__scanner_error)


        #self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        #self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        #self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        #self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def __server_start_stop(self) -> None:
        if self.device is None:
            QMessageBox.warning(self.main_window, "Prepare Launch Monitor", self.start_message)
            self.scanner.scan()
        else:
            self.__disconnect_device()

    def device_found(self, device: QBluetoothDeviceInfo) -> None:
        self.__update_ui(None, 'orange', device.name(), 'red', 'Stop', False)
        self.__update_rssi(device.rssi())

    def __scanner_error(self, error) -> None:
        msg = f"The following error occurred while scanning for a device:\n\n{error}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH, f'{msg}')
        QMessageBox.warning(self.main_window, "Error while scanning for a device", msg)
        self.__not_connected_status()

    def __device_not_found(self) -> None:
        msg = f"No device found.\n\n{self.start_message}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH, f'{msg}')
        QMessageBox.warning(self.main_window, "No device found", msg)
        self.__not_connected_status()

    def __status_update(self, status_message) -> None:
        self.__update_ui(status_message, 'orange', 'No Device', 'red', 'Stop', False)

    def __not_connected_status(self) -> None:
        self.__update_ui('Not Connected', 'red', 'No Device', 'red', 'Start', True)
        self.main_window.launch_monitor_rssi_label.setText('')
        self.main_window.launch_monitor_rssi_label.setStyleSheet(f"QLabel {{ background-color : white; color : white; }}")
        self.main_window.token_expiry_label.setText('')
        self.main_window.token_expiry_label.setStyleSheet(f"QLabel {{ background-color : white; color : white; }}")

    def _setup_device_signals(self) -> None:
        self.device.status_update.connect(self.__device_status_update)
        self.device.error.connect(self.__device_error)
        self.device.connected.connect(self.__device_connected)

        #self.device.error.connect(self.__send_shot_error)
        #self.device.client_disconnected.connect(self.__disconnected)

    def __device_connected(self, status) -> None:
        print('xxxxx connected signal')
        self.__update_ui(status, 'green', None, 'green', 'Stop', True)


    def __device_status_update(self, status_message, device_name) -> None:
        self.__update_ui(status_message, 'orange', device_name, 'red', 'Stop', False)

    def __device_error(self, error) -> None:
        self.__disconnect_device()
        logging.debug(f"Device error: {error}")
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH, error)
        QMessageBox.warning(self.main_window, "Unexpected error", error)
        self.__not_connected_status()

    def __update_rssi(self, rssi) -> None:
        self.main_window.launch_monitor_rssi_label.setText(f"RSSI: {rssi}")
        if rssi < -50 and rssi > -70:
            color = 'green'
        elif rssi < -70 and rssi > -80:
            color = 'orange'
        else:
            color = 'red'
        self.main_window.launch_monitor_rssi_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def __update_ui(self, message, color, status, status_color, button, enabled=True) -> None:
        if status is not None:
            self.main_window.server_connection_label.setText(status)
        self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : {status_color}; color : white; }}")
        if button is not None:
            self.main_window.start_server_button.setText(button)
        self.main_window.start_server_button.setEnabled(enabled)
        if message is not None:
            self.main_window.server_status_label.setText(message)
        self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def __shot_sent(self, shot_data) -> None:
        data = json.loads(shot_data.decode("utf-8"))
        balldata = BallData()
        balldata.from_gspro(data)
        balldata.club = self.main_window.gspro_connection.current_club
        print(f'balldata: {balldata.to_json()} club: {self.main_window.gspro_connection.current_club}')
        balldata.good_shot = True
        if self.prev_shot is None or self.prev_shot.eq(balldata) > 0:
            self.main_window.shot_sent(balldata)
            self.prev_shot = balldata

    def __gspro_message(self, message) -> None:
        self.device_worker.send_msg(message)

    @property
    def start_message(self) -> str:
        return ' '

    def __disconnected(self, device):
        print('__disconnected')
        self.__not_connected_status()

    def __client_status_update(self, status) -> None:
        self.__update_ui(status, 'orange', None, 'red', 'Stop', False)

    def __connected(self):
        self.main_window.server_connection_label.setText(f'Connected {self.main_window.settings.BLUETOOTH_ip_address}:{self.main_window.settings.BLUETOOTH_port}')
        self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")

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
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "Relay Send to GSPro Error", msg)

    def __disconnect_device(self):
        if self.device is not None:
            self.device.disconnect_device()
            self.device = None
            self.__not_connected_status()

    def shutdown(self):
        self.__disconnect_device()
        super().shutdown()