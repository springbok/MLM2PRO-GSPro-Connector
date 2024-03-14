# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DevicesForm.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLayout,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_DevicesForm(object):
    def setupUi(self, DevicesForm):
        if not DevicesForm.objectName():
            DevicesForm.setObjectName(u"DevicesForm")
        DevicesForm.setWindowModality(Qt.ApplicationModal)
        DevicesForm.resize(863, 471)
        DevicesForm.setLayoutDirection(Qt.LeftToRight)
        self.horizontalLayout_5 = QHBoxLayout(DevicesForm)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.devices_table = QTableWidget(DevicesForm)
        if (self.devices_table.columnCount() < 3):
            self.devices_table.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.devices_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.devices_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.devices_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.devices_table.setObjectName(u"devices_table")
        self.devices_table.setMinimumSize(QSize(200, 369))
        self.devices_table.verticalHeader().setStretchLastSection(False)

        self.verticalLayout.addWidget(self.devices_table)


        self.horizontalLayout_5.addLayout(self.verticalLayout)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setSizeConstraint(QLayout.SetNoConstraint)
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.name_edit = QPlainTextEdit(DevicesForm)
        self.name_edit.setObjectName(u"name_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_edit.sizePolicy().hasHeightForWidth())
        self.name_edit.setSizePolicy(sizePolicy)
        self.name_edit.setMaximumSize(QSize(16777215, 31))
        self.name_edit.setTabChangesFocus(True)

        self.verticalLayout_8.addWidget(self.name_edit)

        self.window_title_edit = QPlainTextEdit(DevicesForm)
        self.window_title_edit.setObjectName(u"window_title_edit")
        sizePolicy.setHeightForWidth(self.window_title_edit.sizePolicy().hasHeightForWidth())
        self.window_title_edit.setSizePolicy(sizePolicy)
        self.window_title_edit.setMaximumSize(QSize(16777215, 31))
        self.window_title_edit.setTabChangesFocus(True)

        self.verticalLayout_8.addWidget(self.window_title_edit)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.path_edit = QPlainTextEdit(DevicesForm)
        self.path_edit.setObjectName(u"path_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.path_edit.sizePolicy().hasHeightForWidth())
        self.path_edit.setSizePolicy(sizePolicy1)
        self.path_edit.setMaximumSize(QSize(16777215, 31))

        self.horizontalLayout.addWidget(self.path_edit)

        self.file_browse_button = QPushButton(DevicesForm)
        self.file_browse_button.setObjectName(u"file_browse_button")

        self.horizontalLayout.addWidget(self.file_browse_button)


        self.verticalLayout_8.addLayout(self.horizontalLayout)


        self.verticalLayout_10.addLayout(self.verticalLayout_8)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 5, -1, -1)
        self.save_button = QPushButton(DevicesForm)
        self.save_button.setObjectName(u"save_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.save_button.sizePolicy().hasHeightForWidth())
        self.save_button.setSizePolicy(sizePolicy2)
        self.save_button.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_4.addWidget(self.save_button)

        self.new_button = QPushButton(DevicesForm)
        self.new_button.setObjectName(u"new_button")
        sizePolicy2.setHeightForWidth(self.new_button.sizePolicy().hasHeightForWidth())
        self.new_button.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.new_button)

        self.delete_button = QPushButton(DevicesForm)
        self.delete_button.setObjectName(u"delete_button")
        sizePolicy2.setHeightForWidth(self.delete_button.sizePolicy().hasHeightForWidth())
        self.delete_button.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.delete_button)


        self.verticalLayout_10.addLayout(self.horizontalLayout_4)

        self.open_windows_title_button = QPushButton(DevicesForm)
        self.open_windows_title_button.setObjectName(u"open_windows_title_button")

        self.verticalLayout_10.addWidget(self.open_windows_title_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)

        self.current_row_edit = QTextEdit(DevicesForm)
        self.current_row_edit.setObjectName(u"current_row_edit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.current_row_edit.sizePolicy().hasHeightForWidth())
        self.current_row_edit.setSizePolicy(sizePolicy3)
        self.current_row_edit.setMaximumSize(QSize(200, 30))

        self.verticalLayout_10.addWidget(self.current_row_edit)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.close_button = QPushButton(DevicesForm)
        self.close_button.setObjectName(u"close_button")
        sizePolicy2.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy2)

        self.verticalLayout_11.addWidget(self.close_button)


        self.verticalLayout_10.addLayout(self.verticalLayout_11)


        self.horizontalLayout_5.addLayout(self.verticalLayout_10)

        self.horizontalLayout_5.setStretch(0, 1)

        self.retranslateUi(DevicesForm)

        QMetaObject.connectSlotsByName(DevicesForm)
    # setupUi

    def retranslateUi(self, DevicesForm):
        DevicesForm.setWindowTitle(QCoreApplication.translate("DevicesForm", u"Devices", None))
        ___qtablewidgetitem = self.devices_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DevicesForm", u"Name", None));
        ___qtablewidgetitem1 = self.devices_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DevicesForm", u"Window Name", None));
        ___qtablewidgetitem2 = self.devices_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DevicesForm", u"Path", None));
#if QT_CONFIG(tooltip)
        self.name_edit.setToolTip(QCoreApplication.translate("DevicesForm", u"Name", None))
#endif // QT_CONFIG(tooltip)
        self.name_edit.setPlaceholderText(QCoreApplication.translate("DevicesForm", u"Name", None))
#if QT_CONFIG(tooltip)
        self.window_title_edit.setToolTip(QCoreApplication.translate("DevicesForm", u"Window Title", None))
#endif // QT_CONFIG(tooltip)
        self.window_title_edit.setPlaceholderText(QCoreApplication.translate("DevicesForm", u"Window Title", None))
#if QT_CONFIG(tooltip)
        self.path_edit.setToolTip(QCoreApplication.translate("DevicesForm", u"Application Path(Opyional)", None))
#endif // QT_CONFIG(tooltip)
        self.path_edit.setPlaceholderText(QCoreApplication.translate("DevicesForm", u"Mirror Application Path", None))
        self.file_browse_button.setText(QCoreApplication.translate("DevicesForm", u"Browse", None))
#if QT_CONFIG(tooltip)
        self.save_button.setToolTip(QCoreApplication.translate("DevicesForm", u"Save Changes", None))
#endif // QT_CONFIG(tooltip)
        self.save_button.setText(QCoreApplication.translate("DevicesForm", u"Save", None))
#if QT_CONFIG(tooltip)
        self.new_button.setToolTip(QCoreApplication.translate("DevicesForm", u"New Device", None))
#endif // QT_CONFIG(tooltip)
        self.new_button.setText(QCoreApplication.translate("DevicesForm", u"New", None))
#if QT_CONFIG(tooltip)
        self.delete_button.setToolTip(QCoreApplication.translate("DevicesForm", u"Delete Device", None))
#endif // QT_CONFIG(tooltip)
        self.delete_button.setText(QCoreApplication.translate("DevicesForm", u"Delete", None))
        self.open_windows_title_button.setText(QCoreApplication.translate("DevicesForm", u"Display Window Title of all open Windows", None))
#if QT_CONFIG(tooltip)
        self.close_button.setToolTip(QCoreApplication.translate("DevicesForm", u"Close Form", None))
#endif // QT_CONFIG(tooltip)
        self.close_button.setText(QCoreApplication.translate("DevicesForm", u"Close", None))
    # retranslateUi

