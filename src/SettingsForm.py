from pathlib import Path

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog
from src.SettingsForm_ui import Ui_SettingsForm
from src.settings import Settings


class SettingsForm(QWidget, Ui_SettingsForm):

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setupUi(self)
        self.close_button.clicked.connect(self.__close)
        self.save_button.clicked.connect(self.__save)
        self.file_browse_button.clicked.connect(self.__file_dialog)


    def showEvent(self, event: QShowEvent) -> None:
        self.__load_values()

    def __close(self):
        self.close()

    def __save(self):
        if self.__valid():
            self.settings.ip_address = self.ipaddress_edit.toPlainText()
            self.settings.port = int(self.port_edit.toPlainText())
            self.settings.gspro_path = self.gspro_path_edit.toPlainText()
            self.settings.grspo_window_name = self.gspro_window_name.toPlainText()
            self.settings.gspro_api_window_name = self.gspro_api_window_name.toPlainText()
            self.settings.save()
            QMessageBox.information(self, "Settings Updated", f"Settings have been updated.")

    def __valid(self):
        error = True
        if len(self.ipaddress_edit.toPlainText()) <= 0:
            QMessageBox.information(self, "Error", "IP Address is required.")
            error = False
        if not error and len(self.port_edit.toPlainText()) <= 0:
            QMessageBox.information(self, "Error", "Port is required.")
            error = False
        return error

    def __load_values(self):
        self.ipaddress_edit.setPlainText(self.settings.ip_address)
        self.port_edit.setPlainText(str(self.settings.port))
        self.gspro_path_edit.setPlainText(str(self.settings.gspro_path))
        self.gspro_window_name.setPlainText(str(self.settings.grspo_window_name))
        self.gspro_api_window_name.setPlainText(str(self.settings.gspro_api_window_name))

    def __file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            self.gspro_path_edit.toPlainText(),
            "Exe (*.exe *.lnk *.bat)"
        )
        if filename:
            path = Path(filename)
            self.gspro_path_edit.setPlainText(str(path))
