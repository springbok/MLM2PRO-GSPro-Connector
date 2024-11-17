from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QFileDialog

from src.DevicesForm_ui import Ui_DevicesForm
from src.appdata import AppDataPaths
from src.ctype_screenshot import open_window_titles
from src.device import Device
from src.devices import Devices


class DevicesForm(QWidget, Ui_DevicesForm):
    name_col = 0
    window_title_col = 1
    path_col = 2

    def __init__(self, app_paths: AppDataPaths):
        super().__init__()
        self.setupUi(self)
        self.app_paths = app_paths
        self.close_button.clicked.connect(self.__close)
        self.new_button.clicked.connect(self.__new_device)
        self.save_button.clicked.connect(self.__save_device)
        self.delete_button.clicked.connect(self.__delete_device)
        self.open_windows_title_button.clicked.connect(self.__open_windows_title)
        self.file_browse_button.clicked.connect(self.__file_dialog)
        self.devices_table.resizeRowsToContents()
        self.devices_table.setTextElideMode(Qt.ElideNone)
        self.devices_table.setHorizontalHeaderLabels(['Device Name', 'Mirror App Window Title', 'Mirror App Path'])
        self.devices_table.setColumnWidth(DevicesForm.name_col, 100)
        self.devices_table.setColumnWidth(DevicesForm.window_title_col, 200)
        self.devices_table.setColumnWidth(DevicesForm.path_col, 500)

    def __close(self):
        self.close()

    def showEvent(self, event):
        # Load data into the table
        self.devices_table.selectionModel().selectionChanged.disconnect()
        self.devices = Devices(self.app_paths)
        self.devices_table.setRowCount(0)
        self.__load_device_table()
        self.devices_table.selectRow(0)
        self.devices_table.selectionModel().selectionChanged.connect(self.__selection_changed)
        self.current_row_edit.setVisible(False)
        self.current_row_edit.setText('1')

    def __open_windows_title(self):
        titles = open_window_titles()
        titles = [title for title in titles if title]
        titles = '\n'.join(titles)
        QMessageBox.information(self, "Display Open Window Titles", f"Please open your mirror app and click OK.")
        QMessageBox.information(self, "Open Window Titles", f"Here are the titles of all open windows:\n{titles}")

    def __new_device(self):
        self.name_edit.setPlainText('')
        self.window_title_edit.setPlainText('')
        self.current_row_edit.setText('-1')

    def __save_device(self):
        if self.__valid():
            if int(self.current_row_edit.toPlainText()) < 0:
                device = Device(len(self.devices.devices)+1,
                                self.name_edit.toPlainText(), '',
                                {'left': 0, 'top': 0, 'right': 0, 'bottom': 0},
                                self.window_title_edit.toPlainText(),
                                {}, self.app_paths.app_data_path, False)
                device.save()
                self.devices.devices.append(device)
                self.__add_row(device)
                self.devices_table.selectRow(self.devices_table.rowCount())
                QMessageBox.information(self, "Device Created", f"Device {self.name_edit.toPlainText()} created.")
            else:
                device = self.devices.find_device(self.devices_table.item(self.devices_table.currentRow(), DevicesForm.name_col).text())
                if not device is None:
                    if self.devices_table.item(self.devices_table.currentRow(), DevicesForm.name_col).text() != self.name_edit.toPlainText():
                        device.change_name(self.name_edit.toPlainText())
                    device.window_name = self.window_title_edit.toPlainText()
                    device.window_path = self.path_edit.toPlainText()
                    device.save()
                    self.devices_table.item(self.devices_table.currentRow(), DevicesForm.name_col).setText(self.name_edit.toPlainText())
                    self.devices_table.item(self.devices_table.currentRow(), DevicesForm.window_title_col).setText(self.window_title_edit.toPlainText())
                    self.devices_table.item(self.devices_table.currentRow(), DevicesForm.path_col).setText(self.path_edit.toPlainText())
                    QMessageBox.information(self, "Device Updated", f"Device {self.name_edit.toPlainText()} updated.")

    def __delete_device(self):
        row = int(self.current_row_edit.toPlainText())
        if row < 0:
            QMessageBox.information(self, "Error", "No device selected.")
        else:
            button = QMessageBox.question(self, "Delete Device?", f"Are you sure you want to delete device {self.name_edit.toPlainText()}")
            if button == QMessageBox.Yes:
                QMessageBox.information(self, "Device Deleted",
                    f"Device {self.name_edit.toPlainText()} deleted.")
            device = self.devices.find_device(self.name_edit.toPlainText())
            if not device is None:
                device.delete()
                self.devices.devices.remove(device)
            self.devices_table.removeRow(row)
            self.devices_table.selectRow(0)

    def __valid(self):
        error = True
        if len(self.name_edit.toPlainText()) <= 0:
            QMessageBox.information(self, "Error", "Device Name is required.")
            error = False
        if not error and len(self.window_title_edit.toPlainText()) <= 0:
            QMessageBox.information(self, "Error", "Mirror App Window Name is required.")
            error = False
        return error

    def __selection_changed(self, selected, deselected):
        if int(self.current_row_edit.toPlainText()) != self.devices_table.currentRow():
            self.name_edit.setPlainText(self.devices_table.item(self.devices_table.currentRow(), DevicesForm.name_col).text())
            self.window_title_edit.setPlainText(self.devices_table.item(self.devices_table.currentRow(), DevicesForm.window_title_col).text())
            self.path_edit.setPlainText(self.devices_table.item(self.devices_table.currentRow(), DevicesForm.path_col).text())
            self.current_row_edit.setText(str(self.devices_table.currentRow()))


    def __load_device_table(self):
        for device in self.devices.devices:
            self.__add_row(device)

    def __add_row(self, device: Device):
        row = self.devices_table.rowCount()
        self.devices_table.insertRow(row)
        item = QTableWidgetItem(device.name)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.devices_table.setItem(row, DevicesForm.name_col, item)
        item = QTableWidgetItem(device.window_name)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.devices_table.setItem(row, DevicesForm.window_title_col, item)
        item = QTableWidgetItem(device.window_path)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.devices_table.setItem(row, DevicesForm.path_col, item)

    def __file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            self.path_edit.toPlainText(),
            "Exe (*.exe *.lnk *.bat)"
        )
        if filename:
            path = Path(filename)
            self.path_edit.setPlainText(str(path))
