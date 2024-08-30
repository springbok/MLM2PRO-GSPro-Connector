# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PuttingForm.ui'
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

class Ui_PuttingForm(object):
    def setupUi(self, PuttingForm):
        if not PuttingForm.objectName():
            PuttingForm.setObjectName(u"PuttingForm")
        PuttingForm.setWindowModality(Qt.ApplicationModal)
        PuttingForm.resize(446, 597)
        self.verticalLayout_6 = QVBoxLayout(PuttingForm)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setSizeConstraint(QLayout.SetNoConstraint)
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(PuttingForm)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.putting_system_combo = QComboBox(PuttingForm)
        self.putting_system_combo.addItem("")
        self.putting_system_combo.addItem("")
        self.putting_system_combo.setObjectName(u"putting_system_combo")

        self.horizontalLayout_3.addWidget(self.putting_system_combo)


        self.verticalLayout_8.addLayout(self.horizontalLayout_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(PuttingForm)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_10.addWidget(self.label_6)

        self.exputt_camera_auto_start_combo = QComboBox(self.groupBox)
        self.exputt_camera_auto_start_combo.addItem("")
        self.exputt_camera_auto_start_combo.addItem("")
        self.exputt_camera_auto_start_combo.setObjectName(u"exputt_camera_auto_start_combo")

        self.horizontalLayout_10.addWidget(self.exputt_camera_auto_start_combo)


        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_11.addWidget(self.label_8)

        self.exputt_camera_window_title_edit = QPlainTextEdit(self.groupBox)
        self.exputt_camera_window_title_edit.setObjectName(u"exputt_camera_window_title_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exputt_camera_window_title_edit.sizePolicy().hasHeightForWidth())
        self.exputt_camera_window_title_edit.setSizePolicy(sizePolicy)
        self.exputt_camera_window_title_edit.setMaximumSize(QSize(16777215, 31))
        self.exputt_camera_window_title_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.exputt_camera_window_title_edit.setTabChangesFocus(True)
        self.exputt_camera_window_title_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.horizontalLayout_11.addWidget(self.exputt_camera_window_title_edit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_11)

        self.rois_button = QPushButton(self.groupBox)
        self.rois_button.setObjectName(u"rois_button")

        self.verticalLayout_3.addWidget(self.rois_button)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(PuttingForm)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.webcam_camera_combo = QComboBox(self.groupBox_2)
        self.webcam_camera_combo.addItem("")
        self.webcam_camera_combo.addItem("")
        self.webcam_camera_combo.setObjectName(u"webcam_camera_combo")

        self.horizontalLayout_4.addWidget(self.webcam_camera_combo)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.webcam_ball_color_combo = QComboBox(self.groupBox_2)
        self.webcam_ball_color_combo.addItem("")
        self.webcam_ball_color_combo.addItem("")
        self.webcam_ball_color_combo.setObjectName(u"webcam_ball_color_combo")

        self.horizontalLayout_5.addWidget(self.webcam_ball_color_combo)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.webcam_window_width_label = QLabel(self.groupBox_2)
        self.webcam_window_width_label.setObjectName(u"webcam_window_width_label")

        self.horizontalLayout_12.addWidget(self.webcam_window_width_label)

        self.webcam_putting_width_edit = QPlainTextEdit(self.groupBox_2)
        self.webcam_putting_width_edit.setObjectName(u"webcam_putting_width_edit")
        sizePolicy.setHeightForWidth(self.webcam_putting_width_edit.sizePolicy().hasHeightForWidth())
        self.webcam_putting_width_edit.setSizePolicy(sizePolicy)
        self.webcam_putting_width_edit.setMaximumSize(QSize(16777215, 31))
        self.webcam_putting_width_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.webcam_putting_width_edit.setTabChangesFocus(True)
        self.webcam_putting_width_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.horizontalLayout_12.addWidget(self.webcam_putting_width_edit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.webcam_auto_start_combo = QComboBox(self.groupBox_2)
        self.webcam_auto_start_combo.addItem("")
        self.webcam_auto_start_combo.addItem("")
        self.webcam_auto_start_combo.setObjectName(u"webcam_auto_start_combo")

        self.horizontalLayout_7.addWidget(self.webcam_auto_start_combo)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.ball_tracking_app_params_label = QLabel(self.groupBox_2)
        self.ball_tracking_app_params_label.setObjectName(u"ball_tracking_app_params_label")

        self.horizontalLayout_8.addWidget(self.ball_tracking_app_params_label)

        self.ball_tracking_app_params_edit = QPlainTextEdit(self.groupBox_2)
        self.ball_tracking_app_params_edit.setObjectName(u"ball_tracking_app_params_edit")
        sizePolicy.setHeightForWidth(self.ball_tracking_app_params_edit.sizePolicy().hasHeightForWidth())
        self.ball_tracking_app_params_edit.setSizePolicy(sizePolicy)
        self.ball_tracking_app_params_edit.setMaximumSize(QSize(16777215, 31))
        self.ball_tracking_app_params_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ball_tracking_app_params_edit.setTabChangesFocus(True)
        self.ball_tracking_app_params_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.horizontalLayout_8.addWidget(self.ball_tracking_app_params_edit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_9.addWidget(self.label_7)

        self.webcam_window_title_edit = QPlainTextEdit(self.groupBox_2)
        self.webcam_window_title_edit.setObjectName(u"webcam_window_title_edit")
        sizePolicy.setHeightForWidth(self.webcam_window_title_edit.sizePolicy().hasHeightForWidth())
        self.webcam_window_title_edit.setSizePolicy(sizePolicy)
        self.webcam_window_title_edit.setMaximumSize(QSize(16777215, 31))
        self.webcam_window_title_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.webcam_window_title_edit.setTabChangesFocus(True)
        self.webcam_window_title_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.horizontalLayout_9.addWidget(self.webcam_window_title_edit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.groupBox_3 = QGroupBox(self.groupBox_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_13.addWidget(self.label_9)

        self.webcam_putting_focus_combo = QComboBox(self.groupBox_3)
        self.webcam_putting_focus_combo.addItem("")
        self.webcam_putting_focus_combo.addItem("")
        self.webcam_putting_focus_combo.setObjectName(u"webcam_putting_focus_combo")

        self.horizontalLayout_13.addWidget(self.webcam_putting_focus_combo)


        self.verticalLayout_4.addLayout(self.horizontalLayout_13)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_14.addWidget(self.label_10)

        self.webcam_not_putting_state_combo = QComboBox(self.groupBox_4)
        self.webcam_not_putting_state_combo.addItem("")
        self.webcam_not_putting_state_combo.addItem("")
        self.webcam_not_putting_state_combo.setObjectName(u"webcam_not_putting_state_combo")

        self.horizontalLayout_14.addWidget(self.webcam_not_putting_state_combo)


        self.verticalLayout_5.addLayout(self.horizontalLayout_14)


        self.verticalLayout_2.addWidget(self.groupBox_4)


        self.verticalLayout.addWidget(self.groupBox_2)


        self.verticalLayout_8.addLayout(self.verticalLayout)


        self.verticalLayout_10.addLayout(self.verticalLayout_8)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.find_video_sources_button = QPushButton(PuttingForm)
        self.find_video_sources_button.setObjectName(u"find_video_sources_button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.find_video_sources_button.sizePolicy().hasHeightForWidth())
        self.find_video_sources_button.setSizePolicy(sizePolicy1)
        self.find_video_sources_button.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_2.addWidget(self.find_video_sources_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.save_button = QPushButton(PuttingForm)
        self.save_button.setObjectName(u"save_button")
        sizePolicy1.setHeightForWidth(self.save_button.sizePolicy().hasHeightForWidth())
        self.save_button.setSizePolicy(sizePolicy1)
        self.save_button.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_2.addWidget(self.save_button)

        self.close_button = QPushButton(PuttingForm)
        self.close_button.setObjectName(u"close_button")
        sizePolicy1.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.close_button)


        self.verticalLayout_10.addLayout(self.horizontalLayout_2)


        self.verticalLayout_6.addLayout(self.verticalLayout_10)


        self.retranslateUi(PuttingForm)

        QMetaObject.connectSlotsByName(PuttingForm)
    # setupUi

    def retranslateUi(self, PuttingForm):
        PuttingForm.setWindowTitle(QCoreApplication.translate("PuttingForm", u"Putting Settings", None))
        self.label.setText(QCoreApplication.translate("PuttingForm", u"Putting System", None))
        self.putting_system_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.putting_system_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

        self.groupBox.setTitle(QCoreApplication.translate("PuttingForm", u"ExPutt Settings", None))
        self.label_6.setText(QCoreApplication.translate("PuttingForm", u"Auto start Camera App", None))
        self.exputt_camera_auto_start_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.exputt_camera_auto_start_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

        self.label_8.setText(QCoreApplication.translate("PuttingForm", u"Camera App Window Title                    ", None))
#if QT_CONFIG(tooltip)
        self.exputt_camera_window_title_edit.setToolTip(QCoreApplication.translate("PuttingForm", u"Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.exputt_camera_window_title_edit.setPlaceholderText(QCoreApplication.translate("PuttingForm", u"WindowTitle", None))
        self.rois_button.setText(QCoreApplication.translate("PuttingForm", u"ROI's", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PuttingForm", u"Webcam Settings", None))
        self.label_2.setText(QCoreApplication.translate("PuttingForm", u"Camera ID", None))
        self.webcam_camera_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.webcam_camera_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

        self.label_3.setText(QCoreApplication.translate("PuttingForm", u"Ball Color", None))
        self.webcam_ball_color_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.webcam_ball_color_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

        self.webcam_window_width_label.setText(QCoreApplication.translate("PuttingForm", u"Camera Window Width                         ", None))
#if QT_CONFIG(tooltip)
        self.webcam_putting_width_edit.setToolTip(QCoreApplication.translate("PuttingForm", u"Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.webcam_putting_width_edit.setPlaceholderText(QCoreApplication.translate("PuttingForm", u"Camera Window Width", None))
        self.label_5.setText(QCoreApplication.translate("PuttingForm", u"Auto Start Ball Tracking App", None))
        self.webcam_auto_start_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.webcam_auto_start_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

        self.ball_tracking_app_params_label.setText(QCoreApplication.translate("PuttingForm", u"Ball Tracking App Params                      ", None))
#if QT_CONFIG(tooltip)
        self.ball_tracking_app_params_edit.setToolTip(QCoreApplication.translate("PuttingForm", u"Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.ball_tracking_app_params_edit.setPlaceholderText(QCoreApplication.translate("PuttingForm", u"Ball Tracking App Params", None))
        self.label_7.setText(QCoreApplication.translate("PuttingForm", u"Ball Tracking App Window Title            ", None))
#if QT_CONFIG(tooltip)
        self.webcam_window_title_edit.setToolTip(QCoreApplication.translate("PuttingForm", u"Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.webcam_window_title_edit.setPlaceholderText(QCoreApplication.translate("PuttingForm", u"WindowTitle", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PuttingForm", u"Window Behaviour - Putting", None))
        self.label_9.setText(QCoreApplication.translate("PuttingForm", u"Set Focus To", None))
        self.webcam_putting_focus_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.webcam_putting_focus_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

        self.groupBox_4.setTitle(QCoreApplication.translate("PuttingForm", u"Window Behaviour - Not Putting", None))
        self.label_10.setText(QCoreApplication.translate("PuttingForm", u"Putting Window", None))
        self.webcam_not_putting_state_combo.setItemText(0, QCoreApplication.translate("PuttingForm", u"None", None))
        self.webcam_not_putting_state_combo.setItemText(1, QCoreApplication.translate("PuttingForm", u"New Item", None))

#if QT_CONFIG(tooltip)
        self.find_video_sources_button.setToolTip(QCoreApplication.translate("PuttingForm", u"Save Changes", None))
#endif // QT_CONFIG(tooltip)
        self.find_video_sources_button.setText(QCoreApplication.translate("PuttingForm", u"Find Video Sources", None))
#if QT_CONFIG(tooltip)
        self.save_button.setToolTip(QCoreApplication.translate("PuttingForm", u"Save Changes", None))
#endif // QT_CONFIG(tooltip)
        self.save_button.setText(QCoreApplication.translate("PuttingForm", u"Save", None))
#if QT_CONFIG(tooltip)
        self.close_button.setToolTip(QCoreApplication.translate("PuttingForm", u"Close Form", None))
#endif // QT_CONFIG(tooltip)
        self.close_button.setText(QCoreApplication.translate("PuttingForm", u"Close", None))
    # retranslateUi

