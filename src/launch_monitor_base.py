from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMessageBox

from src.DevicesForm import DevicesForm
from src.SelectDeviceForm import SelectDeviceForm
from src.custom_exception import WindowNotFoundException
from src.log_message import LogMessageTypes, LogMessageSystems
from src.screenshot_worker_launch_monitor import ScreenshotWorkerLaunchMonitor
from src import MainWindow


class LaunchMonitorBase:

    def __init__(self, main_window: MainWindow):
        self.launch_monitor_thread = None
        self.current_device = None
        self.launch_monitor_worker = None
        self.main_window = main_window

    def setup(self):
        return

    def resume(self):
        if self.launch_monitor_worker is not None:
            self.launch_monitor_worker.resume()

    def pause(self):
        if self.launch_monitor_worker is not None:
            self.launch_monitor_worker.pause()

    def shutdown(self):
        if self.launch_monitor_worker is not None and self.launch_monitor_thread is not None:
            self.launch_monitor_worker.shutdown()
            self.launch_monitor_thread.quit()
            self.launch_monitor_thread.wait()
