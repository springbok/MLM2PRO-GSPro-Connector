import asyncio
from PySide6.QtWidgets import QMessageBox

from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_device_launch_monitor_bluetooth_mlm import WorkerDeviceLaunchMonitorBluetoothMLM


class DeviceLaunchMonitorBluetoothMLM2PRO1:

    def __init__(self, main_window):
        self.main_window = main_window
        self.device_worker = WorkerDeviceLaunchMonitorBluetoothMLM()
        self.__not_connected_status()
        self.__setup_signals()

    def __setup_signals(self):
        self.main_window.start_server_button.clicked.connect(self.__server_start_stop)
        self.device_worker.no_device_found.connect(self.__no_device_found)
        self.device_worker.scanning.connect(self.__scanning)
        self.device_worker.device_found.connect(self.__device_found)
        self.device_worker.connecting.connect(self.__connecting)
        self.device_worker.connected.connect(self.__connected)
        self.device_worker.disconnected.connect(self.__disconnected)
        self.device_worker.disconnecting.connect(self.__disconnecting)
        self.device_worker.error.connect(self.__device_worker_error)
        #self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        #self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        #self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        #self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def __not_connected_status(self):
        print('__not_connected_status')
        self.__update_ui('Not Connected', 'red', 'No Device', 'red', 'Start', 'green', True)

    def __scanning(self, message):
        print('__scanning')
        self.__update_ui(message, 'orange', 'No Device', 'red', 'Stop', False)

    def __device_found(self, device):
        print('__device_found')
        self.__update_ui('Not Connected', 'red', device, 'green', 'Stop', False)

    def __no_device_found(self, message):
        print('__no_device_found')
        self.__not_connected_status()
        QMessageBox.warning(self.main_window, "No Device Found", 'No device found. Please ensure your launch monitor is turned on and a STREADY RED light is showing.')

    def __connecting(self, device):
        print('__connecting')
        self.__update_ui('Connecting...', 'orange', device, 'green', 'Stop', False)

    def __disconnecting(self, device):
        print('__disconnecting')
        self.__update_ui('Disconnecting...', 'orange', device, 'green', 'Stop', False)

    def __connected(self, device):
        print('__connected')
        self.__update_ui('Connected', 'green', device, 'green', 'Stop', True)

    def __disconnected(self, device):
        print('__disconnected')
        self.__not_connected_status()

    def __device_worker_error(self, error):
        msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        QMessageBox.warning(self.main_window, "Connector Error", msg)

    def device_worker_paused(self):
        status = 'Not Connected'
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

    def __server_start_stop(self):
        if not self.device_worker.running:
            QMessageBox.warning(self.main_window, "Starting LM connector", 'Before starting Bluetooth connection ensure your launch monitor is turned on and a STREADY RED light is showing.')
            asyncio.ensure_future(self.device_worker.start_bluetooth())
            print('xxx asyncio process done')
        else:
            print('stop')
            self.__not_connected_status()
            self.device_worker.shutdown()
            #self.shutdown()

    def shutdown(self):
        if self.device_worker is not None:
            self.device_worker_paused()
            asyncio.ensure_future(self.device_worker.stop_bluetooth())
            self.device_worker = None

    def is_running(self):
        return (self.device_worker is not None and self.device_worker.is_running())

    def ignore_shots_after_restart(self):
        pass

    def __update_ui(self, message, color, status, status_color, button, button_color, enabled=True):
        self.main_window.server_connection_label.setText(status)
        self.main_window.server_connection_label.setStyleSheet(f"QLabel {{ background-color : {status_color}; color : white; }}")
        self.main_window.start_server_button.setText(button)
        self.main_window.start_server_button.setEnabled(enabled)
        self.main_window.server_status_label.setText(message)
        self.main_window.server_status_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
