import logging
import subprocess
from threading import Event

import cv2
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QMessageBox, QProgressDialog

from src.PuttingForm_ui import Ui_PuttingForm
from src.RoisExPuttForm import RoisExPuttForm
from src.ball_data import BallData
from src.ctype_screenshot import ScreenMirrorWindow
from src.putting_settings import PuttingSystems


class PuttingForm(QWidget, Ui_PuttingForm):

    saved = Signal()
    cancel = Signal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = main_window.putting_settings
        self.rois_form = RoisExPuttForm(main_window=self.main_window)
        self.setupUi(self)
        self.__setup_ui()
        self.close_button.clicked.connect(self.__close)
        self.save_button.clicked.connect(self.__save)
        self.rois_button.clicked.connect(self.__rois)
        self.find_video_sources_button.clicked.connect(self.__find_video_sources)

    def __setup_ui(self):
        self.putting_system_combo.clear()
        #self.exputt_capture_card_combo.clear()
        self.webcam_auto_start_combo.clear()
        self.exputt_camera_auto_start_combo.clear()
        self.webcam_ball_color_combo.clear()
        self.webcam_camera_combo.clear()
        sources = []
        for i in range(8):
            sources.append(str(i))
        self.putting_system_combo.addItems([PuttingSystems.NONE, PuttingSystems.EXPUTT, PuttingSystems.WEBCAM])
        self.webcam_camera_combo.addItems(sources)
        #self.exputt_capture_card_combo.addItems(sources)
        self.webcam_auto_start_combo.addItems(['Yes', 'No'])
        self.exputt_camera_auto_start_combo.addItems(['Yes', 'No'])
        self.webcam_ball_color_combo.addItems(BallData.ballcolor_as_list())


    def showEvent(self, event: QShowEvent) -> None:
        self.__load_values()

    def __close(self):
        self.cancel.emit()
        self.close()

    def __load_values(self):
        self.webcam_camera_combo.setCurrentText(str(self.settings.webcam['camera']))
        self.webcam_ball_color_combo.setCurrentText(self.settings.webcam['ball_color'])
        self.webcam_auto_start_combo.setCurrentText(self.settings.webcam['auto_start'])
        self.exputt_camera_auto_start_combo.setCurrentText(self.settings.exputt['auto_start'])
        self.webcam_window_title_edit.setPlainText(self.settings.webcam['window_name'])
        self.putting_system_combo.setCurrentText(self.settings.system)
        #self.exputt_capture_card_combo.setCurrentText(str(self.settings.exputt['camera']))
        self.ball_tracking_app_params_edit.setPlainText(self.settings.webcam['params'])
        self.exputt_camera_window_title_edit.setPlainText(self.settings.exputt['window_name'])

    def __save(self):
        if self.__valid():
            self.settings.webcam['camera'] = int(self.webcam_camera_combo.currentText())
            self.settings.webcam['ball_color'] = self.webcam_ball_color_combo.currentText()
            self.settings.webcam['auto_start'] = self.webcam_auto_start_combo.currentText()
            self.settings.webcam['window_name'] = self.webcam_window_title_edit.toPlainText()
            self.settings.system = self.putting_system_combo.currentText()
            #self.settings.exputt['camera'] = int(self.exputt_capture_card_combo.currentText())
            self.settings.webcam['params'] = self.ball_tracking_app_params_edit.toPlainText()
            self.settings.exputt['window_name'] = self.exputt_camera_window_title_edit.toPlainText()
            self.settings.exputt['auto_start'] = self.exputt_camera_auto_start_combo.currentText()
            self.settings.save()
            self.saved.emit()
            msg = ''
            if self.settings.system == PuttingSystems.WEBCAM:
                msg = "For any updated settings to take effect:\nQuit/Close the Webcam putting app using the 'q' key.\nClose this form.\n'Start putting again, it should open the Webcam putting app using the new settings."
            else:
                msg = "Settings have been updated."
            QMessageBox.information(self, "Settings Updated", msg)

    def __valid(self):
        valid = True
        msg = ''
        if self.putting_system_combo.currentText() == PuttingSystems.WEBCAM:
            if len(self.webcam_window_title_edit.toPlainText()) <= 0:
                msg = "Ball Tracking App Window Title required."
        elif self.putting_system_combo.currentText() == PuttingSystems.EXPUTT:
            if len(self.settings.exputt['rois']) <= 0:
                msg = f"You are unable to select {PuttingSystems.EXPUTT} until the ROI's have been specified."
            if len(self.exputt_camera_window_title_edit.toPlainText()) <= 0:
                msg = "Camera App Window Title required."
        if len(msg) > 0:
            QMessageBox.information(self, "Error", msg)
            valid = False
        return valid

    def __find_video_sources(self):
        QMessageBox.information(self, "Video Sources", "Press ok to start a search for all video sources.\nA window will be opened for each valid source.\nThe search may take some time.")
        progress = QProgressDialog("Searching...", '', 0, 24, self)
        progress.setWindowTitle("Search for Video Sources")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        task = 0
        valid_sources = []
        logging.debug('Checking for available video sources')
        for i in range(8):
            try:
                progress.setValue(task)
                cap = cv2.VideoCapture(i)
                if cap is None or not cap.isOpened():
                    logging.debug(f'Unable to open video source: {i}')
                else:
                    valid_sources.append(i)
                    logging.debug(f'Found a valid video source: {i}')
            except:
                logging.debug(f'Unable to open video source: {i}')
            task = task + 1
        caps = []
        for webcam in valid_sources:
            progress.setValue(task)
            caps.append(cv2.VideoCapture(webcam))
            task = task + 1
        for webcam in valid_sources:
            progress.setValue(task)
            ret, frame = caps[webcam].read()
            # Display the resulting frame
            cv2.imshow('webcam'+str(webcam), frame)
            task = task + 1
        progress.hide()

    def __rois(self):
        try:
            ScreenMirrorWindow.find_window(self.settings.exputt['window_name'])
        except:
            subprocess.run('start microsoft.windows.camera:', shell=True)
        Event().wait(1)
        self.rois_form.show()

    def shutdown(self):
        self.rois_form.shutdown()