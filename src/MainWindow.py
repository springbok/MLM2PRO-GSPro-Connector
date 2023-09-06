import logging
import os
from dataclasses import dataclass
from datetime import datetime
from PySide6.QtCore import Qt, QCoreApplication, QThread
from PySide6.QtGui import QShowEvent, QFont, QColor, QPalette
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QTextEdit, QHBoxLayout
from src.DevicesForm import DevicesForm
from src.SettingsForm import SettingsForm
from src.MainWindow_ui import Ui_MainWindow
from src.SelectDeviceForm import SelectDeviceForm
from src.appdata import AppDataPaths
from src.ball_data import BallData, BallMetrics
from src.ctype_screenshot import ScreenMirrorWindow
from src.gspro_connection import GSProConnection
from src.log_message import LogMessage, LogMessageSystems, LogMessageTypes
from src.screenshot_worker import ScreenshotWorker
from src.settings import Settings
from src.custom_exception import WindowNotFoundException


@dataclass
class LogTableCols:
    date = 0
    system = 1
    message = 2


class MainWindow(QMainWindow, Ui_MainWindow):
    version = 'V1.00.00'
    app_name = 'MLM2PRO-GSPro-Connector'

    def __init__(self, app):
        super().__init__()
        self.setupUi(self)
        self.current_device = None
        self.edit_fields = {}
        self.app = app
        self.app_paths = AppDataPaths('mlm2pro-gspro-connect')
        self.app_paths.setup()
        self.settings = Settings(self.app_paths)
        self.__setup_logging()
        self.gspro_connection = GSProConnection(self, self.settings)
        self.devices = DevicesForm(self.app_paths)
        self.select_device = SelectDeviceForm(main_window=self, app_paths=self.app_paths)
        self.settings_form = SettingsForm(self.settings)
        self.__setup_ui()
        self.__setup_screenshot_thread()

    def __setup_logging(self):
        level = logging.DEBUG
        path = self.app_paths.get_log_file_path()
        if os.path.isfile(path):
            os.unlink(path)
        logging.basicConfig(
            format="%(asctime)s,%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            level=level,
            filename=path,
            encoding='utf-8',
            force=True
        )
        logging.getLogger(__name__)
        logging.getLogger("PIL.PngImagePlugin").setLevel(logging.CRITICAL + 1)

    def __setup_screenshot_thread(self):
        self.screenshot_thread = QThread()
        self.screenshot_worker = ScreenshotWorker(self.settings.screenshot_interval)
        self.screenshot_worker.moveToThread(self.screenshot_thread)
        self.screenshot_thread.started.connect(self.screenshot_worker.run)
        self.screenshot_worker.shot.connect(self.gspro_connection.send_shot_worker.run)
        self.screenshot_worker.bad_shot.connect(self.__bad_shot)
        self.screenshot_worker.error.connect(self.__screenshot_worker_error)
        self.screenshot_worker.paused.connect(self.__screenshot_worker_paused)
        self.screenshot_worker.resumed.connect(self.__screenshot_worker_resumed)
        self.screenshot_thread.start()

    def __screenshot_worker_error(self, error):
        if isinstance(error[0], WindowNotFoundException):
            msg = f"Screen capture application ' {self.current_device.window_name}' does not seem to be running.\nPlease start the app, then press the 'Restart' button to restart the connector."
            self.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        else:
            msg = f"An unexpected error has occurred.\nException: {format(error[0])}"
            self.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, msg)
        self.__screenshot_worker_paused()
        QMessageBox.critical(self, "Connector Error", msg)

    def showEvent(self, event: QShowEvent) -> None:
        super(QMainWindow, self).showEvent(event)
        # Start GSPro if not running
        if len(self.settings.gspro_path) > 0 and len(self.settings.grspo_window_name) and os.path.exists(self.settings.gspro_path):
            try:
                ScreenMirrorWindow.find_window(self.settings.grspo_window_name)
            except:
                self.log_message(LogMessageTypes.ALL, LogMessageSystems.CONNECTOR, f"GSPro not running, starting")
                try:
                    os.startfile(self.settings.gspro_path)
                except Exception as e:
                    self.log_message(LogMessageTypes.LOGS, LogMessageSystems.CONNECTOR, "Could not start GSPro at {self.settings.gspro_path}.\nException: {format(e)}")

    def __setup_ui(self):
        self.__update_selected_mirror_app()
        self.actionExit.triggered.connect(self.__exit)
        self.actionAbout.triggered.connect(self.__about)
        self.actionDevices.triggered.connect(self.__devices)
        self.actionSettings.triggered.connect(self.__settings)
        self.select_device_button.clicked.connect(self.__select_device)
        self.gspro_connect_button.clicked.connect(self.__gspro_connect)
        self.main_tab.setCurrentIndex(0)
        #self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.setHorizontalHeaderLabels(['Date', 'Type', 'System', 'Message'])
        self.log_table.setColumnWidth(LogTableCols.date, 120)
        self.log_table.setColumnWidth(LogTableCols.message, 1000)
        self.log_table.resizeRowsToContents()
        self.log_table.setTextElideMode(Qt.ElideNone)
        headings = ['Result']
        vla = list(BallData.properties).index(BallMetrics.VLA)+1
        hla = list(BallData.properties).index(BallMetrics.HLA)+1
        for metric in BallData.properties:
            headings.append(BallData.properties[metric])
        self.shot_history_table.resizeRowsToContents()
        self.shot_history_table.setTextElideMode(Qt.ElideNone)
        self.shot_history_table.setColumnCount(len(BallData.properties)+1)
        self.shot_history_table.setHorizontalHeaderLabels(headings)
        self.shot_history_table.setColumnWidth(vla, 150)
        self.shot_history_table.setColumnWidth(hla, 150)
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.shot_history_table.horizontalHeader().setFont(font)
        self.shot_history_table.selectionModel().selectionChanged.connect(self.__shot_history_changed)
        self.select_device.selected.connect(self.__device_selected)
        self.select_device.cancel.connect(self.__device_select_cancelled)
        self.gspro_connection.connected_to_gspro.connect(self.__gspro_connected)
        self.gspro_connection.disconnected_from_gspro.connect(self.__gspro_disconnected)
        self.gspro_connection.shot_sent.connect(self.__shot_sent)
        self.gspro_connection.gspro_app_not_found.connect(self.__gspro_app_not_found)
        self.__screenshot_worker_paused()
        self.restart_button.clicked.connect(self.__restart_connector)
        self.restart_button.setEnabled(False)
        # Find and load refs to all edit fields
        self.__find_edit_fields()

    def __device_select_cancelled(self):
        if not self.current_device is None and self.gspro_connection.connected:
            self.screenshot_worker.resume()

    def __gspro_connected(self):
        self.gspro_connect_button.setEnabled(True)
        self.log_message(LogMessageTypes.ALL, LogMessageSystems.GSPRO_CONNECT, f'Connected to GSPro')
        self.gspro_connect_button.setText('Disconnect')
        self.gspro_status_label.setText('Connected')
        self.gspro_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        if not self.current_device is None:
            self.screenshot_worker.resume()

    def __screenshot_worker_resumed(self):
        self.connector_status.setText('Ready')
        self.connector_status.setStyleSheet("QLabel { background-color : green; color : white; }")
        self.restart_button.setEnabled(False)

    def __screenshot_worker_paused(self):
        self.connector_status.setText('Not Ready')
        self.connector_status.setStyleSheet("QLabel { background-color : red; color : white; }")
        self.restart_button.setEnabled(True)

    def __restart_connector(self):
        self.screenshot_worker.resume()

    def __gspro_disconnected(self):
        self.screenshot_worker.pause()
        self.gspro_connect_button.setEnabled(True)
        self.log_message(LogMessageTypes.ALL, LogMessageSystems.GSPRO_CONNECT, 'Disconnected from GSPro')
        self.gspro_connect_button.setText('Connect')
        self.gspro_status_label.setText('Not Connected')
        self.gspro_status_label.setStyleSheet(f"QLabel {{ background-color : red; color : white; }}")

    def __exit(self):
        self.close()

    def closeEvent(self, event: QShowEvent) -> None:
        self.gspro_connection.shutdown()
        self.select_device.shutdown()
        self.screenshot_worker.shutdown()
        self.screenshot_thread.quit()
        self.screenshot_thread.wait()

    def __select_device(self):
        self.screenshot_worker.pause()
        self.select_device.show()

    def __settings(self):
        self.settings_form.show()

    def __gspro_connect(self):
        if self.gspro_connection.connected:
            self.gspro_connection.disconnect_from_gspro()
        else:
            self.gspro_connection.connect_to_gspro()

    def __about(self):
        QMessageBox.information(self, "About", f"{MainWindow.app_name}\nVersion: {MainWindow.version}")

    def __devices(self):
        self.devices.show()

    def __gspro_app_not_found(self):
        self.gspro_connection.disconnect_from_gspro()
        msg = f"GSPro API window '{self.settings.gspro_api_window_name}' does not seem to be running.\nStart GSPro or reset the API connector.\nPress 'Connect' to reconnect to GSPro."
        self.log_message(LogMessageTypes.LOGS,
                         LogMessageSystems.GSPRO_CONNECT,
                         msg)
        QMessageBox.critical(self, "GSPRO API Window Not Found", msg)

    def log_message(self, message_types, message_system, message):
        self.__add_log_row(
            LogMessage(
                message_types=message_types,
                message_system=message_system,
                message=message
            )
        )

    def __add_log_row(self, message: LogMessage):
        if message.display_on(LogMessageTypes.LOG_WINDOW):
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            item = QTableWidgetItem(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.log_table.setItem(row, LogTableCols.date, item)
            item = QTableWidgetItem(message.message_system)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.log_table.setItem(row, LogTableCols.system, item)
            item = QTableWidgetItem(message.message)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.log_table.setItem(row, LogTableCols.message, item)
            self.log_table.selectRow(self.log_table.rowCount()-1)
        if message.display_on(LogMessageTypes.LOG_FILE):
            logging.log(logging.INFO, message.message_string())
        if message.display_on(LogMessageTypes.STATUS_BAR):
            self.statusbar.showMessage(message.message, 2000)

    def __update_selected_mirror_app(self):
        if not self.current_device is None:
            self.selected_device.setText(self.current_device.name)
            self.selected_device.setStyleSheet("QLabel { background-color : green; color : white; }")
            self.selected_mirror_app.setText(self.current_device.window_name)
            self.selected_mirror_app.setStyleSheet("QLabel { background-color : green; color : white; }")
        else:
            self.selected_device.setText('No Device')
            self.selected_device.setStyleSheet("QLabel { background-color : red; color : white; }")
            self.selected_mirror_app.setText('No Mirror App')
            self.selected_mirror_app.setStyleSheet("QLabel { background-color : red; color : white; }")
        QCoreApplication.processEvents()

    def __device_selected(self, device):
        self.current_device = device
        self.__update_selected_mirror_app()
        self.screenshot_worker.change_device(device)
        if self.gspro_connection.connected:
            self.screenshot_worker.resume()

    def __shot_sent(self, balldata):
        self.__add_shot_history_row(balldata)

    def __bad_shot(self, balldata):
        self.__add_shot_history_row(balldata)

    def __add_shot_history_row(self, balldata: BallData):
        row = self.shot_history_table.rowCount()
        self.shot_history_table.insertRow(row)
        i=1
        for metric in BallData.properties:
            error = False
            if len(balldata.errors) > 0 and metric in balldata.errors and len(balldata.errors[metric]):
                error = True
                value = 'Error'
            else:
                value = str(getattr(balldata, metric))
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.shot_history_table.setItem(row, i, item)
            if error:
                item.setBackground(QColor("#ff3800"))
            else:
                item.setBackground(QColor("#62ff00"))
            i = i + 1
        result = 'Success'
        if not balldata.good_shot:
            result = 'Failure'
            for metric in balldata.errors:
                self.log_message(LogMessageTypes.LOGS,
                             LogMessageSystems.CONNECTOR,
                             f"{BallData.properties[metric]}: {balldata.errors[metric]}")
        else:
            self.log_message(LogMessageTypes.LOGS,
                     LogMessageSystems.GSPRO_CONNECT,
                     f"{result}: {balldata.to_json()}")
        item = QTableWidgetItem(result)
        item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.shot_history_table.setItem(row, 0, item)
        if not balldata.good_shot:
            item.setBackground(QColor("#ff3800"))
        else:
            item.setBackground(QColor("#62ff00"))
        self.shot_history_table.selectRow(self.shot_history_table.rowCount()-1)

    def __find_edit_fields(self):
        layouts = (self.edit_field_layout.itemAt(i) for i in range(self.edit_field_layout.count()))
        for layout in layouts:
            if isinstance(layout, QHBoxLayout):
                edits = (layout.itemAt(i).widget() for i in range(layout.count()))
                for edit in edits:
                    if isinstance(edit, QTextEdit):
                        self.edit_fields[edit.objectName().replace('_edit', '')] = edit

    def __shot_history_changed(self):
        i=1
        for metric in BallData.properties:
            item = self.shot_history_table.item(self.shot_history_table.currentRow(), i)
            self.edit_fields[metric].setPlainText(item.text())
            self.edit_fields[metric].setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            result = self.shot_history_table.item(self.shot_history_table.currentRow(), i).text()
            palette = self.edit_fields[metric].palette()
            palette.setColor(QPalette.Base, item.background().color())
            self.edit_fields[metric].setPalette(palette)
            i = i + 1
