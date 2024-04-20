from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMessageBox, QMainWindow

from src.RoisFormBase import RoisFormBase
from src.screenshot_exputt import ScreenshotExPutt
from src.worker_thread import WorkerThread

class RoisExPuttForm(RoisFormBase):

    def __init__(self, main_window):
        self.roi_image = ScreenshotExPutt(main_window.putting_settings)
        self.settings = main_window.putting_settings
        super(RoisExPuttForm, self).__init__(main_window)
        self.setup_ui()

    def showEvent(self, event: QShowEvent) -> None:
        # Reload settings to ensure we are using the latest
        self.settings.load()
        if len(self.settings.exputt['rois']) <= 0:
            QMessageBox.information(self, "Resize Window",
                                f"Before you continue:\nTake a shot.\nOpen the Windows Camera App.\nResize the window to desired size.")
        else:
            QMessageBox.information(self, "Windows Camera App",
                                f"Before you continue:\nTake a shot.\nOpen Windows Camera App")
        # Force a window resize
        self.roi_image.resize_window = True
        self.__get_screenshot()

    def reset(self):
        button = QMessageBox.question(self, "Are you sure?", "This will clear all ExPutt ROI's. If you want to record new settings:\nAdjust your Windows Camera App to the desired size.\nSelect new ROI's.")
        if button == QMessageBox.Yes:
            self.settings.exputt['window_rect'] = {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}
            self.settings.exputt['rois'] = {}
            self.roi_image.resize_window = True
            self.__get_screenshot()

    def save(self):
        self.settings.exputt['rois'] = self.roi_image.get_rois()
        self.settings.save()
        QMessageBox.information(self, "Settings Updated", f"RIO's have been updated.")


    def __get_screenshot(self):
        self.worker = WorkerThread(self.roi_image.capture_screenshot, self.settings, True)
        self.worker.moveToThread(self.thread)
        self.worker.started.connect(super().in_progress)
        self.worker.error.connect(super().error)
        self.thread.started.connect(self.worker.run())
        self.thread.start()
