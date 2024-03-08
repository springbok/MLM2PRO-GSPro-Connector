import os
import subprocess
from PySide6.QtCore import QThread, QCoreApplication, Signal, QObject
from PySide6.QtWidgets import QMessageBox
from src import MainWindow
from src.ctype_screenshot import ScreenMirrorWindow
from src.gspro_connect import GSProConnect
from src.gspro_messages_worker import GSProMessagesWorker
from src.gspro_start_worker import GSProStartWorker
from src.gspro_worker import GsproWorker
from src.log_message import LogMessageSystems, LogMessageTypes
from src.worker_thread import WorkerThread


class GSProConnection(QObject):

    connected_to_gspro = Signal()
    disconnected_from_gspro = Signal()
    shot_sent = Signal(object)
    gspro_app_not_found = Signal()
    club_selected = Signal(object)
    club_selection_error = Signal()

    def __init__(self, main_window: MainWindow):
        super(GSProConnection, self).__init__()
        self.main_window = main_window
        self.worker = None
        self.thread = None
        self.gspro_messages_thread = None
        self.gspro_messages_worker = None
        self.send_shot_thread = None
        self.send_shot_worker = None
        self.gspro_start_worker = None
        self.gspro_start_thread = None
        self.connected = None
        self.settings = main_window.settings
        self.gspro_connect = GSProConnect(
            self.settings.device_id,
            self.settings.units,
            self.settings.api_version
        )
        self.main_window.gspro_status_label.setText('Not Connected')
        self.main_window.gspro_status_label.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.__setup_send_shot_thread()
        self.__setup_gspro_messages_thread()

    def __setup_send_shot_thread(self):
        self.send_shot_thread = QThread()
        self.send_shot_worker = GsproWorker(self.gspro_connect)
        self.send_shot_worker.moveToThread(self.send_shot_thread)
        self.send_shot_worker.started.connect(self.__sending_shot)
        self.send_shot_worker.sent.connect(self.__sent)
        self.send_shot_worker.error.connect(self.__send_shot_error)
        self.send_shot_thread.started.connect(self.send_shot_worker.run)
        self.send_shot_thread.start()

    def __setup_gspro_messages_thread(self):
        self.gspro_messages_thread = QThread()
        self.gspro_messages_worker = GSProMessagesWorker(self.gspro_connect)
        self.gspro_messages_worker.moveToThread(self.gspro_messages_thread)
        self.gspro_messages_worker.club_selected.connect(self.__club_selected)
        self.gspro_messages_worker.error.connect(self.__gspro_messages_error)
        self.gspro_messages_thread.started.connect(self.gspro_messages_worker.run)
        self.gspro_messages_thread.start()

    def __setup_connection_thread(self):
        self.thread = QThread()
        self.worker = WorkerThread(
            self.gspro_connect.init_socket,
        self.settings.ip_address,
            self.settings.port)
        self.worker.moveToThread(self.thread)
        self.worker.started.connect(self.__in_progress)
        self.worker.result.connect(self.__connected)
        self.worker.error.connect(self.__error)
        # self.worker.finished.connect(self.__finished)
        self.thread.started.connect(self.worker.run())
        self.thread.start()

    def __club_selecion_error(self, error):
        self.club_selection_error.emit()
        self.disconnect_from_gspro()
        msg = f"Error while trying to check for club selection messages from GSPro.\nMake sure GSPro API Connect is running.\nStart/restart API Connect from GSPro.\nPress 'Connect' to reconnect to GSPro."
        self.__log_message(LogMessageTypes.LOGS, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "GSPro Receive Error", msg)

    def __club_selected(self, club_data):
        self.club_selected.emit(club_data)

    def __send_shot_error(self, error):
        self.disconnect_from_gspro()
        msg = f"Error while trying to send shot to GSPro.\nMake sure GSPro API Connect is running.\nStart/restart API Connect from GSPro.\nPress 'Connect' to reconnect to GSPro."
        self.__log_message(LogMessageTypes.LOGS, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "GSPro Send Error", msg)

    def __gspro_messages_error(self, error):
        self.disconnect_from_gspro()
        msg = f"Error while trying to check for new messages from GSPro.\nStart/restart API Connect from GSPro.\nPress 'Connect' to reconnect to GSPro."
        self.__log_message(LogMessageTypes.LOGS, f'{msg}\nException: {format(error)}')
        QMessageBox.warning(self.main_window, "GSPro Message Receive Error", msg)

    def connect_to_gspro(self):
        if not self.connected:
            if self.__find_gspro_api_app():
                if self.thread is None:
                    self.__setup_connection_thread()
                if self.gspro_messages_thread is None:
                    self.__setup_gspro_messages_thread()
                if self.send_shot_thread is None:
                    self.__setup_send_shot_thread()

    def disconnect_from_gspro(self):
        if self.connected:
            self.main_window.gspro_connect_button.setEnabled(False)
            self.__shutdown_threads()
            self.gspro_connect.terminate_session()
            self.connected = False
            self.disconnected_from_gspro.emit()

    def __sent(self, balldata):
        self.shot_sent.emit(balldata)

    def __sending_shot(self):
        self.__log_message(LogMessageTypes.ALL, 'Sending shot to GSPro')

    def __in_progress(self):
        msg = 'Connecting...'
        self.__log_message(LogMessageTypes.ALL, f'Connecting to GSPro...')
        self.__log_message(LogMessageTypes.LOGS, f'Connection settings: {self.settings.to_json(True)}')
        self.main_window.gspro_status_label.setText(msg)
        self.main_window.gspro_status_label.setStyleSheet("QLabel { background-color : orange; color : white; }")
        self.main_window.gspro_connect_button.setEnabled(False)
        QCoreApplication.processEvents()

    def __connected(self):
        self.connected = True
        self.connected_to_gspro.emit()

    def __error(self, error):
        self.disconnect_from_gspro()
        msg = "Error while trying to connect to GSPro.\nMake sure GSPro API Connect is running.\nStart/restart API Connect from GSPro.\nPress 'Connect' to reconnect to GSPro."
        self.__log_message(LogMessageTypes.LOGS, f'{msg} Exception: {format(error)}')
        QMessageBox.warning(self.main_window, "GSPro Connect Error", msg)

    def shutdown(self):
        self.gspro_connect.terminate_session()
        self.connected = False
        self.__shutdown_threads()

    def __log_message(self, types, message):
        self.main_window.log_message(types, LogMessageSystems.GSPRO_CONNECT, message)

    def __find_gspro_api_app(self):
        running = False
        try:
            if self.settings.local_gspro():
                ScreenMirrorWindow.find_window(self.settings.gspro_api_window_name)
            running = True
        except Exception:
            self.gspro_app_not_found.emit()
            running = False
        return running

    def gspro_start(self, settings, auto_start):
        # Start GSPro if not running
        if len(settings.gspro_path) > 0 and len(settings.grspo_window_name) and os.path.exists(settings.gspro_path):
            gspro_running = False
            try:
                ScreenMirrorWindow.find_window(settings.grspo_window_name)
                gspro_running = True
                if auto_start:
                    ScreenMirrorWindow.find_window(settings.gspro_api_window_name)
                    self.connect_to_gspro()
            except Exception:
                self.main_window.log_message(LogMessageTypes.ALL, LogMessageSystems.CONNECTOR, f"GSPro not running, starting")
                try:
                    if not gspro_running:
                        subprocess.Popen(settings.gspro_path)
                    if auto_start:
                        self.gspro_start_thread = QThread()
                        self.gspro_start_worker = GSProStartWorker(settings)
                        self.gspro_start_worker.moveToThread(self.gspro_start_thread)
                        self.gspro_start_worker.error.connect(self.__gspro_start_error)
                        self.gspro_start_thread.started.connect(self.gspro_start_worker.run)
                        self.gspro_start_worker.gspro_started.connect(self.connect_to_gspro)
                        self.gspro_start_thread.start()
                except Exception as e:
                    self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, "Could not start GSPro at {path}.\nException: {format(e)}")

    def __gspro_start_error(self, error):
        msg = "Unable to automatically start GSPro."
        self.__log_message(LogMessageTypes.LOGS, f'{msg} Exception: {format(error)}')
        QMessageBox.warning(self.main_window, "GSPro Start Error", msg)

    def __shutdown_threads(self):
        if self.gspro_messages_thread is not None:
            self.gspro_messages_thread.quit()
            self.gspro_messages_thread.wait()
            self.gspro_messages_thread = None
            self.gspro_messages_worker = None
        if self.send_shot_thread is not None:
            self.send_shot_thread.quit()
            self.send_shot_thread.wait()
            self.send_shot_thread = None
            self.send_shot_worker = None
        if self.gspro_start_thread is not None:
            self.gspro_start_worker.shutdown()
            self.gspro_start_thread.quit()
            self.gspro_start_thread.wait()
            self.gspro_start_thread = None
            self.gspro_start_worker = None
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
            self.worker = None
