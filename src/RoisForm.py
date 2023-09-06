from functools import partial
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox
from src.RoisForm_ui import Ui_RoisForm
from src.VerifyRoiForm import VerifyRoiForm
from src.log_message import LogMessageTypes, LogMessageSystems
from src.screenshot import Screenshot
from src.worker_thread import WorkerThread


class RoisForm(QMainWindow, Ui_RoisForm):

    closed = Signal()

    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.roi_image = Screenshot()
        self.thread = QThread()
        self.verify_roi = VerifyRoiForm()
        self.device = None
        self.current_button = None
        self.setupUi(self)
        self.__setupUi()

    def __setupUi(self):
        self.roi_graphics_layout.addItem(self.roi_image)
        self.close_button.clicked.connect(self.__close)
        self.save_button.clicked.connect(self.__save)
        self.reset_button.clicked.connect(self.__reset)
        self.verify_button.clicked.connect(self.__verify)
        self.zoomin_button.clicked.connect(partial(self.__zoom,in_or_out='in'))
        self.zoomout_button.clicked.connect(partial(self.__zoom,in_or_out='out'))

    def showEvent(self, event: QShowEvent) -> None:
        if len(self.device.rois) <= 0:
            QMessageBox.information(self, "Resize Window",
                                f"Before you continue:\nTake a shot.\nMirror your device screen.\nResize the window to remove any black borders.")
        else:
            QMessageBox.information(self, "Setup Screen Mirror",
                                f"Before you continue:\nTake a shot.\nMirror your device screen.")
        # Reset current device so setting are reloaded
        self.roi_image.device = None
        # Reload settings to ensure we are using the latest
        self.device.load()
        # Force a window resize
        self.roi_image.resize_window = True
        self.__get_screenshot()

    def __close(self):
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def __reset(self):
        button = QMessageBox.question(self, "Are you sure?", "This will clear the settings for this device including; mirror app window size and all associated RIO's. If you want to record new settings:\nAdjust your mirror app window to the desired size.\nSelect new ROI's.")
        if button == QMessageBox.Yes:
            self.device.window_rect = {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}
            self.device.rois = {}
            self.roi_image.resize_window = True
            self.__get_screenshot()

    def __save(self):
        if not self.device is None:
            self.device.rois = self.roi_image.get_rois()
            self.device.save()
            QMessageBox.information(self, "Device Updated", f"Device {self.device.name} RIO's updated.")

    def __zoom(self, in_or_out):
        self.roi_image.zoom(in_or_out)

    def __verify(self):
        self.roi_image.ocr_image()
        self.verify_roi.balldata = self.roi_image.balldata
        self.verify_roi.show()

    def __get_screenshot(self):
        if not self.device:
            raise RuntimeError('No device specified unable to capture screenshot')
        self.worker = WorkerThread(self.roi_image.capture_screenshot, self.device, True)
        self.worker.moveToThread(self.thread)
        self.worker.started.connect(self.__in_progress)
        self.worker.error.connect(self.__error)
        self.thread.started.connect(self.worker.run())
        self.thread.start()

    def __in_progress(self):
        self.__log_message(LogMessageTypes.STATUS_BAR, f'Taking screenshot...')

    def __error(self, error):
        msg = f"Error while trying to take a screenshot: {error}"
        self.__log_message(LogMessageTypes.LOGS, msg)
        QMessageBox.critical(self.main_window, "Screenshot Error", msg)

    def __log_message(self, types, message):
        self.main_window.log_message(types, LogMessageSystems.CONNECTOR, message)

    def shutdown(self):
        self.thread.quit()
        self.thread.wait()
