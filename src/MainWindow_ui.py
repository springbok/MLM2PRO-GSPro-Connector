# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QToolBar, QVBoxLayout, QWidget)
import src.resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1193, 642)
        icon = QIcon()
        icon.addFile(u":/ico/ico/connect.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(6.000000000000000)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon1 = QIcon()
        icon1.addFile(u":/ico/ico/exit.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.actionExit.setIcon(icon1)
        self.actionDevices = QAction(MainWindow)
        self.actionDevices.setObjectName(u"actionDevices")
        icon2 = QIcon()
        icon2.addFile(u":/ico/ico/devices.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDevices.setIcon(icon2)
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        icon3 = QIcon()
        icon3.addFile(u":/ico/ico/settings.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSettings.setIcon(icon3)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon4 = QIcon()
        icon4.addFile(u":/ico/ico/about.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAbout.setIcon(icon4)
        self.actionPuttingSettings = QAction(MainWindow)
        self.actionPuttingSettings.setObjectName(u"actionPuttingSettings")
        icon5 = QIcon()
        icon5.addFile(u":/ico/ico/Iconsmind-Outline-Golf-2.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.actionPuttingSettings.setIcon(icon5)
        self.actionDonate = QAction(MainWindow)
        self.actionDonate.setObjectName(u"actionDonate")
        icon6 = QIcon()
        icon6.addFile(u":/ico/ico/nav-logo-stroke.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDonate.setIcon(icon6)
        self.actionShop = QAction(MainWindow)
        self.actionShop.setObjectName(u"actionShop")
        icon7 = QIcon()
        icon7.addFile(u":/ico/ico/store_2838968.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionShop.setIcon(icon7)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.main_tab = QTabWidget(self.centralwidget)
        self.main_tab.setObjectName(u"main_tab")
        self.connector_tab = QWidget()
        self.connector_tab.setObjectName(u"connector_tab")
        self.verticalLayout_7 = QVBoxLayout(self.connector_tab)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setSizeConstraint(QLayout.SetFixedSize)
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.groupBox = QGroupBox(self.connector_tab)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gspro_connect_button = QPushButton(self.groupBox)
        self.gspro_connect_button.setObjectName(u"gspro_connect_button")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gspro_connect_button.sizePolicy().hasHeightForWidth())
        self.gspro_connect_button.setSizePolicy(sizePolicy)
        self.gspro_connect_button.setMaximumSize(QSize(200, 30))

        self.verticalLayout.addWidget(self.gspro_connect_button)

        self.gspro_status_label = QLabel(self.groupBox)
        self.gspro_status_label.setObjectName(u"gspro_status_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.gspro_status_label.sizePolicy().hasHeightForWidth())
        self.gspro_status_label.setSizePolicy(sizePolicy1)
        self.gspro_status_label.setMinimumSize(QSize(120, 0))
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        self.gspro_status_label.setFont(font)
        self.gspro_status_label.setAlignment(Qt.AlignCenter)
        self.gspro_status_label.setMargin(5)

        self.verticalLayout.addWidget(self.gspro_status_label)

        self.club_selection = QLabel(self.groupBox)
        self.club_selection.setObjectName(u"club_selection")
        sizePolicy1.setHeightForWidth(self.club_selection.sizePolicy().hasHeightForWidth())
        self.club_selection.setSizePolicy(sizePolicy1)
        self.club_selection.setMinimumSize(QSize(120, 0))
        self.club_selection.setFont(font)
        self.club_selection.setAlignment(Qt.AlignCenter)
        self.club_selection.setMargin(5)

        self.verticalLayout.addWidget(self.club_selection)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.horizontalLayout_8.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(self.connector_tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.putting_server_button = QPushButton(self.groupBox_3)
        self.putting_server_button.setObjectName(u"putting_server_button")
        sizePolicy.setHeightForWidth(self.putting_server_button.sizePolicy().hasHeightForWidth())
        self.putting_server_button.setSizePolicy(sizePolicy)
        self.putting_server_button.setMaximumSize(QSize(200, 30))

        self.verticalLayout_2.addWidget(self.putting_server_button)

        self.putting_system_label = QLabel(self.groupBox_3)
        self.putting_system_label.setObjectName(u"putting_system_label")
        sizePolicy1.setHeightForWidth(self.putting_system_label.sizePolicy().hasHeightForWidth())
        self.putting_system_label.setSizePolicy(sizePolicy1)
        self.putting_system_label.setMinimumSize(QSize(120, 0))
        self.putting_system_label.setFont(font)
        self.putting_system_label.setAlignment(Qt.AlignCenter)
        self.putting_system_label.setMargin(5)

        self.verticalLayout_2.addWidget(self.putting_system_label)

        self.putting_server_status_label = QLabel(self.groupBox_3)
        self.putting_server_status_label.setObjectName(u"putting_server_status_label")
        sizePolicy1.setHeightForWidth(self.putting_server_status_label.sizePolicy().hasHeightForWidth())
        self.putting_server_status_label.setSizePolicy(sizePolicy1)
        self.putting_server_status_label.setMinimumSize(QSize(120, 0))
        self.putting_server_status_label.setFont(font)
        self.putting_server_status_label.setAlignment(Qt.AlignCenter)
        self.putting_server_status_label.setMargin(5)

        self.verticalLayout_2.addWidget(self.putting_server_status_label)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.horizontalLayout_8.addWidget(self.groupBox_3)

        self.launch_monitor_groupbox = QGroupBox(self.connector_tab)
        self.launch_monitor_groupbox.setObjectName(u"launch_monitor_groupbox")
        self.horizontalLayout_13 = QHBoxLayout(self.launch_monitor_groupbox)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.device_control_widget = QWidget(self.launch_monitor_groupbox)
        self.device_control_widget.setObjectName(u"device_control_widget")
        self.verticalLayout_8 = QVBoxLayout(self.device_control_widget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.select_device_button = QPushButton(self.device_control_widget)
        self.select_device_button.setObjectName(u"select_device_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.select_device_button.sizePolicy().hasHeightForWidth())
        self.select_device_button.setSizePolicy(sizePolicy2)
        self.select_device_button.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_8.addWidget(self.select_device_button)

        self.selected_device = QLabel(self.device_control_widget)
        self.selected_device.setObjectName(u"selected_device")
        font1 = QFont()
        font1.setPointSize(12)
        self.selected_device.setFont(font1)
        self.selected_device.setAlignment(Qt.AlignCenter)
        self.selected_device.setMargin(5)

        self.verticalLayout_8.addWidget(self.selected_device)

        self.selected_mirror_app = QLabel(self.device_control_widget)
        self.selected_mirror_app.setObjectName(u"selected_mirror_app")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.selected_mirror_app.sizePolicy().hasHeightForWidth())
        self.selected_mirror_app.setSizePolicy(sizePolicy3)
        self.selected_mirror_app.setMinimumSize(QSize(0, 0))
        self.selected_mirror_app.setFont(font)
        self.selected_mirror_app.setAlignment(Qt.AlignCenter)
        self.selected_mirror_app.setMargin(5)

        self.verticalLayout_8.addWidget(self.selected_mirror_app)

        self.connector_status = QLabel(self.device_control_widget)
        self.connector_status.setObjectName(u"connector_status")
        self.connector_status.setFont(font1)
        self.connector_status.setAlignment(Qt.AlignCenter)
        self.connector_status.setMargin(5)

        self.verticalLayout_8.addWidget(self.connector_status)

        self.pause_button = QPushButton(self.device_control_widget)
        self.pause_button.setObjectName(u"pause_button")

        self.verticalLayout_8.addWidget(self.pause_button)

        self.restart_button = QPushButton(self.device_control_widget)
        self.restart_button.setObjectName(u"restart_button")

        self.verticalLayout_8.addWidget(self.restart_button)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_4)


        self.horizontalLayout_12.addWidget(self.device_control_widget)

        self.server_control_widget = QWidget(self.launch_monitor_groupbox)
        self.server_control_widget.setObjectName(u"server_control_widget")
        self.verticalLayout_12 = QVBoxLayout(self.server_control_widget)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.start_server_button = QPushButton(self.server_control_widget)
        self.start_server_button.setObjectName(u"start_server_button")
        sizePolicy2.setHeightForWidth(self.start_server_button.sizePolicy().hasHeightForWidth())
        self.start_server_button.setSizePolicy(sizePolicy2)
        self.start_server_button.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_12.addWidget(self.start_server_button)

        self.server_status = QLabel(self.server_control_widget)
        self.server_status.setObjectName(u"server_status")
        self.server_status.setFont(font1)
        self.server_status.setAlignment(Qt.AlignCenter)
        self.server_status.setMargin(5)

        self.verticalLayout_12.addWidget(self.server_status)

        self.server_connection = QLabel(self.server_control_widget)
        self.server_connection.setObjectName(u"server_connection")
        sizePolicy3.setHeightForWidth(self.server_connection.sizePolicy().hasHeightForWidth())
        self.server_connection.setSizePolicy(sizePolicy3)
        self.server_connection.setMinimumSize(QSize(0, 0))
        self.server_connection.setFont(font)
        self.server_connection.setAlignment(Qt.AlignCenter)
        self.server_connection.setMargin(5)

        self.verticalLayout_12.addWidget(self.server_connection)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_7)


        self.horizontalLayout_12.addWidget(self.server_control_widget)

        self.line = QFrame(self.launch_monitor_groupbox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_12.addWidget(self.line)

        self.edit_field_layout = QVBoxLayout()
        self.edit_field_layout.setObjectName(u"edit_field_layout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setSizeConstraint(QLayout.SetFixedSize)

        self.edit_field_layout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.label_2 = QLabel(self.launch_monitor_groupbox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.label_3 = QLabel(self.launch_monitor_groupbox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.label = QLabel(self.launch_monitor_groupbox)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label)

        self.label_4 = QLabel(self.launch_monitor_groupbox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_4)

        self.label_6 = QLabel(self.launch_monitor_groupbox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font1)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_6)


        self.edit_field_layout.addLayout(self.horizontalLayout_2)

        self.edit_field_layout1 = QHBoxLayout()
        self.edit_field_layout1.setObjectName(u"edit_field_layout1")
        self.edit_field_layout1.setSizeConstraint(QLayout.SetFixedSize)
        self.speed_edit = QTextEdit(self.launch_monitor_groupbox)
        self.speed_edit.setObjectName(u"speed_edit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.speed_edit.sizePolicy().hasHeightForWidth())
        self.speed_edit.setSizePolicy(sizePolicy4)
        self.speed_edit.setMaximumSize(QSize(230, 50))
        font2 = QFont()
        font2.setPointSize(14)
        self.speed_edit.setFont(font2)

        self.edit_field_layout1.addWidget(self.speed_edit)

        self.spin_axis_edit = QTextEdit(self.launch_monitor_groupbox)
        self.spin_axis_edit.setObjectName(u"spin_axis_edit")
        sizePolicy4.setHeightForWidth(self.spin_axis_edit.sizePolicy().hasHeightForWidth())
        self.spin_axis_edit.setSizePolicy(sizePolicy4)
        self.spin_axis_edit.setMaximumSize(QSize(230, 50))
        self.spin_axis_edit.setFont(font2)

        self.edit_field_layout1.addWidget(self.spin_axis_edit)

        self.total_spin_edit = QTextEdit(self.launch_monitor_groupbox)
        self.total_spin_edit.setObjectName(u"total_spin_edit")
        sizePolicy4.setHeightForWidth(self.total_spin_edit.sizePolicy().hasHeightForWidth())
        self.total_spin_edit.setSizePolicy(sizePolicy4)
        self.total_spin_edit.setMaximumSize(QSize(230, 50))
        self.total_spin_edit.setFont(font2)

        self.edit_field_layout1.addWidget(self.total_spin_edit)

        self.hla_edit = QTextEdit(self.launch_monitor_groupbox)
        self.hla_edit.setObjectName(u"hla_edit")
        sizePolicy4.setHeightForWidth(self.hla_edit.sizePolicy().hasHeightForWidth())
        self.hla_edit.setSizePolicy(sizePolicy4)
        self.hla_edit.setMaximumSize(QSize(230, 50))
        self.hla_edit.setFont(font2)

        self.edit_field_layout1.addWidget(self.hla_edit)

        self.path_edit = QTextEdit(self.launch_monitor_groupbox)
        self.path_edit.setObjectName(u"path_edit")
        sizePolicy4.setHeightForWidth(self.path_edit.sizePolicy().hasHeightForWidth())
        self.path_edit.setSizePolicy(sizePolicy4)
        self.path_edit.setMaximumSize(QSize(230, 50))
        self.path_edit.setFont(font2)

        self.edit_field_layout1.addWidget(self.path_edit)


        self.edit_field_layout.addLayout(self.edit_field_layout1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setSizeConstraint(QLayout.SetFixedSize)
        self.label_7 = QLabel(self.launch_monitor_groupbox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font1)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.label_7)

        self.label_8 = QLabel(self.launch_monitor_groupbox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font1)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.label_8)

        self.label_5 = QLabel(self.launch_monitor_groupbox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.label_5)

        self.SideSpin = QLabel(self.launch_monitor_groupbox)
        self.SideSpin.setObjectName(u"SideSpin")
        self.SideSpin.setFont(font1)
        self.SideSpin.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.SideSpin)

        self.SideSpin_2 = QLabel(self.launch_monitor_groupbox)
        self.SideSpin_2.setObjectName(u"SideSpin_2")
        self.SideSpin_2.setFont(font1)
        self.SideSpin_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_5.addWidget(self.SideSpin_2)


        self.edit_field_layout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setSizeConstraint(QLayout.SetFixedSize)
        self.vla_edit = QTextEdit(self.launch_monitor_groupbox)
        self.vla_edit.setObjectName(u"vla_edit")
        sizePolicy4.setHeightForWidth(self.vla_edit.sizePolicy().hasHeightForWidth())
        self.vla_edit.setSizePolicy(sizePolicy4)
        self.vla_edit.setMaximumSize(QSize(230, 50))
        self.vla_edit.setFont(font2)

        self.horizontalLayout_6.addWidget(self.vla_edit)

        self.club_speed_edit = QTextEdit(self.launch_monitor_groupbox)
        self.club_speed_edit.setObjectName(u"club_speed_edit")
        sizePolicy4.setHeightForWidth(self.club_speed_edit.sizePolicy().hasHeightForWidth())
        self.club_speed_edit.setSizePolicy(sizePolicy4)
        self.club_speed_edit.setMaximumSize(QSize(230, 50))
        self.club_speed_edit.setFont(font2)

        self.horizontalLayout_6.addWidget(self.club_speed_edit)

        self.back_spin_edit = QTextEdit(self.launch_monitor_groupbox)
        self.back_spin_edit.setObjectName(u"back_spin_edit")
        sizePolicy4.setHeightForWidth(self.back_spin_edit.sizePolicy().hasHeightForWidth())
        self.back_spin_edit.setSizePolicy(sizePolicy4)
        self.back_spin_edit.setMaximumSize(QSize(230, 50))
        self.back_spin_edit.setFont(font2)

        self.horizontalLayout_6.addWidget(self.back_spin_edit)

        self.side_spin_edit = QTextEdit(self.launch_monitor_groupbox)
        self.side_spin_edit.setObjectName(u"side_spin_edit")
        sizePolicy4.setHeightForWidth(self.side_spin_edit.sizePolicy().hasHeightForWidth())
        self.side_spin_edit.setSizePolicy(sizePolicy4)
        self.side_spin_edit.setMaximumSize(QSize(230, 50))
        self.side_spin_edit.setFont(font2)

        self.horizontalLayout_6.addWidget(self.side_spin_edit)

        self.face_to_target_edit = QTextEdit(self.launch_monitor_groupbox)
        self.face_to_target_edit.setObjectName(u"face_to_target_edit")
        sizePolicy4.setHeightForWidth(self.face_to_target_edit.sizePolicy().hasHeightForWidth())
        self.face_to_target_edit.setSizePolicy(sizePolicy4)
        self.face_to_target_edit.setMaximumSize(QSize(230, 50))
        self.face_to_target_edit.setFont(font2)

        self.horizontalLayout_6.addWidget(self.face_to_target_edit)


        self.edit_field_layout.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_12.addLayout(self.edit_field_layout)


        self.horizontalLayout_13.addLayout(self.horizontalLayout_12)


        self.horizontalLayout_8.addWidget(self.launch_monitor_groupbox)

        self.horizontalLayout_8.setStretch(2, 2)

        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.shot_history_table = QTableWidget(self.connector_tab)
        self.shot_history_table.setObjectName(u"shot_history_table")
        self.shot_history_table.setWordWrap(False)

        self.verticalLayout_3.addWidget(self.shot_history_table)


        self.verticalLayout_5.addLayout(self.verticalLayout_3)

        self.verticalLayout_5.setStretch(1, 2)

        self.verticalLayout_7.addLayout(self.verticalLayout_5)

        self.main_tab.addTab(self.connector_tab, "")
        self.log_tab = QWidget()
        self.log_tab.setObjectName(u"log_tab")
        self.verticalLayout_9 = QVBoxLayout(self.log_tab)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.log_table = QTableWidget(self.log_tab)
        if (self.log_table.columnCount() < 3):
            self.log_table.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.log_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.log_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.log_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.log_table.setObjectName(u"log_table")
        self.log_table.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.log_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
        self.log_table.setWordWrap(False)

        self.verticalLayout_9.addWidget(self.log_table)

        self.main_tab.addTab(self.log_tab, "")

        self.horizontalLayout_4.addWidget(self.main_tab)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionExit)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionDevices)
        self.toolBar.addAction(self.actionSettings)
        self.toolBar.addAction(self.actionPuttingSettings)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionDonate)
        self.toolBar.addAction(self.actionShop)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.main_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MLM2PRO-GSPro-Connect", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionDevices.setText(QCoreApplication.translate("MainWindow", u"Devices", None))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.actionSettings.setToolTip(QCoreApplication.translate("MainWindow", u"Settings", None))
#endif // QT_CONFIG(tooltip)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionPuttingSettings.setText(QCoreApplication.translate("MainWindow", u"Putting Settings", None))
#if QT_CONFIG(tooltip)
        self.actionPuttingSettings.setToolTip(QCoreApplication.translate("MainWindow", u"Putting Settings", None))
#endif // QT_CONFIG(tooltip)
        self.actionDonate.setText(QCoreApplication.translate("MainWindow", u"Donate", None))
#if QT_CONFIG(tooltip)
        self.actionDonate.setToolTip(QCoreApplication.translate("MainWindow", u"Donate", None))
#endif // QT_CONFIG(tooltip)
        self.actionShop.setText(QCoreApplication.translate("MainWindow", u"Shop", None))
#if QT_CONFIG(tooltip)
        self.actionShop.setToolTip(QCoreApplication.translate("MainWindow", u"Shop", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.connector_tab.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"GSPro Connection", None))
        self.gspro_connect_button.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.gspro_status_label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.club_selection.setText("")
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Putting", None))
        self.putting_server_button.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.putting_system_label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.putting_server_status_label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.launch_monitor_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Launch Monitor", None))
        self.select_device_button.setText(QCoreApplication.translate("MainWindow", u"Device", None))
        self.selected_device.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.selected_mirror_app.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.connector_status.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pause_button.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.restart_button.setText(QCoreApplication.translate("MainWindow", u"Restart", None))
        self.start_server_button.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.server_status.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.server_connection.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Ball Speed", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Spin Axis", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Spin Rate", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Launch Dir (HLA)", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Path", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Launch Angle (VLA)", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Club Speed", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Back Spin", None))
        self.SideSpin.setText(QCoreApplication.translate("MainWindow", u"Side Spin", None))
        self.SideSpin_2.setText(QCoreApplication.translate("MainWindow", u"Face to Target", None))
        self.main_tab.setTabText(self.main_tab.indexOf(self.connector_tab), QCoreApplication.translate("MainWindow", u"Connector", None))
        ___qtablewidgetitem = self.log_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Date", None));
        ___qtablewidgetitem1 = self.log_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"System", None));
        ___qtablewidgetitem2 = self.log_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Message", None));
        self.main_tab.setTabText(self.main_tab.indexOf(self.log_tab), QCoreApplication.translate("MainWindow", u"Log", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

