import json
import logging
import os
import subprocess

from PySide6.QtWidgets import QMessageBox
from src.ball_data import BallData
from src.ctype_screenshot import ScreenMirrorWindow
from src.device_base import DeviceBase
from src.log_message import LogMessageTypes, LogMessageSystems
from src.worker_device_launch_monitor_relay_server import WorkerDeviceLaunchMonitorRelayServer


class DeviceLaunchMonitorRelayServerBase(DeviceBase):

    def __init__(self, main_window):
        DeviceBase.__init__(self, main_window)
        self.launch_monitor_app = None
        self.__setup_signals()
        self.device_worker_paused()
        self.prev_shot = None

    def setup_device_thread(self):
        super().setup_device_thread()
        self.device_worker.listening.connect(self.__listening)
        self.device_worker.connected.connect(self.__connected)
        self.device_worker.finished.connect(self.device_worker_paused)
        self.device_worker.relay_server_shot.connect(self.__shot_sent)

    def __setup_signals(self):
        self.main_window.start_server_button.clicked.connect(self.__server_start_stop)
        self.main_window.gspro_connection.club_selected.connect(self.__club_selected)
        self.main_window.gspro_connection.disconnected_from_gspro.connect(self.pause)
        self.main_window.gspro_connection.connected_to_gspro.connect(self.resume)
        self.main_window.gspro_connection.gspro_message.connect(self.__gspro_message)

    def __shot_sent(self, shot_data):
        data = json.loads(shot_data.decode("utf-8"))
        balldata = BallData()
        balldata.from_gspro(data)
        balldata.good_shot = True
        if self.prev_shot is None or self.prev_shot.eq(balldata) > 0:
            self.main_window.shot_sent(balldata)
            self.prev_shot = balldata

    def __gspro_message(self, message):
        self.device_worker.send_msg(message)

    def __server_start_stop(self):
        if self.device_worker is None:
            self.device_worker = WorkerDeviceLaunchMonitorRelayServer(self.main_window.settings, self.main_window.gspro_connection.gspro_connect)
            self.setup_device_thread()
            self.device_worker.start()
            self.device_worker.club_selected(self.main_window.gspro_connection.current_club)
            self.start_app()
        else:
            self.device_worker.stop()
            self.shutdown()
            self.device_worker_paused()

    def start_app(self):
        if not self.__find_connector_app():
            print(f'app not found {self.launch_monitor_app}')
            try:
                path = f"{os.getcwd()}{self.launch_monitor_app}"
                logging.debug(f'Starting connector app: {path}')
                print(f'starting {path}')
                subprocess.Popen(path, cwd=os.path.dirname(path))
            except Exception as e:
                logging.debug(f'Could not start LM connector app: {self.launch_monitor_app} error: {format(e)}')

    def __find_connector_app(self):
        try:
            ScreenMirrorWindow.find_window(self.main_window.settings.relay_server_window_name)
            running = True
        except Exception:
            running = False
        return running

    def device_worker_error(self, error):
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.R10, f'Error: {format(error)}')
        QMessageBox.warning(self.main_window, "R10 Error", f'{format(error)}')
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

    def device_worker_paused(self):
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
