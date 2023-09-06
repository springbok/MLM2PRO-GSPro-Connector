# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RoisForm.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

from pyqtgraph import GraphicsLayoutWidget

class Ui_RoisForm(object):
    def setupUi(self, RoisForm):
        if not RoisForm.objectName():
            RoisForm.setObjectName(u"RoisForm")
        RoisForm.setWindowModality(Qt.ApplicationModal)
        RoisForm.resize(988, 581)
        self.centralwidget = QWidget(RoisForm)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.roi_button_layout = QHBoxLayout()
        self.roi_button_layout.setObjectName(u"roi_button_layout")
        self.zoomin_button = QPushButton(self.centralwidget)
        self.zoomin_button.setObjectName(u"zoomin_button")

        self.roi_button_layout.addWidget(self.zoomin_button)

        self.zoomout_button = QPushButton(self.centralwidget)
        self.zoomout_button.setObjectName(u"zoomout_button")

        self.roi_button_layout.addWidget(self.zoomout_button)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)

        self.roi_button_layout.addItem(self.horizontalSpacer_2)

        self.verify_button = QPushButton(self.centralwidget)
        self.verify_button.setObjectName(u"verify_button")

        self.roi_button_layout.addWidget(self.verify_button)

        self.reset_button = QPushButton(self.centralwidget)
        self.reset_button.setObjectName(u"reset_button")

        self.roi_button_layout.addWidget(self.reset_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.roi_button_layout.addItem(self.horizontalSpacer)

        self.save_button = QPushButton(self.centralwidget)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setAutoExclusive(False)

        self.roi_button_layout.addWidget(self.save_button)

        self.close_button = QPushButton(self.centralwidget)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setCheckable(False)
        self.close_button.setAutoExclusive(False)

        self.roi_button_layout.addWidget(self.close_button)


        self.gridLayout_2.addLayout(self.roi_button_layout, 0, 0, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.roi_graphics_layout = GraphicsLayoutWidget(self.centralwidget)
        self.roi_graphics_layout.setObjectName(u"roi_graphics_layout")

        self.gridLayout.addWidget(self.roi_graphics_layout, 0, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)

        RoisForm.setCentralWidget(self.centralwidget)

        self.retranslateUi(RoisForm)

        QMetaObject.connectSlotsByName(RoisForm)
    # setupUi

    def retranslateUi(self, RoisForm):
        RoisForm.setWindowTitle(QCoreApplication.translate("RoisForm", u"Specify ROI's", None))
        self.zoomin_button.setText(QCoreApplication.translate("RoisForm", u"Zoom In", None))
        self.zoomout_button.setText(QCoreApplication.translate("RoisForm", u"Zoom Out", None))
        self.verify_button.setText(QCoreApplication.translate("RoisForm", u"Verify", None))
        self.reset_button.setText(QCoreApplication.translate("RoisForm", u"Reset", None))
        self.save_button.setText(QCoreApplication.translate("RoisForm", u"Save", None))
        self.close_button.setText(QCoreApplication.translate("RoisForm", u"Close", None))
    # retranslateUi

