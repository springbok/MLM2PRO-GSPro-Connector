# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VerifyRoiForm.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_VerifyRoiForm(object):
    def setupUi(self, VerifyRoiForm):
        if not VerifyRoiForm.objectName():
            VerifyRoiForm.setObjectName(u"VerifyRoiForm")
        VerifyRoiForm.setWindowModality(Qt.ApplicationModal)
        VerifyRoiForm.resize(287, 309)
        self.verticalLayout = QVBoxLayout(VerifyRoiForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.results_view = QListWidget(VerifyRoiForm)
        self.results_view.setObjectName(u"results_view")
        font = QFont()
        font.setPointSize(12)
        self.results_view.setFont(font)

        self.verticalLayout.addWidget(self.results_view)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.close_button = QPushButton(VerifyRoiForm)
        self.close_button.setObjectName(u"close_button")

        self.horizontalLayout.addWidget(self.close_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(VerifyRoiForm)

        QMetaObject.connectSlotsByName(VerifyRoiForm)
    # setupUi

    def retranslateUi(self, VerifyRoiForm):
        VerifyRoiForm.setWindowTitle(QCoreApplication.translate("VerifyRoiForm", u"Verify ROI Results", None))
        self.close_button.setText(QCoreApplication.translate("VerifyRoiForm", u"Close", None))
    # retranslateUi

