from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMessageBox
from src.custom_exception import CameraWindowNotFoundException
from src.log_message import LogMessageTypes, LogMessageSystems
from src.screenshot_worker_exputt import ScreenshotWorkerExPutt
from src import MainWindow


class PuttingExPutt:

    def __init__(self, main_window: MainWindow):
        self.screenshot_thread = None
        self.screenshot_worker = None
        self.main_window = main_window
        self.setup()

    def setup(self):
        self.screenshot_worker = ScreenshotWorkerExPutt(self.main_window.settings, self.main_window.putting_settings)
        self.__setup_screenshot_thread()

    def __setup_screenshot_thread(self):
        self.screenshot_thread = QThread()
        self.screenshot_worker.moveToThread(self.screenshot_thread)
        self.screenshot_thread.started.connect(self.screenshot_worker.run)
        self.screenshot_worker.shot.connect(self.main_window.gspro_connection.send_shot_worker.run)
        self.screenshot_worker.bad_shot.connect(self.main_window.bad_shot)
        self.screenshot_worker.same_shot.connect(self.main_window.gspro_connection.club_selecion_worker.run)
        self.screenshot_worker.bad_shot.connect(self.main_window.gspro_connection.club_selecion_worker.run)
        self.screenshot_worker.too_many_ghost_shots.connect(self.__too_many_ghost_shots)
        self.screenshot_worker.error.connect(self.__screenshot_worker_error)
        self.screenshot_worker.paused.connect(self.__screenshot_worker_paused)
        self.screenshot_worker.resumed.connect(self.__screenshot_worker_resumed)
        self.screenshot_thread.start()
        self.__screenshot_worker_paused()

    def __too_many_ghost_shots(self):
        self.screenshot_worker.pause()
        QMessageBox.warning(self.main_window, "Ghost Shots Detected",
                            "Too many shots were received within a short space of time.")

    def __screenshot_worker_error(self, error):
        msg = ''
        if isinstance(error[0], CameraWindowNotFoundException):
            msg = f"Windows Camera application ' {self.main_window.putting_settings.exputt['window_name']}' does not seem to be running.\nPlease start the app, then press the 'Start' button to restart the putting."
            if self.screenshot_worker.get_putting_active():
                self.__putting_stop_start()
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
            self.__screenshot_worker_paused()
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        QMessageBox.warning(self.main_window, "Connector Error", msg)

    def __screenshot_worker_paused(self):
        self.main_window.connector_status.setText('Not Ready')
        self.main_window.connector_status.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.main_window.restart_button.setEnabled(True)
        self.main_window.pause_button.setEnabled(False)

    def __screenshot_worker_resumed(self):
        self.screenshot_worker.ignore_shots_after_restart()
        self.main_window.connector_status.setText('Ready')
        self.main_window.connector_status.setStyleSheet("QLabel { background-color : green; color : white; }")
        self.main_window.restart_button.setEnabled(False)
        self.main_window.pause_button.setEnabled(True)

    def shutdown(self):
        self.screenshot_worker.shutdown()
        self.screenshot_thread.quit()
        self.screenshot_thread.wait()

    def __putting_stop_start(self):
        running = False
        self.screenshot_worker.set_putting_active(False)
            running = True
        logging.debug(f'putting running: {running} self.current_putting_system: {self.current_putting_system} self.screenshot_worker.get_putting_active(): {self.screenshot_worker.get_putting_active()}')
        if not running:
            self.__setup_putting()


def __setup_putting(self):
    self.__display_putting_system()
    if self.putting_settings.system == PuttingSystems.WEBCAM:
        self.putting_server_button.setEnabled(True)
        self.webcam_putting = PuttingWebcam(self.putting_settings)
        self.webcam_putting.started.connect(self.__putting_started)
        self.webcam_putting.stopped.connect(self.__putting_stopped)
        self.webcam_putting.error.connect(self.__putting_error)
        self.webcam_putting.putt_shot.connect(self.gspro_connection.send_shot_worker.run)
        if self.putting_settings.webcam['auto_start'] == 'Yes':
            self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR, f'Starting webcam putting')
            self.webcam_putting.start_server()
            if not self.webcam_putting.http_server_worker is None and self.putter_selected:
                self.webcam_putting.http_server_worker.select_putter(self.putter_selected)
    elif self.putting_settings.system == PuttingSystems.EXPUTT:
        self.screenshot_worker.set_putting_active(True)
        self.screenshot_worker.putting_settings = self.putting_settings
        if self.putting_settings.exputt['auto_start'] == 'Yes':
            try:
                self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR,
                                 f'Starting ExPutt')
                ScreenMirrorWindow.find_window(self.putting_settings.exputt['window_name'])
            except:
                subprocess.run('start microsoft.windows.camera:', shell=True)
    self.current_putting_system = self.putting_settings.system
    QCoreApplication.processEvents()


    def __display_putting_system(self):
        self.putting_system_label.setText(self.putting_settings.system)
        if self.putting_settings.system == PuttingSystems.NONE:
            color = 'orange'
        elif self.putting_settings.system == PuttingSystems.WEBCAM or self.putting_settings.system == PuttingSystems.EXPUTT:
            color = 'green'
        self.putting_system_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
        QCoreApplication.processEvents()
