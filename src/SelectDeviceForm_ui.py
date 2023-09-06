# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SelectDeviceForm.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_SelectDeviceForm(object):
    def setupUi(self, SelectDeviceForm):
        if not SelectDeviceForm.objectName():
            SelectDeviceForm.setObjectName(u"SelectDeviceForm")
        SelectDeviceForm.setWindowModality(Qt.ApplicationModal)
        SelectDeviceForm.resize(264, 389)
        self.horizontalLayout_2 = QHBoxLayout(SelectDeviceForm)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.devices_table = QTableWidget(SelectDeviceForm)
        if (self.devices_table.columnCount() < 1):
            self.devices_table.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.devices_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        self.devices_table.setObjectName(u"devices_table")
        self.devices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        self.devices_table.verticalHeader().setStretchLastSection(False)

        self.verticalLayout.addWidget(self.devices_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.select_button = QPushButton(SelectDeviceForm)
        self.select_button.setObjectName(u"select_button")

        self.horizontalLayout.addWidget(self.select_button)

        self.roi_button = QPushButton(SelectDeviceForm)
        self.roi_button.setObjectName(u"roi_button")

        self.horizontalLayout.addWidget(self.roi_button)

        self.close_button = QPushButton(SelectDeviceForm)
        self.close_button.setObjectName(u"close_button")

        self.horizontalLayout.addWidget(self.close_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(SelectDeviceForm)

        QMetaObject.connectSlotsByName(SelectDeviceForm)
    # setupUi

    def retranslateUi(self, SelectDeviceForm):
        SelectDeviceForm.setWindowTitle(QCoreApplication.translate("SelectDeviceForm", u"Select Device", None))
        ___qtablewidgetitem = self.devices_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("SelectDeviceForm", u"Name", None));
        self.select_button.setText(QCoreApplication.translate("SelectDeviceForm", u"Select", None))
        self.roi_button.setText(QCoreApplication.translate("SelectDeviceForm", u"ROI's", None))
        self.close_button.setText(QCoreApplication.translate("SelectDeviceForm", u"Cancel", None))
    # retranslateUi

