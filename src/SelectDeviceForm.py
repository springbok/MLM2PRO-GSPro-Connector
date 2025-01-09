import os
from threading import Event
import PySide6
from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QMainWindow
from src.RoisForm import RoisForm
from src.SelectDeviceForm_ui import Ui_SelectDeviceForm
from src.ctype_screenshot import ScreenMirrorWindow
from src.device import Device
from src.devices import Devices
from src.log_message import LogMessageSystems, LogMessageTypes


class SelectDeviceForm(QWidget, Ui_SelectDeviceForm):
    name_col = 0
    selected = Signal(object or None)
    cancel = Signal()

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.app_paths = main_window.app_paths
        self.devices = Devices(self.app_paths)
        self.rois_form = RoisForm(main_window=self.main_window)
        self.close_button.clicked.connect(self.__close)
        self.select_button.clicked.connect(self.select_device)
        self.roi_button.clicked.connect(self.__rois)
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        self.devices_table.setHorizontalHeaderLabels(['Device Name'])
        self.devices_table.selectionModel().selectionChanged.connect(self.__selection_changed)
        self.rois_form.closed.connect(self.__rois_form_closed)
        self.current_device = None


    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        self.devices.load_devices()
        # Load data into the table
        self.__load_device_table()
        self.devices_table.selectRow(0)

    def __close(self):
        self.cancel.emit()
        self.close()

    def __rois(self):
        self.rois_form.device = self.devices.devices[self.devices_table.currentRow()]
        if self.__screen_mirror_app_running(self.rois_form.device):
            self.rois_form.show()

    def __rois_form_closed(self):
            item = self.devices_table.item(self.devices_table.currentRow(), SelectDeviceForm.name_col)
            if len(self.rois_form.device.rois) > 0:
                self.select_button.setDisabled(False)
                item.setBackground(QtGui.QColor("white"))
            else:
                item.setBackground(QtGui.QColor("#ff3800"))
                self.select_button.setDisabled(True)

    def __selection_changed(self, selected, deselected):
        device = self.devices.devices[self.devices_table.currentRow()]
        if len(device.rois) <= 0:
            self.select_button.setDisabled(True)
        else:
            self.select_button.setDisabled(False)

    def select_device(self, device=None):
        if device is None or not device:
            self.current_device = self.devices.devices[self.devices_table.currentRow()]
        else:
            self.current_device = device
        if self.__screen_mirror_app_running(self.current_device):
            self.selected.emit(self.current_device)
            self.__close()

    def __load_device_table(self):
        self.devices_table.setRowCount(0)
        for device in self.devices.devices:
            device.load()
            self.__add_row(device)

    def __add_row(self, device: Device):
        row = self.devices_table.rowCount()
        self.devices_table.insertRow(row)
        item = QTableWidgetItem(device.name)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.devices_table.setItem(row, SelectDeviceForm.name_col, item)
        if len(device.rois) <= 0:
            item.setBackground(QtGui.QColor("#ff3800"))

    def __log_message(self, types, message):
        self.main_window.log_message(types, LogMessageSystems.CONNECTOR, message)

    def __find_screen_mirror_app(self, device):
        running = False
        try:
            ScreenMirrorWindow.find_window(device.window_name)
            running = True
        except Exception:
            running = False
        return running

    def __screen_mirror_app_running(self, device):
        running = False
        if len(device.window_path) > 0 and len(device.window_name) > 0 and os.path.exists(device.window_path):
            if not self.__find_screen_mirror_app(device):
                self.__log_message(LogMessageTypes.ALL, f"{device.window_name} not running, starting")
                try:
                    os.startfile(device.window_path)
                    Event().wait(3)
                    if not self.__find_screen_mirror_app(device):
                        # Wait another 15 seconds if app still not running
                        Event().wait(15)
                except Exception as e:
                    self.__log_message(LogMessageTypes.LOG_FILE, f"Could not start app at {device.window_path} exception: {format(e)}")
        if not self.__find_screen_mirror_app(device):
            msg = f"Screen capture application ' {device.window_name}' does not seem to be running, please start the app and retry."
            self.__log_message(LogMessageTypes.LOG_FILE, msg)
            QMessageBox.warning(self, "Screen Mirror App Not Found", msg)
        else:
            running = True
        return running

    def shutdown(self):
        self.rois_form.shutdown()