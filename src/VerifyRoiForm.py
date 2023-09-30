import PySide6
from PySide6 import QtGui
from PySide6.QtWidgets import QWidget
from src.VerifyRoiForm_ui import Ui_VerifyRoiForm
from src.ball_data import BallData


class VerifyRoiForm(QWidget, Ui_VerifyRoiForm):

    def __init__(self, rois_properties):
        super().__init__()
        self.rois_properties = rois_properties
        self.setupUi(self)
        self.close_button.clicked.connect(self.__close)
        self.balldata = {}

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        # Load data into the table
        self.__load_results()

    def __close(self):
        self.close()

    def __load_results(self):
        self.results_view.clear()
        items = []
        for roi in self.rois_properties:
            value = getattr(self.balldata, roi)
            if int(value) == BallData.invalid_value:
                value = 'Invalid Value'
            items.append(f'{BallData.properties[roi]}: {value}')
        self.results_view.addItems(items)
