import asyncio
from PySide6.QtWidgets import QMessageBox
from src.worker_device_launch_monitor_bluetooth_mlm import WorkerDeviceLaunchMonitorBluetoothMLM


class DeviceLaunchMonitorBluetoothMLM2PRO:

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
        #self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        #self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        #self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        #self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def __not_connected_status(self):
        self.__update_ui('Not Connected', 'red', 'No Device', 'red', 'Start', 'green', True)

    def __scanning(self, message):
        self.__update_ui(message, 'orange', 'No Device', 'red', 'Stop', False)

    def __device_found(self, device):
        self.__update_ui('Not Connected', 'red', device, 'green', 'Stop', False)

    def __no_device_found(self, message):
        self.__not_connected_status()
        QMessageBox.warning(self.main_window, "No Device Found", 'No device found. Please ensure your launch monitor is turned on and a STREADY RED light is showing.')

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
