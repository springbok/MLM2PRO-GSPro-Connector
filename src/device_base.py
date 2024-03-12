from PySide6.QtCore import QObject, QThread
from PySide6.QtWidgets import QMessageBox

from src import MainWindow
from src.log_message import LogMessageTypes, LogMessageSystems


class DeviceBase(QObject):

    def __init__(self, main_window: MainWindow):
        super(QObject, self).__init__()
        self.device_thread = None
        self.device_worker = None
        self.main_window = main_window

    def resume(self):
        self.running = True
        if self.device_worker is not None and self.running and self.main_window.gspro_connection.connected:
            self.device_worker.resume()

    def pause(self):
        if self.device_worker is not None:
            self.device_worker.pause()

    def shutdown(self):
        if self.device_worker is not None and self.device_thread is not None:
            self.device_worker.shutdown()
            self.device_thread.quit()
            self.device_thread.wait()
            self.device_thread = None
            self.device_worker = None

    def setup_device_thread(self):
        self.device_thread = QThread()
        self.device_worker.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_worker.run)
        self.device_worker.error.connect(self.device_worker_error)
        self.device_worker.paused.connect(self.device_worker_paused)
        self.device_worker.resumed.connect(self.device_worker_resumed)
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

    def is_paused(self):
        return (self.device_worker is not None and self.device_worker.is_paused())

    def is_running(self):
        return (self.device_worker is not None and self.device_worker.is_running())

    def start(self):
        if self.device_worker is not None and not self.is_running():
            self.device_worker.start()

    def stop(self):
        if self.device_worker is not None and self.is_running():
            self.device_worker.stop()