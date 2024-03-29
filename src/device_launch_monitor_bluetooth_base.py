import asyncio
import json
import logging
import traceback

from PySide6.QtWidgets import QMessageBox
from bleak import BLEDevice, AdvertisementData

from src.ball_data import BallData
from src.bluetooth.bluetooth_device_scanner import BluetoothDeviceScanner
from src.bluetooth.bluetooth_signal import BluetoothSignal
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems


class DeviceLaunchMonitorBluetoothBase(DeviceBase):

    def __init__(self, main_window, device_names: list[str]):
        DeviceBase.__init__(self, main_window)
        self.device = None
        self.device_names = device_names
        self.scanner = BluetoothDeviceScanner(self.device_names)
        self.setup_signals()
        self.__not_connected_status()

    def setup_device_thread(self) -> None:
        pass
        #super().setup_device_thread()
        #self.device_worker.listening.connect(self.__listening)
        #self.device_worker.connected.connect(self.__connected)
        #self.device_worker.finished.connect(self.__not_connected_status)
        #self.device_worker.shot_error.connect(self.__send_shot_error)
        #self.device_worker.disconnected.connect(self.__listening)
        #self.device_worker.relay_server_shot.connect(self.__shot_sent)

    def setup_signals(self) -> None:
        self.main_window.start_server_button.clicked.connect(self.__server_start_stop)
        # Scanner signals
        self.scanner.started.connect(self.__update_status)
        self.scanner.device_found.connect(self._device_found)
        self.scanner.device_not_found.connect(self.__no_device_found)
        # Bluetooth client

        #self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        #self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        #self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        #self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def _device_found(self, device: BLEDevice, advertised_data: AdvertisementData) -> None:
        print(f'_device_found base: {device.name}')
        self.__update_ui('Found', 'orange', device.name, 'red', 'Stop', True)
        self.main_window.launch_monitor_rssi_label.setText(f"RSSI: {advertised_data.rssi}")
        if advertised_data.rssi < -50 and advertised_data.rssi > -70:
            color = 'green'
        elif advertised_data.rssi < -70 and advertised_data.rssi > -80:
            color = 'orange'
        else:
            color = 'red'
        self.main_window.launch_monitor_rssi_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def __no_device_found(self):
        self.__not_connected_status()
        QMessageBox.warning(self.main_window,
                            "No Device Found",
                            f'No device was found during the scan. {self._start_message}')

    def _setup_device_signals(self):
        if self.device is not None:
            # Bluetooth client
            self.device.device_disconnecting.connect(self.__update_status)
            self.device.device_disconnected.connect(self.__client_disconnected)
            self.device.device_connecting.connect(self.__update_status)
            self.device.device_connected.connect(self.__update_status)
            self.device.device_setting_up.connect(self.__update_status)
            self.device.device_error.connect(self.__device_error)

    def __update_status(self, signal: BluetoothSignal):
        print(f'__update_status: {signal.connection_status} {signal.connection_color} {signal.device_message} {signal.device_color} {signal.button_message} {signal.button_enabled}')
        self.__update_ui(signal.connection_status, signal.connection_color,
                         signal.device_message, signal.device_color,
                         signal.button_message, signal.button_enabled)

    def __device_error(self, heading, error):
        print(f'__device_error: {error} {heading}')
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH_CONNECTOR, error)
        QMessageBox.warning(self.main_window, heading, error)

    def __client_disconnected(self):
        self.__not_connected_status()
        self.main_window.launch_monitor_rssi_label.setStyleSheet(f"QLabel {{ background-color : white; color : white; }}")
        self.main_window.launch_monitor_rssi_label.setText("")
        self.device = None

    def __not_connected_status(self) -> None:
        self.__update_ui('Not Connected', 'red', 'No Device', 'red', 'Start', True)

    def __update_ui(self, connection_status, connection_color, device_message, device_color, button_message, button_enabled=True) -> None:
        if button_message is not None:
            self.main_window.server_connection_label.setText(device_message)
            self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : {device_color}; color : white; }}")
        if button_message is not None:
            self.main_window.start_server_button.setText(button_message)
        self.main_window.start_server_button.setEnabled(button_enabled)
        if connection_status is not None:
            self.main_window.server_status_label.setText(connection_status)
            self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : {connection_color}; color : white; }}")

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

    def __server_start_stop(self) -> None:
        if self.device is None:
            QMessageBox.warning(self.main_window, "Prepare Launch Monitor", self._start_message)
            asyncio.ensure_future(self.scanner.scan())
        else:
            #self.device_worker.stop()
            self.__shutdown()

    def start_message(self) -> str:
        return ' '

    def __club_selected(self, club_data):
        self.device_worker.club_selected(club_data['Player']['Club'])
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")

    def __send_shot_error(self, error):
        msg = f"Error while trying to send shot to GSPro.\nMake sure GSPro API Connect is running.\nStart/restart API Connect from GSPro.\nPress 'Connect' to reconnect to GSPro."
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH_CONNECTOR, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "Relay Send to GSPro Error", msg)

    def __shutdown(self):
        if self.device is not None:
            self.device.stop()
            self.device = None
            self.__client_disconnected()

    def _connect_device(self):
        if self.device is not None:
            try:
                asyncio.ensure_future(self.device.connect_device())
            except Exception as e:
                self.__shutdown()
                self.__device_error('Connection error', traceback.format_exc())

        # if self.client is not None:
        #    self.client.reset_connection()
        #    self.client = None
        # self.device_worker = WorkerDeviceLaunchMonitorBluetoothMLM2PRO(self.main_window.settings, self.device, device)
        # self.client = BluetoothClient()
        # self.client.connect_client(device)
