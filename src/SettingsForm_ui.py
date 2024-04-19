# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsForm.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_SettingsForm(object):
    def setupUi(self, SettingsForm):
        if not SettingsForm.objectName():
            SettingsForm.setObjectName(u"SettingsForm")
        SettingsForm.setWindowModality(Qt.ApplicationModal)
        SettingsForm.resize(892, 444)
        self.horizontalLayout_5 = QHBoxLayout(SettingsForm)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.r10_settings_groupbox_2 = QGroupBox(SettingsForm)
        self.r10_settings_groupbox_2.setObjectName(u"r10_settings_groupbox_2")
        self.verticalLayout_7 = QVBoxLayout(self.r10_settings_groupbox_2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.ipaddress_edit = QPlainTextEdit(self.r10_settings_groupbox_2)
        self.ipaddress_edit.setObjectName(u"ipaddress_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ipaddress_edit.sizePolicy().hasHeightForWidth())
        self.ipaddress_edit.setSizePolicy(sizePolicy)
        self.ipaddress_edit.setMinimumSize(QSize(0, 31))
        self.ipaddress_edit.setMaximumSize(QSize(16777215, 31))
        self.ipaddress_edit.setContextMenuPolicy(Qt.PreventContextMenu)
        self.ipaddress_edit.setTabChangesFocus(True)

        self.verticalLayout_7.addWidget(self.ipaddress_edit)

        self.gspro_window_name = QPlainTextEdit(self.r10_settings_groupbox_2)
        self.gspro_window_name.setObjectName(u"gspro_window_name")
        sizePolicy.setHeightForWidth(self.gspro_window_name.sizePolicy().hasHeightForWidth())
        self.gspro_window_name.setSizePolicy(sizePolicy)
        self.gspro_window_name.setMinimumSize(QSize(0, 31))
        self.gspro_window_name.setMaximumSize(QSize(16777215, 31))

        self.verticalLayout_7.addWidget(self.gspro_window_name)

        self.port_edit = QPlainTextEdit(self.r10_settings_groupbox_2)
        self.port_edit.setObjectName(u"port_edit")
        self.port_edit.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.port_edit.sizePolicy().hasHeightForWidth())
        self.port_edit.setSizePolicy(sizePolicy1)
        self.port_edit.setMinimumSize(QSize(0, 31))
        self.port_edit.setMaximumSize(QSize(16777215, 31))
        self.port_edit.setTabChangesFocus(True)

        self.verticalLayout_7.addWidget(self.port_edit)

        self.gspro_api_window_name = QPlainTextEdit(self.r10_settings_groupbox_2)
        self.gspro_api_window_name.setObjectName(u"gspro_api_window_name")
        sizePolicy.setHeightForWidth(self.gspro_api_window_name.sizePolicy().hasHeightForWidth())
        self.gspro_api_window_name.setSizePolicy(sizePolicy)
        self.gspro_api_window_name.setMinimumSize(QSize(0, 31))
        self.gspro_api_window_name.setMaximumSize(QSize(16777215, 31))

        self.verticalLayout_7.addWidget(self.gspro_api_window_name)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gspro_path_edit = QPlainTextEdit(self.r10_settings_groupbox_2)
        self.gspro_path_edit.setObjectName(u"gspro_path_edit")
        sizePolicy.setHeightForWidth(self.gspro_path_edit.sizePolicy().hasHeightForWidth())
        self.gspro_path_edit.setSizePolicy(sizePolicy)
        self.gspro_path_edit.setMinimumSize(QSize(300, 0))
        self.gspro_path_edit.setMaximumSize(QSize(16777215, 31))
        self.gspro_path_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.horizontalLayout_2.addWidget(self.gspro_path_edit)

        self.file_browse_button = QPushButton(self.r10_settings_groupbox_2)
        self.file_browse_button.setObjectName(u"file_browse_button")

        self.horizontalLayout_2.addWidget(self.file_browse_button)


        self.verticalLayout_7.addLayout(self.horizontalLayout_2)


        self.verticalLayout_8.addWidget(self.r10_settings_groupbox_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_2)


        self.horizontalLayout_6.addLayout(self.verticalLayout_8)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_6 = QLabel(SettingsForm)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_10.addWidget(self.label_6)

        self.launch_monitor_combo = QComboBox(SettingsForm)
        self.launch_monitor_combo.addItem("")
        self.launch_monitor_combo.addItem("")
        self.launch_monitor_combo.setObjectName(u"launch_monitor_combo")

        self.horizontalLayout_10.addWidget(self.launch_monitor_combo)


        self.verticalLayout_5.addLayout(self.horizontalLayout_10)

        self.r10_settings_groupbox = QGroupBox(SettingsForm)
        self.r10_settings_groupbox.setObjectName(u"r10_settings_groupbox")
        self.verticalLayout_6 = QVBoxLayout(self.r10_settings_groupbox)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.r10_settings_device_name_edit = QPlainTextEdit(self.r10_settings_groupbox)
        self.r10_settings_device_name_edit.setObjectName(u"r10_settings_device_name_edit")
        sizePolicy.setHeightForWidth(self.r10_settings_device_name_edit.sizePolicy().hasHeightForWidth())
        self.r10_settings_device_name_edit.setSizePolicy(sizePolicy)
        self.r10_settings_device_name_edit.setMinimumSize(QSize(0, 31))
        self.r10_settings_device_name_edit.setMaximumSize(QSize(16777215, 31))
        self.r10_settings_device_name_edit.setTabChangesFocus(True)

        self.verticalLayout_6.addWidget(self.r10_settings_device_name_edit)

        self.r10_settings_humidity_edit = QPlainTextEdit(self.r10_settings_groupbox)
        self.r10_settings_humidity_edit.setObjectName(u"r10_settings_humidity_edit")
        sizePolicy.setHeightForWidth(self.r10_settings_humidity_edit.sizePolicy().hasHeightForWidth())
        self.r10_settings_humidity_edit.setSizePolicy(sizePolicy)
        self.r10_settings_humidity_edit.setMinimumSize(QSize(0, 31))
        self.r10_settings_humidity_edit.setMaximumSize(QSize(16777215, 31))
        self.r10_settings_humidity_edit.setTabChangesFocus(True)

        self.verticalLayout_6.addWidget(self.r10_settings_humidity_edit)

        self.r10_settings_temperature_edit = QPlainTextEdit(self.r10_settings_groupbox)
        self.r10_settings_temperature_edit.setObjectName(u"r10_settings_temperature_edit")
        sizePolicy.setHeightForWidth(self.r10_settings_temperature_edit.sizePolicy().hasHeightForWidth())
        self.r10_settings_temperature_edit.setSizePolicy(sizePolicy)
        self.r10_settings_temperature_edit.setMinimumSize(QSize(0, 31))
        self.r10_settings_temperature_edit.setMaximumSize(QSize(16777215, 31))
        self.r10_settings_temperature_edit.setTabChangesFocus(True)

        self.verticalLayout_6.addWidget(self.r10_settings_temperature_edit)

        self.r10_settings_altitude_edit = QPlainTextEdit(self.r10_settings_groupbox)
        self.r10_settings_altitude_edit.setObjectName(u"r10_settings_altitude_edit")
        sizePolicy.setHeightForWidth(self.r10_settings_altitude_edit.sizePolicy().hasHeightForWidth())
        self.r10_settings_altitude_edit.setSizePolicy(sizePolicy)
        self.r10_settings_altitude_edit.setMinimumSize(QSize(0, 31))
        self.r10_settings_altitude_edit.setMaximumSize(QSize(16777215, 31))
        self.r10_settings_altitude_edit.setTabChangesFocus(True)

        self.verticalLayout_6.addWidget(self.r10_settings_altitude_edit)

        self.r10_settings_airdensity_edit = QPlainTextEdit(self.r10_settings_groupbox)
        self.r10_settings_airdensity_edit.setObjectName(u"r10_settings_airdensity_edit")
        sizePolicy.setHeightForWidth(self.r10_settings_airdensity_edit.sizePolicy().hasHeightForWidth())
        self.r10_settings_airdensity_edit.setSizePolicy(sizePolicy)
        self.r10_settings_airdensity_edit.setMinimumSize(QSize(0, 31))
        self.r10_settings_airdensity_edit.setMaximumSize(QSize(16777215, 31))
        self.r10_settings_airdensity_edit.setTabChangesFocus(True)

        self.verticalLayout_6.addWidget(self.r10_settings_airdensity_edit)

        self.r10_settings_tee_distance_edit = QPlainTextEdit(self.r10_settings_groupbox)
        self.r10_settings_tee_distance_edit.setObjectName(u"r10_settings_tee_distance_edit")
        sizePolicy.setHeightForWidth(self.r10_settings_tee_distance_edit.sizePolicy().hasHeightForWidth())
        self.r10_settings_tee_distance_edit.setSizePolicy(sizePolicy)
        self.r10_settings_tee_distance_edit.setMinimumSize(QSize(0, 31))
        self.r10_settings_tee_distance_edit.setMaximumSize(QSize(16777215, 31))
        self.r10_settings_tee_distance_edit.setTabChangesFocus(True)

        self.verticalLayout_6.addWidget(self.r10_settings_tee_distance_edit)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")

        self.verticalLayout_6.addLayout(self.horizontalLayout_4)


        self.verticalLayout_5.addWidget(self.r10_settings_groupbox)

        self.groupBox = QGroupBox(SettingsForm)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.relay_server_ip_edit = QPlainTextEdit(self.groupBox)
        self.relay_server_ip_edit.setObjectName(u"relay_server_ip_edit")
        sizePolicy.setHeightForWidth(self.relay_server_ip_edit.sizePolicy().hasHeightForWidth())
        self.relay_server_ip_edit.setSizePolicy(sizePolicy)
        self.relay_server_ip_edit.setMinimumSize(QSize(0, 31))
        self.relay_server_ip_edit.setMaximumSize(QSize(16777215, 31))
        self.relay_server_ip_edit.setTabChangesFocus(True)

        self.verticalLayout_4.addWidget(self.relay_server_ip_edit)

        self.relay_server_port_edit = QPlainTextEdit(self.groupBox)
        self.relay_server_port_edit.setObjectName(u"relay_server_port_edit")
        sizePolicy.setHeightForWidth(self.relay_server_port_edit.sizePolicy().hasHeightForWidth())
        self.relay_server_port_edit.setSizePolicy(sizePolicy)
        self.relay_server_port_edit.setMinimumSize(QSize(0, 31))
        self.relay_server_port_edit.setMaximumSize(QSize(16777215, 31))
        self.relay_server_port_edit.setTabChangesFocus(True)

        self.verticalLayout_4.addWidget(self.relay_server_port_edit)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.verticalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout_5.addWidget(self.groupBox)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_3)


        self.horizontalLayout_6.addLayout(self.verticalLayout_5)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetMinimumSize)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_7 = QLabel(SettingsForm)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(120, 0))
        self.label_7.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_9.addWidget(self.label_7)

        self.default_device_combo = QComboBox(SettingsForm)
        self.default_device_combo.addItem("")
        self.default_device_combo.addItem("")
        self.default_device_combo.setObjectName(u"default_device_combo")
        self.default_device_combo.setMinimumSize(QSize(130, 0))

        self.horizontalLayout_9.addWidget(self.default_device_combo)


        self.verticalLayout_3.addLayout(self.horizontalLayout_9)


        self.verticalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.auto_start_all_label = QLabel(SettingsForm)
        self.auto_start_all_label.setObjectName(u"auto_start_all_label")
        self.auto_start_all_label.setMinimumSize(QSize(120, 0))
        self.auto_start_all_label.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_11.addWidget(self.auto_start_all_label)

        self.auto_start_all_apps_combo = QComboBox(SettingsForm)
        self.auto_start_all_apps_combo.addItem("")
        self.auto_start_all_apps_combo.addItem("")
        self.auto_start_all_apps_combo.setObjectName(u"auto_start_all_apps_combo")
        self.auto_start_all_apps_combo.setMinimumSize(QSize(130, 0))

        self.horizontalLayout_11.addWidget(self.auto_start_all_apps_combo)


        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.save_button = QPushButton(SettingsForm)
        self.save_button.setObjectName(u"save_button")

        self.horizontalLayout.addWidget(self.save_button)

        self.close_button = QPushButton(SettingsForm)
        self.close_button.setObjectName(u"close_button")

        self.horizontalLayout.addWidget(self.close_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.horizontalLayout_6.addLayout(self.verticalLayout_2)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_6)


        self.retranslateUi(SettingsForm)

        QMetaObject.connectSlotsByName(SettingsForm)
    # setupUi

    def retranslateUi(self, SettingsForm):
        SettingsForm.setWindowTitle(QCoreApplication.translate("SettingsForm", u"Settings", None))
        self.r10_settings_groupbox_2.setTitle(QCoreApplication.translate("SettingsForm", u"GSPro", None))
#if QT_CONFIG(tooltip)
        self.ipaddress_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"GSPro IP Address", None))
#endif // QT_CONFIG(tooltip)
        self.ipaddress_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro IP Address", None))
#if QT_CONFIG(tooltip)
        self.gspro_window_name.setToolTip(QCoreApplication.translate("SettingsForm", u"GSPro Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.gspro_window_name.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro Window Title", None))
#if QT_CONFIG(tooltip)
        self.port_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"GSPro Port", None))
#endif // QT_CONFIG(tooltip)
        self.port_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro Port", None))
#if QT_CONFIG(tooltip)
        self.gspro_api_window_name.setToolTip(QCoreApplication.translate("SettingsForm", u"GSPro API Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.gspro_api_window_name.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro API Window Title", None))
#if QT_CONFIG(tooltip)
        self.gspro_path_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Application Path(Opyional)", None))
#endif // QT_CONFIG(tooltip)
        self.gspro_path_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"GSPro Path", None))
        self.file_browse_button.setText(QCoreApplication.translate("SettingsForm", u"Browse", None))
        self.label_6.setText(QCoreApplication.translate("SettingsForm", u"Launch Monitor", None))
        self.launch_monitor_combo.setItemText(0, QCoreApplication.translate("SettingsForm", u"None", None))
        self.launch_monitor_combo.setItemText(1, QCoreApplication.translate("SettingsForm", u"New Item", None))

        self.r10_settings_groupbox.setTitle(QCoreApplication.translate("SettingsForm", u"R10 BT Settings", None))
#if QT_CONFIG(tooltip)
        self.r10_settings_device_name_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Device Name", None))
#endif // QT_CONFIG(tooltip)
        self.r10_settings_device_name_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Device Name", None))
#if QT_CONFIG(tooltip)
        self.r10_settings_humidity_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Humidity (percent (0 - 1)", None))
#endif // QT_CONFIG(tooltip)
        self.r10_settings_humidity_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Humidity (percent (0 - 1)", None))
#if QT_CONFIG(tooltip)
        self.r10_settings_temperature_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Temperature (fahrenheit )", None))
#endif // QT_CONFIG(tooltip)
        self.r10_settings_temperature_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Temperature (fahrenheit )", None))
#if QT_CONFIG(tooltip)
        self.r10_settings_altitude_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Altitude (feet)", None))
#endif // QT_CONFIG(tooltip)
        self.r10_settings_altitude_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Altitude (feet)", None))
#if QT_CONFIG(tooltip)
        self.r10_settings_airdensity_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Air Density (kg/m^3)", None))
#endif // QT_CONFIG(tooltip)
        self.r10_settings_airdensity_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Air Density (kg/m^3)", None))
#if QT_CONFIG(tooltip)
        self.r10_settings_tee_distance_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Tee Distance to R10 (feet)", None))
#endif // QT_CONFIG(tooltip)
        self.r10_settings_tee_distance_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Tee Distance to R10 (feet)", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsForm", u"Relay Server Settings", None))
#if QT_CONFIG(tooltip)
        self.relay_server_ip_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Relay Server IP Address", None))
#endif // QT_CONFIG(tooltip)
        self.relay_server_ip_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Relay Server IP Address", None))
#if QT_CONFIG(tooltip)
        self.relay_server_port_edit.setToolTip(QCoreApplication.translate("SettingsForm", u"Relay Server Port", None))
#endif // QT_CONFIG(tooltip)
        self.relay_server_port_edit.setPlaceholderText(QCoreApplication.translate("SettingsForm", u"Relay Server Port", None))
        self.label_7.setText(QCoreApplication.translate("SettingsForm", u"Default OCR Device ", None))
        self.default_device_combo.setItemText(0, QCoreApplication.translate("SettingsForm", u"None", None))
        self.default_device_combo.setItemText(1, QCoreApplication.translate("SettingsForm", u"New Item", None))

        self.auto_start_all_label.setText(QCoreApplication.translate("SettingsForm", u"Auto Start All Apps", None))
        self.auto_start_all_apps_combo.setItemText(0, QCoreApplication.translate("SettingsForm", u"None", None))
        self.auto_start_all_apps_combo.setItemText(1, QCoreApplication.translate("SettingsForm", u"New Item", None))

#if QT_CONFIG(tooltip)
        self.save_button.setToolTip(QCoreApplication.translate("SettingsForm", u"New Device", None))
#endif // QT_CONFIG(tooltip)
        self.save_button.setText(QCoreApplication.translate("SettingsForm", u"Save", None))
#if QT_CONFIG(tooltip)
        self.close_button.setToolTip(QCoreApplication.translate("SettingsForm", u"New Device", None))
#endif // QT_CONFIG(tooltip)
        self.close_button.setText(QCoreApplication.translate("SettingsForm", u"Close", None))
    # retranslateUi

