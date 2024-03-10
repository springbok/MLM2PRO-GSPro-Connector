from PySide6.QtCore import QObject, QThread
from PySide6.QtWidgets import QMessageBox

from src import MainWindow
from src.log_message import LogMessageTypes, LogMessageSystems


class DeviceBase(QObject):

    def __init__(self, main_window: MainWindow):
        super(QObject, self).__init__()
        self.device_thread = None
        self.device_worker = None
        self.running = False
        self.main_window = main_window

    def resume(self):
        print('DeviceBase resume')
        if self.device_worker is not None and self.running and self.main_window.gspro_connection.connected:
            self.device_worker.resume()

    def pause(self):
        if self.device_worker is not None:
            self.device_worker.pause()

    def shutdown(self):
        print(f'DeviceBase shutdown {self.__class__.__name__}')
        if self.device_worker is not None and self.device_thread is not None:
            print('DeviceBase shutdown 2')
            self.device_worker.shutdown()
            self.device_thread.quit()
            self.device_thread.wait()

    def setup_device_thread(self):
        self.device_thread = QThread()
        self.device_worker.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_worker.run)
        self.device_worker.error.connect(self.device_worker_error)
        self.device_worker.paused.connect(self.device_worker_paused)
        self.device_worker.resumed.connect(self.device_worker_resumed)
        self.device_worker.started.connect(self.__server_started)
        self.device_worker.finished.connect(self.__server_stopped)
        self.device_thread.start()

    def device_worker_error(self, error):
        msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
        self.main_window.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        QMessageBox.warning(self.main_window, "Connector Error", msg)

    def device_worker_paused(self):
        return

    def device_worker_resumed(self):
        return

    def reload_putting_rois(self):
        pass

    def paused(self):
        return (self.device_worker is not None and self.device_worker.paused())

    def __server_started(self):
        self.running = True

    def __server_stopped(self):
        self.running = False