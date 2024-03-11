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
        print(f'__setup_putting_device {self.main_window.putting_settings.system}')
        if self.main_window.putting_settings.system == PuttingSystems.WEBCAM:
            print('webcam device')
            self.putting_device = DevicePuttingWebcam(self.main_window)
        elif self.main_window.putting_settings.system == PuttingSystems.EXPUTT:
            self.putting_device = DevicePuttingExPutt(self.main_window)
        else:
            self.putting_device = None
        self.__display_putting_system()

    def __setup_signals(self):
        self.main_window.putting_settings_form.saved.connect(self.__putting_settings_saved)
        self.main_window.putting_server_button.clicked.connect(self.__putting_stop_start)
        self.main_window.actionPuttingSettings.triggered.connect(self.__putting_settings)

    def __putting_stop_start(self):
        if self.putting_device is not None:
            if self.putting_device.is_running():
                self.putting_device.stop()
            else:
                self.putting_device.start_app()
                self.putting_device.start()
            self.putting_device.device_worker.club_selected(self.main_window.gspro_connection.current_club)

    def __putting_started(self):
        self.main_window.putting_server_button.setText('Stop')
        self.main_window.putting_server_status_label.setText('Running')
        self.main_window.putting_server_status_label.setStyleSheet(f"QLabel {{ background-color : green; color : white; }}")
        QCoreApplication.processEvents()

    def __putting_settings(self):
        self.previous_putting_system = PuttingSystems.NONE
        if self.putting_device is not None:
            self.previous_putting_system = self.main_window.putting_settings.system
            self.putting_device.pause()
        self.main_window.putting_settings_form.show()

    def __putting_settings_saved(self):
        self.main_window.putting_settings_form.close()
        # Reload updated settings
        self.main_window.putting_settings.load()
        # Check if putting device changed
        if self.previous_putting_system != self.main_window.putting_settings.system:
            if self.putting_device is not None:
                self.putting_device.shutdown()
                self.putting_device = None
            self.__setup_putting_device()
        if self.putting_device is not None:
            self.putting_device.reload_putting_rois()

    def __putting_settings_cancelled(self):
        if self.putting_device is not None and self.main_window.gspro_connection.connected:
            self.putting_device.reload_putting_rois()
            self.putting_device.resume()

    def __display_putting_system(self):
        self.main_window.putting_system_label.setText(self.main_window.putting_settings.system)
        self.main_window.putting_server_button.setText('Start')
        self.main_window.putting_server_status_label.setText('Not Running')
        self.main_window.putting_server_status_label.setStyleSheet(
            f"QLabel {{ background-color : red; color : white; }}")
        if self.main_window.putting_settings.system == PuttingSystems.NONE:
            color = 'orange'
            self.main_window.putting_server_button.setEnabled(False)
        else:
            color = 'green'
            self.main_window.putting_server_button.setEnabled(True)
        self.main_window.putting_system_label.setStyleSheet(f"QLabel {{ background-color : {color}; color : white; }}")

    def shutdown(self):
        self.main_window.putting_settings_form.shutdown()
        if self.putting_device is not None:
            print('putting shutdown - putting device')
            self.putting_device.shutdown()
