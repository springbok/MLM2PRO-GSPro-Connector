import json
import logging

from PySide6.QtBluetooth import QBluetoothDeviceInfo
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox
from src.ball_data import BallData
from src.bluetooth.bluetooth_device_rssi_scanner import BluetoothDeviceRssiScanner
from src.bluetooth.bluetooth_device_scanner import BluetoothDeviceScanner
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems


class DeviceLaunchMonitorBluetoothBase(DeviceBase):

    RSSI_SCAN_INTERVAL = 5000

    def __init__(self, main_window, device_names: list[str]):
        DeviceBase.__init__(self, main_window)
        self._device = None
        self._device_names: list[str] = device_names
        self._scanner: BluetoothDeviceScanner  = BluetoothDeviceScanner(self._device_names)
        self._rssi_scanner: BluetoothDeviceRssiScanner = BluetoothDeviceRssiScanner(self._device_names)
        self._rssi_timer: QTimer = QTimer()
        self._rssi_timer.setInterval(DeviceLaunchMonitorBluetoothBase.RSSI_SCAN_INTERVAL)
        self._rssi_timer.timeout.connect(self._rssi_scanner.scan)
        self.__setup_signals()
        self.__not_connected_status()

    def setup_device_thread(self) -> None:
        super().setup_device_thread()

    def __setup_signals(self) -> None:
        self.main_window.start_server_button.clicked.connect(self.server_start_stop)
        self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        # Scanner signals
        self._scanner.status_update.connect(self.__status_update)
        self._scanner.device_found.connect(self.device_found)
        self._scanner.device_not_found.connect(self.__device_not_found)
        self._scanner.error.connect(self.__scanner_error)

        self._rssi_scanner.rssi.connect(self.__update_rssi)

    def __club_selected(self, club_data):
        self._device.club_selected(club_data['Player']['Club'])
        logging.debug(f"{self.__class__.__name__} Club selected: {club_data['Player']['Club']}")

    def server_start_stop(self) -> None:
        if self._device is None:
            self._scanner.scan()
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
        self.main_window.launch_monitor_event_label.setText('')
        self.main_window.launch_monitor_event_label.setStyleSheet(f"QLabel {{ background-color : white; color : white; }}")
        self.main_window.launch_monitor_battery_label.setText('')
        self.main_window.launch_monitor_battery_label.setStyleSheet(f"QLabel {{ background-color : white; color : white; }}")

    def _setup_device_signals(self) -> None:
        self._device.status_update.connect(self.__device_status_update)
        self._device.error.connect(self.__device_error)
        self._device.connected.connect(self.__device_connected)
        self._device.update_battery.connect(self.__update_battery)
        self._device.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self._device.launch_monitor_event.connect(self.__launch_monitor_event)

    def __launch_monitor_event(self, event: str) -> None:
        self.main_window.launch_monitor_event_label.setText(f"LM: {event}")
        self.main_window.launch_monitor_event_label.setStyleSheet(f"QLabel {{ background-color : blue; color : white; }}")

    def __shot_sent(self, ball_data: BallData) -> None:
        print(f"Shot sent: {json.dumps(ball_data.to_json())}")
        if self.main_window.gspro_connection.connected:
            self.main_window.shot_sent(ball_data)

    def __update_battery(self, battery: int) -> None:
        self.main_window.launch_monitor_battery_label.setText(f"Battery: {battery}")
        if battery > 50:
            color = 'green'
        elif battery > 20:
            color = 'orange'
        else:
            color = 'red'
        self.main_window.launch_monitor_battery_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def __device_connected(self, status) -> None:
        self.__update_ui(status, 'green', None, 'green', 'Stop', True)
        self._rssi_timer.start()

    def __device_status_update(self, status_message, device_name) -> None:
        self.__update_ui(status_message, 'orange', device_name, 'red', 'Stop', False)

    def __device_error(self, error) -> None:
        if self._device is not None:
            self.__disconnect_device()
            logging.debug(f"Device error: {error}")
            self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.BLUETOOTH, error)
            QMessageBox.warning(self.main_window, "Bluetooth Connection Error", error)
        self.__not_connected_status()

    def __update_rssi(self, rssi) -> None:
        logging.debug(f"inside __update_rssi: {rssi}")

        self.main_window.launch_monitor_rssi_label.setText(f"RSSI: {rssi}")
        if rssi > -60:
            color = 'green'
        elif rssi <= -60 and rssi >= -80:
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

    @property
    def start_message(self) -> str:
        return ' '

    def __client_status_update(self, status) -> None:
        self.__update_ui(status, 'orange', None, 'red', 'Stop', False)

    def __disconnect_device(self):
        if self._device is not None:
            print(f'{self.__class__.__name__} Disconnecting device')
            self._device.disconnect_device()
            self._device.shutdown()
            self._device = None
            self._rssi_timer.stop()
            self.__not_connected_status()

    def shutdown(self):
        self.__disconnect_device()
        super().shutdown()
