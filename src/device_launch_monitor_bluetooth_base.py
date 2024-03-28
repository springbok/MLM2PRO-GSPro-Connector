import asyncio
import json
import logging
import traceback

from PySide6.QtWidgets import QMessageBox
from bleak import BLEDevice, AdvertisementData

from src.ball_data import BallData
from src.bluetooth.bluetooth_device_scanner import BluetoothDeviceScanner
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems


class DeviceLaunchMonitorBluetoothBase(DeviceBase):

    def __init__(self, main_window, device_names: list[str]):
        DeviceBase.__init__(self, main_window)
        self.api = None
        self.device_names = device_names
        self.scanner = BluetoothDeviceScanner(self.device_names)
        self.setup_signals()
        self.__not_connected_status()
        self.launch_monitor_task = None

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
        self.scanner.status_update.connect(self.__scanning)
        self.scanner.device_found.connect(self._device_found)
        self.scanner.error.connect(self.__scanner_error)
        self.scanner.device_not_found.connect(self.__no_device_found)
        # Bluetooth client

        #self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        #self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        #self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        #self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def _setup_api_signals(self):
        if self.api is not None and self.api.client is not None:
            # Bluetooth client
            self.api.client.client_disconnected.connect(self.__client_disconnected)
            self.api.client.client_connecting.connect(self.__client_connecting)
            self.api.client.client_connected.connect(self.__client_connected)
            self.api.client.client_connecting.connect(self.__client_connecting)
            self.api.error.connect(self._unexpected_error)

    def __client_connecting(self, device):
        self.__update_ui('Connecting...', 'orange', device, 'green', 'Stop', False)

    def __client_disconnecting(self, device):
        self.__update_ui('Disconnecting...', 'orange', device, 'green', 'Stop', False)

    def __client_connected(self, device):
        self.__update_ui('Connected', 'orange', device, 'green', 'Stop', True)

    def __client_disconnected(self, device):
        self.__not_connected_status()
        self.main_window.launch_monitor_rssi_label.setStyleSheet(f"QLabel {{ background-color : white; color : white; }}")
        self.main_window.launch_monitor_rssi_label.setText("")
        self.api = None

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
        print('__no_device_found')
        self.__not_connected_status()
        QMessageBox.warning(self.main_window, "No Device Found", 'No device found. Please ensure your launch monitor is turned on and a STREADY RED light is showing.')


    def __not_connected_status(self) -> None:
        self.__update_ui('Not Connected', 'red', 'No Device', 'red', 'Start', True)

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

    def __server_start_stop(self) -> None:
        print('__server_start_stop')
        if self.api is None:
            QMessageBox.warning(self.main_window, "Prepare Launch Monitor", self.start_message())
            asyncio.ensure_future(self.scanner.scan())
        else:
            print('api not none')
            #self.device_worker.stop()
            self.shutdown()

    def start_message(self) -> str:
        return ' '

    def __scanner_error(self, error):
        msg = f"The following error occurred while scanning for devices:\n{error}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH_CONNECTOR, f'{msg}')
        QMessageBox.warning(self.main_window, "Error while scanning for devices", msg)

    def __scanning(self, status_message):
        self.__update_ui(status_message, 'orange', 'No Device', 'red', 'Stop', False)

    def __client_status_update(self, status):
        print(f'__client_status_update: {status}' )
        self.__update_ui(status, 'orange', None, 'red', 'Stop', False)

    def device_worker_error(self, error):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH_CONNECTOR, f'Error: {format(error)}')
        QMessageBox.warning(self.main_window, "LM Error", f'{format(error)}')
        self.stop()

    def __listening(self):
        self.main_window.start_server_button.setText('Stop')
        self.main_window.server_status_label.setText('Running')
        self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        self.main_window.server_connection_label.setText(f'Listening {self.main_window.settings.relay_server_ip_address}:{self.main_window.settings.relay_server_port}')
        self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : orange; color : white; }}")

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
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH_CONNECTOR, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "Relay Send to GSPro Error", msg)

    def _unexpected_error(self, error):
        self.shutdown()
        msg = f"An error has occurred when connecting to your device.\n\nError: {format(error)}\n\nPlease fix the error and retry the connection to the Bluetooth Device."
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH_CONNECTOR, msg)
        QMessageBox.warning(self.main_window, "Bluetooth Connector Error", msg)

    def shutdown(self):
        if self.api is not None:
            print('stopping api')
            if self.launch_monitor_task is not None and not self.launch_monitor_task.done() and not self.launch_monitor_task.cancelled():
                print('xxxx cancel taks')
                self.launch_monitor_task.cancel()
            print('stop')
            asyncio.ensure_future(self.api.stop())

    def _start_api(self):
        if self.api is not None:
            try:
                self.launch_monitor_task = asyncio.ensure_future(self.api.start())
            except Exception as e:
                self._unexpected_error((e, traceback.format_exc()))

        # if self.client is not None:
        #    self.client.reset_connection()
        #    self.client = None
        # self.device_worker = WorkerDeviceLaunchMonitorBluetoothMLM2PRO(self.main_window.settings, self.api, device)
        # self.client = BluetoothClient()
        # self.client.connect_client(device)
