from PySide6.QtCore import QCoreApplication

from src import MainWindow
from src.device_putting_exputt import DevicePuttingExPutt
from src.device_putting_webcam import DevicePuttingWebcam
from src.putting_settings import PuttingSystems


class Putting:

    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.__setup_putting_device()
        self.__setup_signals()

    def __setup_putting_device(self):
        if self.main_window.putting_settings.system == PuttingSystems.WEBCAM:
            self.putting_device = DevicePuttingWebcam(self.main_window)
        elif self.main_window.putting_settings.system == PuttingSystems.EXPUTT:
            self.putting_device = DevicePuttingExPutt(self.main_window)
        else:
            self.putting_device = None
        self.__display_putting_system()

    def __setup_signals(self):
        self.main_window.putting_settings_form.saved.connect(self.__putting_settings_saved)
        self.main_window.putting_settings_form.cancel.connect(self.__putting_settings_cancelled)
        self.main_window.putting_server_button.clicked.connect(self.__putting_stop_start)
        self.main_window.actionPuttingSettings.triggered.connect(self.__putting_settings)
        self.main_window.gspro_connection.club_selected.connect(self.__club_selected)

    def __putting_started(self):
        self.main_window.putting_server_button.setText('Stop')
        self.main_window.putting_server_status_label.setText('Running')
        self.main_window.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        QCoreApplication.processEvents()

    def __putting_settings(self):
        self.previous_putting_system = PuttingSystems.NONE
        if self.putting_device is not None:
            self.previous_putting_system = self.putting_device.system
            self.putting_device.pause()
        self.main_window.putting_settings_form.show()

    def __putting_settings_saved(self):
        # Reload updated settings
        self.main_window.putting_settings.load()
        # Check if putting device changed
        if self.previous_putting_system != self.main_window.putting_settings.system and self.putting_device is not None:
            self.putting_device.shutdown()
            self.putting_device = None
        self.putting_device.reload_putting_rois()

    def __putting_settings_cancelled(self):
        if not self.putting_device is None and self.main_window.gspro_connection.connected:
            self.putting_device.reload_putting_rois()
            self.putting_device.resume()

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
        self.main_window.putting_system_label.setText(self.main_window.putting_settings.system)
        if self.main_window.putting_settings.system == PuttingSystems.NONE:
            color = 'orange'
        else:
            color = 'green'
        self.main_window.putting_system_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")


    def __club_selected(self, club_data):
        if (self.club_selection.text() != club_data['Player']['Club'] and
                (club_data['Player']['Club'] != "PT" or (club_data['Player']['Club'] == "PT" and self.club_selection.text() != 'Putter'))):
            self.log_message(LogMessageTypes.LOGS, LogMessageSystems.GSPRO_CONNECT, f"Change of Club: {club_data['Player']['Club']}")
            if club_data['Player']['Club'] == "PT":
                self.club_selection.setText('Putter')
                self.club_selection.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
                #if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
                #    self.webcam_putting.select_putter(True)
                #    self.webcam_putting.start_putting_app()
                #    ScreenMirrorWindow.top_window(self.putting_settings.webcam['window_name'])
                #elif self.current_putting_system == PuttingSystems.EXPUTT:
                #    self.screenshot_worker.select_putter(True)
            else:
                self.club_selection.setText(club_data['Player']['Club'])
                self.club_selection.setStyleSheet(f"QLabel {{ background-color : orange; color : white; }}")
                #if not self.webcam_putting is None and self.webcam_putting.running and self.current_putting_system == PuttingSystems.WEBCAM:
                #    self.webcam_putting.select_putter(False)
                #    ScreenMirrorWindow.not_top_window(self.putting_settings.webcam['window_name'])
                #    ScreenMirrorWindow.bring_to_front(self.settings.grspo_window_name)
                #elif self.current_putting_system == PuttingSystems.EXPUTT:
                #    self.screenshot_worker.select_putter(False)
            QCoreApplication.processEvents()

    def pause(self):
        return


    def shutdown(self):
        self.main_window.putting_settings_form.shutdown()
        #if not self.webcam_putting is None:
        #    self.webcam_putting.shutdown()
