# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsForm.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLayout, QPlainTextEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_SettingsForm(object):
    def setupUi(self, SettingsForm):
        if not SettingsForm.objectName():
            SettingsForm.setObjectName(u"SettingsForm")
        SettingsForm.setWindowModality(Qt.ApplicationModal)
        SettingsForm.resize(339, 294)
        self.verticalLayoutWidget_2 = QWidget(SettingsForm)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(9, 9, 321, 279))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetMinimumSize)
        self.ipaddress_edit = QPlainTextEdit(self.verticalLayoutWidget_2)
        self.ipaddress_edit.setObjectName(u"ipaddress_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ipaddress_edit.sizePolicy().hasHeightForWidth())
        self.ipaddress_edit.setSizePolicy(sizePolicy)
        self.ipaddress_edit.setMinimumSize(QSize(0, 31))
        self.ipaddress_edit.setTabChangesFocus(True)

        self.verticalLayout_3.addWidget(self.ipaddress_edit)

        self.port_edit = QPlainTextEdit(self.verticalLayoutWidget_2)
        self.port_edit.setObjectName(u"port_edit")
        sizePolicy.setHeightForWidth(self.port_edit.sizePolicy().hasHeightForWidth())
        self.port_edit.setSizePolicy(sizePolicy)
        self.port_edit.setMinimumSize(QSize(0, 31))
        self.port_edit.setTabChangesFocus(True)

        self.verticalLayout_3.addWidget(self.port_edit)

        self.gspro_window_name = QPlainTextEdit(self.verticalLayoutWidget_2)
        self.gspro_window_name.setObjectName(u"gspro_window_name")
        sizePolicy.setHeightForWidth(self.gspro_window_name.sizePolicy().hasHeightForWidth())
        self.gspro_window_name.setSizePolicy(sizePolicy)
        self.gspro_window_name.setMinimumSize(QSize(0, 31))

        self.verticalLayout_3.addWidget(self.gspro_window_name)

        self.gspro_api_window_name = QPlainTextEdit(self.verticalLayoutWidget_2)
        self.gspro_api_window_name.setObjectName(u"gspro_api_window_name")
        sizePolicy.setHeightForWidth(self.gspro_api_window_name.sizePolicy().hasHeightForWidth())
        self.gspro_api_window_name.setSizePolicy(sizePolicy)
        self.gspro_api_window_name.setMinimumSize(QSize(0, 31))

        self.verticalLayout_3.addWidget(self.gspro_api_window_name)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gspro_path_edit = QPlainTextEdit(self.verticalLayoutWidget_2)
        self.gspro_path_edit.setObjectName(u"gspro_path_edit")
        sizePolicy.setHeightForWidth(self.gspro_path_edit.sizePolicy().hasHeightForWidth())
        self.gspro_path_edit.setSizePolicy(sizePolicy)
        self.gspro_path_edit.setMaximumSize(QSize(16777215, 31))
        self.gspro_path_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.horizontalLayout_2.addWidget(self.gspro_path_edit)

        self.file_browse_button = QPushButton(self.verticalLayoutWidget_2)
        self.file_browse_button.setObjectName(u"file_browse_button")

        self.horizontalLayout_2.addWidget(self.file_browse_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_7 = QLabel(self.verticalLayoutWidget_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_9.addWidget(self.label_7)

        self.default_device_combo = QComboBox(self.verticalLayoutWidget_2)
        self.default_device_combo.addItem("")
        self.default_device_combo.addItem("")
        self.default_device_combo.setObjectName(u"default_device_combo")

        self.horizontalLayout_9.addWidget(self.default_device_combo)


        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 1)

        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_6 = QLabel(self.verticalLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_10.addWidget(self.label_6)

        self.launch_monitor_combo = QComboBox(self.verticalLayoutWidget_2)
        self.launch_monitor_combo.addItem("")
        self.launch_monitor_combo.addItem("")
        self.launch_monitor_combo.setObjectName(u"launch_monitor_combo")

        self.horizontalLayout_10.addWidget(self.launch_monitor_combo)


        self.verticalLayout.addLayout(self.horizontalLayout_10)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.save_button = QPushButton(self.verticalLayoutWidget_2)
        self.save_button.setObjectName(u"save_button")

        self.horizontalLayout.addWidget(self.save_button)

        self.close_button = QPushButton(self.verticalLayoutWidget_2)
        self.close_button.setObjectName(u"close_button")

        self.horizontalLayout.addWidget(self.close_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(SettingsForm)

        QMetaObject.connectSlotsByName(SettingsForm)
    # setupUi

    def retranslateUi(self, SettingsForm):
        SettingsForm.setWindowTitle(QCoreApplication.translate("SettingsForm", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.ipaddress_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"IP Address", None))
#endif // QT_CONFIG(tooltip)
        self.ipaddress_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"IP Address", None))
#if QT_CONFIG(tooltip)
        self.port_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.port_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Port", None))
        self.gspro_window_name.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro Window Title", None))
        self.gspro_api_window_name.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro API Window Title", None))
#if QT_CONFIG(tooltip)
        self.gspro_path_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Application Path(Opyional)", None))
#endif // QT_CONFIG(tooltip)
        self.gspro_path_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro Path", None))
        self.file_browse_button.setText(QCoreApplication.translate("SettingsForm", u"Browse", None))
        self.label_7.setText(QCoreApplication.translate("SettingsForm", u"Default Device", None))
        self.default_device_combo.setItemText(0, QCoreApplication.translate("SettingsForm", u"None", None))
        self.default_device_combo.setItemText(1, QCoreApplication.translate("SettingsForm", u"New Item", None))

        self.label_6.setText(QCoreApplication.translate("SettingsForm", u"Launch Monitor", None))
        self.launch_monitor_combo.setItemText(0, QCoreApplication.translate("SettingsForm", u"None", None))
        self.launch_monitor_combo.setItemText(1, QCoreApplication.translate("SettingsForm", u"New Item", None))

#if QT_CONFIG(tooltip)
        self.save_button.setToolTip(QCoreApplication.translate("SettingsForm", u"New Device", None))
#endif // QT_CONFIG(tooltip)
        self.save_button.setText(QCoreApplication.translate("SettingsForm", u"Save", None))
#if QT_CONFIG(tooltip)
        self.close_button.setToolTip(QCoreApplication.translate("SettingsForm", u"New Device", None))
#endif // QT_CONFIG(tooltip)
        self.close_button.setText(QCoreApplication.translate("SettingsForm", u"Close", None))
    # retranslateUi

