import logging
import os
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QShowEvent, QFont, QColor, QPalette
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QTextEdit, QHBoxLayout
from src.PuttingForm import PuttingForm
from src.SettingsForm import SettingsForm
from src.MainWindow_ui import Ui_MainWindow
from src.appdata import AppDataPaths
from src.ball_data import BallData, BallMetrics
from src.devices import Devices
from src.gspro_connection import GSProConnection
from src.launch_monitor_screenshot import LaunchMonitorScreenshot
from src.log_message import LogMessage, LogMessageSystems, LogMessageTypes
from src.putting_settings import PuttingSettings, PuttingSystems
from src.settings import Settings, LaunchMonitor
from src.custom_exception import PutterNotSelected


@dataclass
class LogTableCols:
    date = 0
    system = 1
    message = 2


class MainWindow(QMainWindow, Ui_MainWindow):
    version = 'V1.03.00'
    app_name = 'MLM2PRO-GSPro-Connector'
    good_shot_color = '#62ff00'
    good_putt_color = '#fbff00'
    bad_shot_color = '#ff3800'

    def __init__(self, app):
        super().__init__()
        self.setupUi(self)
        self.launch_monitor = None

        self.putter_selected = False
        self.edit_fields = {}
        self.app = app
        self.app_paths = AppDataPaths('mlm2pro-gspro-connect')
        self.app_paths.setup()
        self.__setup_logging()
        self.settings = Settings(self.app_paths)
        self.gspro_connection = GSProConnection(self)
        self.settings_form = SettingsForm(settings=self.settings, app_paths=self.app_paths)
        self.putting_settings = PuttingSettings(self.app_paths)
        self.putting_settings_form = PuttingForm(main_window=self)
        self.webcam_putting = None
        self.current_putting_system = None
        if self.settings.device_id != LaunchMonitor.R10:
            self.launch_monitor = LaunchMonitorScreenshot(self)
            self.launch_monitor.setup()
        self.__setup_ui()
        self.__auto_start()

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
        logging.debug(f"App Version: {MainWindow.version}")
        path = os.getcwd()
        for file in os.listdir(path):
            if file.endswith(".traineddata"):
                dt = datetime.fromtimestamp(os.stat(file).st_ctime)
                size = os.stat(file).st_size
                logging.debug(f"Training file name: {file} Date: {dt} Size: {size}")

    def showEvent(self, event: QShowEvent) -> None:
        super(QMainWindow, self).showEvent(event)

    def __setup_ui(self):
        self.actionExit.triggered.connect(self.__exit)
        self.actionAbout.triggered.connect(self.__about)
        self.actionDevices.triggered.connect(self.__devices)
        self.actionSettings.triggered.connect(self.__settings)
        self.actionPuttingSettings.triggered.connect(self.__putting_settings)
        self.actionDonate.triggered.connect(self.__donate)
        self.actionShop.triggered.connect(self.__shop)
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
        self.gspro_connection.connected_to_gspro.connect(self.__gspro_connected)
        self.gspro_connection.disconnected_from_gspro.connect(self.__gspro_disconnected)
        self.gspro_connection.shot_sent.connect(self.__shot_sent)
        self.gspro_connection.gspro_app_not_found.connect(self.__gspro_app_not_found)
        self.gspro_connection.club_selected.connect(self.__club_selected)
        self.restart_button.clicked.connect(self.__restart_connector)
        self.pause_button.clicked.connect(self.__pause_connector)
        self.restart_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.settings_form.saved.connect(self.__settings_saved)
        self.putting_settings_form.saved.connect(self.__putting_settings_saved)
        self.putting_settings_form.cancel.connect(self.__putting_settings_cancelled)
        self.putting_server_button.clicked.connect(self.__putting_stop_start)
        # Find and load refs to all edit fields
        self.putting_system_label.setText(self.putting_settings.system)
        self.__find_edit_fields()
        self.__putting_stopped()
        self.__display_putting_system()

    def __auto_start(self):
        # If a default device is specified try and start all components
        if hasattr(self.settings, 'default_device') and self.settings.default_device != 'None':
            self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR, f'Default Device specified, attempting to auto start all software')
            devices = Devices(self.app_paths)
            device = devices.find_device(self.settings.default_device)
            if not device is None:
                self.select_device.select_device(device)
                self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR, f'Selecting Device:{device.name}')
            self.__setup_putting()
            if len(self.settings.gspro_path) > 0 and len(self.settings.grspo_window_name) and os.path.exists(self.settings.gspro_path):
                self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR, f'Starting GSPro')
                self.gspro_connection.gspro_start(self.settings, True)
        else:
            self.gspro_connection.gspro_start(self.settings, False)


    def __club_selected(self, club_data):
        return
        '''
        hwnd = None
        logging.debug(f'__club_selected: {club_data}')
        if club_data['Player']['Club'] == "PT":
            self.club_selection.setText('Putter')
            self.club_selection.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
            if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
                self.webcam_putting.select_putter(True)
                self.webcam_putting.start_putting_app()
                ScreenMirrorWindow.top_window(self.putting_settings.webcam['window_name'])
            elif self.current_putting_system == PuttingSystems.EXPUTT:
                self.screenshot_worker.select_putter(True)
        else:
            self.club_selection.setText(club_data['Player']['Club'])
            self.club_selection.setStyleSheet(f"QLabel {{ background-color : orange; color : white; }}")
            if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
                self.webcam_putting.select_putter(False)
                ScreenMirrorWindow.not_top_window(self.putting_settings.webcam['window_name'])
                ScreenMirrorWindow.bring_to_front(self.settings.grspo_window_name)
            elif self.current_putting_system == PuttingSystems.EXPUTT:
                self.screenshot_worker.select_putter(False)
        self.screenshot_worker.club_selected(club_data['Player']['Club'])
        QCoreApplication.processEvents()
        '''

    def __putting_stop_start(self):
        return
        '''
        running = False
        if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
            self.putter_selected = False
            if not self.webcam_putting.http_server_worker is None and \
                    self.webcam_putting.http_server_worker.putter_selected():
                self.putter_selected = True
            self.webcam_putting.shutdown()
            self.webcam_putting = None
            running = True
        elif self.current_putting_system == PuttingSystems.EXPUTT and self.screenshot_worker.get_putting_active():
            self.screenshot_worker.set_putting_active(False)
            running = True
        logging.debug(f'putting running: {running} self.current_putting_system: {self.current_putting_system} self.screenshot_worker.get_putting_active(): {self.screenshot_worker.get_putting_active()}')
        if not running:
            self.__setup_putting()
        '''

    def __putting_error(self, error):
        self.log_message(LogMessageTypes.LOGS, LogMessageSystems.WEBCAM_PUTTING, f'Putting Error: {format(error)}')
        if not isinstance(error, ValueError) and not isinstance(error, PutterNotSelected):
            QMessageBox.warning(self, "Putting Error", f'{format(error)}')

    def __setup_putting(self):
        return
        '''
        self.__display_putting_system()
        if self.putting_settings.system == PuttingSystems.WEBCAM:
            self.putting_server_button.setEnabled(True)
            self.webcam_putting = PuttingWebcam(self.putting_settings)
            self.webcam_putting.started.connect(self.__putting_started)
            self.webcam_putting.stopped.connect(self.__putting_stopped)
            self.webcam_putting.error.connect(self.__putting_error)
            self.webcam_putting.putt_shot.connect(self.gspro_connection.send_shot_worker.run)
            if self.putting_settings.webcam['auto_start'] == 'Yes':
                self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR, f'Starting webcam putting')
                self.webcam_putting.start_server()
                if not self.webcam_putting.http_server_worker is None and self.putter_selected:
                    self.webcam_putting.http_server_worker.select_putter(self.putter_selected)
        elif self.putting_settings.system == PuttingSystems.EXPUTT:
            self.screenshot_worker.set_putting_active(True)
            self.screenshot_worker.putting_settings = self.putting_settings
            if self.putting_settings.exputt['auto_start'] == 'Yes':
                try:
                    self.log_message(LogMessageTypes.LOG_WINDOW, LogMessageSystems.CONNECTOR,
                                     f'Starting ExPutt')
                    ScreenMirrorWindow.find_window(self.putting_settings.exputt['window_name'])
                except:
                    subprocess.run('start microsoft.windows.camera:', shell=True)
        self.current_putting_system = self.putting_settings.system
        QCoreApplication.processEvents()
        '''

    def __display_putting_system(self):
        self.putting_system_label.setText(self.putting_settings.system)
        if self.putting_settings.system == PuttingSystems.NONE:
            color = 'orange'
        elif self.putting_settings.system == PuttingSystems.WEBCAM or self.putting_settings.system == PuttingSystems.EXPUTT:
            color = 'green'
        self.putting_system_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")
        QCoreApplication.processEvents()

    def __putting_settings_saved(self):
        return
        '''
        # Reload updated settings
        self.putting_settings.load()
        if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
            self.webcam_putting.shutdown()
            self.webcam_putting = None
        elif self.putting_settings.system == PuttingSystems.EXPUTT and self.screenshot_worker.get_putting_active():
            self.screenshot_worker.set_putting_active(False)
            self.screenshot_worker.reload_putting_rois()
        self.launch_monitor.resume()
        self.__display_putting_system()
        '''

    def __settings_saved(self):
        # Reload updated settings
        self.settings.load()

    def __putting_settings_cancelled(self):
        pass
        #if not self.current_device is None and self.gspro_connection.connected:
        #    self.screenshot_worker.reload_putting_rois()
        #    self.screenshot_worker.resume()


    def __gspro_connected(self):
        self.gspro_connect_button.setEnabled(True)
        self.log_message(LogMessageTypes.ALL, LogMessageSystems.GSPRO_CONNECT, f'Connected to GSPro')
        self.gspro_connect_button.setText('Disconnect')
        self.gspro_status_label.setText('Connected')
        self.gspro_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        self.launch_monitor.resume()

    def __restart_connector(self):
        self.launch_monitor.resume()

    def __pause_connector(self):
        self.launch_monitor.pause()

    def __putting_stopped(self):
        self.putting_server_button.setText('Start')
        self.putting_server_status_label.setText('Not Running')
        self.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : red; color : white; }}")
        QCoreApplication.processEvents()

    def __putting_started(self):
        self.putting_server_button.setText('Stop')
        self.putting_server_status_label.setText('Running')
        self.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        QCoreApplication.processEvents()

    def __gspro_disconnected(self):
        self.launch_monitor.pause()
        self.gspro_connect_button.setEnabled(True)
        self.log_message(LogMessageTypes.ALL, LogMessageSystems.GSPRO_CONNECT, 'Disconnected from GSPro')
        self.gspro_connect_button.setText('Connect')
        self.gspro_status_label.setText('Not Connected')
        self.gspro_status_label.setStyleSheet(f"QLabel {{ background-color : red; color : white; }}")

    def __exit(self):
        self.close()

    def closeEvent(self, event: QShowEvent) -> None:
        #if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
        #    ScreenMirrorWindow.not_top_window(self.putting_settings.webcam['window_name'])
        self.gspro_connection.shutdown()
        self.putting_settings_form.shutdown()
        self.launch_monitor.shutdown()
        #if not self.webcam_putting is None:
        #    self.webcam_putting.shutdown()
        sys.exit()

    def __settings(self):
        self.settings_form.show()

    def __putting_settings(self):
        return
        '''
        if (not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM) or \
            (self.current_putting_system == PuttingSystems.EXPUTT and self.screenshot_worker.get_putting_active()):
            self.__putting_stop_start()
        self.screenshot_worker.pause()
        self.putting_settings_form.show()
        '''

    def __donate(self):
        url = "https://ko-fi.com/springbok_dev"
        webbrowser.open(url, new=2) # 2 = open in new tab

    def __shop(self):
        url = "https://cascadia3dpd.com"
        webbrowser.open(url, new=2) # 2 = open in new tab

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
        QMessageBox.warning(self, "GSPRO API Window Not Found", msg)

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

    def __shot_sent(self, balldata):
        self.__add_shot_history_row(balldata)

    def bad_shot(self, balldata):
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
                item.setBackground(QColor(MainWindow.bad_shot_color))
            else:
                if balldata.putt_type is None:
                    item.setBackground(QColor(MainWindow.good_shot_color))
                else:
                    item.setBackground(QColor(MainWindow.good_putt_color))
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
            item.setBackground(QColor(MainWindow.bad_shot_color))
        else:
            if balldata.putt_type is None:
                item.setBackground(QColor(MainWindow.good_shot_color))
            else:
                item.setBackground(QColor(MainWindow.good_putt_color))
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
