import logging
from PySide6.QtCore import QThread, QCoreApplication, Signal, QObject
from PySide6.QtWidgets import QMessageBox
from src import MainWindow
from src.ctype_screenshot import ScreenMirrorWindow
from src.gspro_connect import GSProConnect
from src.gspro_worker import GsproWorker
from src.log_message import LogMessageSystems, LogMessageTypes
from src.settings import Settings
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
        self.thread = QThread()
        self.connected = None
        self.settings = main_window.settings
        self.gspro_connect = GSProConnect(
            self.settings.device_id,
            self.settings.units,
            self.settings.api_version
        )
        self.gspro_connect.club_selected.connect(self.__club_selected)
        self.main_window.gspro_status_label.setText('Not Connected')
        self.main_window.gspro_status_label.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.__setup_send_shot_thread()
        self.__setup_club_selection_thread()

    def __setup_send_shot_thread(self):
        self.send_shot_thread = QThread()
        self.send_shot_worker = GsproWorker(
            self.gspro_connect.launch_ball)
        self.send_shot_worker.moveToThread(self.send_shot_thread)
        self.send_shot_worker.started.connect(self.__sending_shot)
        self.send_shot_worker.sent.connect(self.__sent)
        self.send_shot_worker.error.connect(self.__send_shot_error)
        self.send_shot_thread.started.connect(self.send_shot_worker.run)
        self.send_shot_thread.start()

    def __setup_club_selection_thread(self):
        logging.debug('__setup_club_selection_thread start')
        self.club_selecion_thread = QThread()
        self.club_selecion_worker = WorkerThread(
            self.gspro_connect.check_for_message)
        self.club_selecion_worker.moveToThread(self.club_selecion_thread)
        self.club_selecion_worker.error.connect(self.__club_selecion_error)
        self.club_selecion_thread.start()

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

    def connect_to_gspro(self):
        if not self.connected:
            if self.__find_gspro_api_app():
                self.worker = WorkerThread(
                self.gspro_connect.init_socket,
                self.settings.ip_address,
                self.settings.port)
                self.worker.moveToThread(self.thread)
                self.worker.started.connect(self.__in_progress)
                self.worker.result.connect(self.__connected)
                self.worker.error.connect(self.__error)
                #self.worker.finished.connect(self.__finished)
                self.thread.started.connect(self.worker.run())
                self.thread.start()

    def disconnect_from_gspro(self):
        if self.connected:
            self.main_window.gspro_connect_button.setEnabled(False)
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
        self.thread.quit()
        self.thread.wait()
        self.send_shot_thread.quit()
        self.send_shot_thread.wait()
        self.club_selecion_thread.quit()
        self.club_selecion_thread.wait()


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

