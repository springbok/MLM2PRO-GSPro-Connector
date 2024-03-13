from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMessageBox, QMainWindow
from src.RoisFormBase import RoisFormBase
from src.screenshot import Screenshot
from src.worker_thread import WorkerThread


class RoisForm(RoisFormBase):

    def __init__(self, main_window):
        self.roi_image = Screenshot(main_window.settings)
        super(RoisForm, self).__init__(main_window)
        self.setup_ui()

    def showEvent(self, event: QShowEvent) -> None:
        # Reload settings to ensure we are using the latest
        self.device.load()
        if len(self.device.rois) <= 0:
            QMessageBox.information(self, "Resize Window",
                                f"Before you continue:\nTake a shot.\nMirror your device screen.\nResize the window to remove any black borders.")
        else:
            QMessageBox.information(self, "Setup Screen Mirror",
                                f"Before you continue:\nTake a shot.\nMirror your device screen.")
        # Reset current device so setting are reloaded
        self.roi_image.device = None
        # Force a window resize
        self.roi_image.resize_window = True
        self.__get_screenshot()

    def reset(self):
        button = QMessageBox.question(self, "Are you sure?", "This will clear the settings for this device including; mirror app window size and all associated RIO's. If you want to record new settings:\nAdjust your mirror app window to the desired size.\nSelect new ROI's.")
        if button == QMessageBox.Yes:
            self.device.window_rect = {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}
            self.device.rois = {}
            self.roi_image.resize_window = True
            self.__get_screenshot()

    def save(self):
        if not self.device is None:
            self.device.rois = self.roi_image.get_rois()
            self.device.save()
            self.saved.emit()
            QMessageBox.information(self, "Device Updated", f"Device {self.device.name} RIO's updated.")

    def __get_screenshot(self):
        if not self.device:
            raise RuntimeError('No device specified unable to capture screenshot')
        self.worker = WorkerThread(self.roi_image.capture_screenshot, self.device, True)
        self.worker.moveToThread(self.thread)
        self.worker.started.connect(super().in_progress)
        self.worker.error.connect(super().error)
        self.thread.started.connect(self.worker.run())
        self.thread.start()
