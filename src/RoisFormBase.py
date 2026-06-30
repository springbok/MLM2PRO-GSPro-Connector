from functools import partial
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMainWindow, QMessageBox

from src.RoisForm_ui import Ui_RoisForm
from src.VerifyRoiForm import VerifyRoiForm
from src.ball_data import BallData, BallMetrics
from src.log_message import LogMessageTypes, LogMessageSystems
from src.settings import LaunchMonitor


class RoisFormBase(QMainWindow, Ui_RoisForm):

    closed = Signal()
    saved = Signal()

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.thread = QThread()
        self.verify_roi = VerifyRoiForm(self.__rois_properties())
        self.device = None
        self.current_button = None

    def __rois_properties(self):
        if self.__class__.__name__ == 'RoisExPuttForm':
            rois_properties = BallData.rois_putting_properties
            BallData.properties[BallMetrics.HLA] = "Launch Dir"
            BallData.properties[BallMetrics.CLUB_PATH] = "Putter path"
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = "Impact Angle"
        elif self.main_window.settings.device_id == LaunchMonitor.UNEEKOR or self.main_window.settings.device_id == LaunchMonitor.UNEEKOR_IPAD :
            rois_properties = BallData.rois_uneekor_properties
            BallData.properties[BallMetrics.VLA] = "Launch Angle"
            BallData.properties[BallMetrics.HLA] = "Side Angle"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = "Attack Angle"
        elif self.main_window.settings.device_id ==  LaunchMonitor.MEVOPLUS:
            rois_properties = BallData.rois_mevoplus_properties
            BallData.properties[BallMetrics.VLA] = "Launch V"
            BallData.properties[BallMetrics.HLA] = "Launch H"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = 'AOA'
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Face to target'
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Face to path'
        elif self.main_window.settings.device_id ==  LaunchMonitor.R50:
            rois_properties = BallData.rois_r50_properties
            BallData.properties[BallMetrics.HLA] = "Launch Direction"
            BallData.properties[BallMetrics.VLA] = "Launch Angle"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = "Attack Angle"
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Face to Path'
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Club Face'
        elif self.main_window.settings.device_id ==  LaunchMonitor.SKYTRAKPLUS :
            rois_properties = BallData.rois_skytrak_properties
            BallData.properties[BallMetrics.VLA] = "Launch Angle"
            BallData.properties[BallMetrics.HLA] = "Side Angle"
            BallData.properties[BallMetrics.CLUB_PATH] = 'Club path'
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Face to target'
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Face to path'
        else :
            rois_properties = BallData.rois_properties
            BallData.properties[BallMetrics.HLA] = "Launch Direction (HLA)"
            BallData.properties[BallMetrics.VLA] = "Launch Angle (VLA)"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = "Angle of Attack"
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Impact Angle'

        return rois_properties

    def setup_ui(self):
        self.roi_graphics_layout.addItem(self.roi_image)
        self.close_button.clicked.connect(self.__close)
        self.save_button.clicked.connect(self.save)
        self.reset_button.clicked.connect(self.reset)
        self.verify_button.clicked.connect(self.__verify)
        self.zoomin_button.clicked.connect(partial(self.__zoom,in_or_out='in'))
        self.zoomout_button.clicked.connect(partial(self.__zoom,in_or_out='out'))

    def __verify(self):
        self.roi_image.ocr_image()
        self.verify_roi.balldata = self.roi_image.balldata
        self.verify_roi.show()

    def __close(self):
        self.close()

    def save(self):
        pass

    def reset(self):
        pass

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def __zoom(self, in_or_out):
        self.roi_image.zoom(in_or_out)

    def in_progress(self):
        self.__log_message(LogMessageTypes.STATUS_BAR, f'Taking screenshot...')

    def error(self, error):
        msg = f"Error while trying to take a screenshot: {error}"
        self.__log_message(LogMessageTypes.LOGS, msg)
        QMessageBox.warning(self.main_window, "Screenshot Error", msg)

    def __log_message(self, types, message):
        self.main_window.log_message(types, LogMessageSystems.CONNECTOR, message)

    def shutdown(self):
        self.thread.quit()
        self.thread.wait()
