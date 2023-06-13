# -*- coding: utf-8 -*-
import os

# Form implementation generated from reading ui file 'RoverTab.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RoverTab(QtWidgets.QWidget):

    def setupUi(self, RoverTab):
        RoverTab.setObjectName("RoverTab")
        RoverTab.resize(360, 108)
        self.gridLayout = QtWidgets.QGridLayout(RoverTab)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(RoverTab)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.tRoverOBS = QtWidgets.QLineEdit(RoverTab)
        self.tRoverOBS.setObjectName("tRoverOBS")
        self.horizontalLayout.addWidget(self.tRoverOBS)
        self.btnChoseRoverOBS = QtWidgets.QToolButton(RoverTab)
        self.btnChoseRoverOBS.setObjectName("btnChoseRoverOBS")
        self.horizontalLayout.addWidget(self.btnChoseRoverOBS)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.chkRoverNAV = QtWidgets.QCheckBox(RoverTab)
        self.chkRoverNAV.setObjectName("chkRoverNAV")
        self.horizontalLayout_2.addWidget(self.chkRoverNAV)
        self.tRoverNAV = QtWidgets.QLineEdit(RoverTab)
        self.tRoverNAV.setEnabled(False)
        self.tRoverNAV.setObjectName("tRoverNAV")
        self.horizontalLayout_2.addWidget(self.tRoverNAV)
        self.btnChoseRoverNAV = QtWidgets.QToolButton(RoverTab)
        self.btnChoseRoverNAV.setObjectName("btnChoseRoverNAV")
        self.horizontalLayout_2.addWidget(self.btnChoseRoverNAV)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtWidgets.QLabel(RoverTab)
        self.label_5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.tRoverPosX = QtWidgets.QDoubleSpinBox(RoverTab)
        self.tRoverPosX.setObjectName("tRoverPosX")
        self.horizontalLayout_3.addWidget(self.tRoverPosX)
        self.label_6 = QtWidgets.QLabel(RoverTab)
        self.label_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        self.tRoverPosY = QtWidgets.QDoubleSpinBox(RoverTab)
        self.tRoverPosY.setObjectName("tRoverPosY")
        self.horizontalLayout_3.addWidget(self.tRoverPosY)
        self.label_7 = QtWidgets.QLabel(RoverTab)
        self.label_7.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.tRoverPosZ = QtWidgets.QDoubleSpinBox(RoverTab)
        self.tRoverPosZ.setObjectName("tRoverPosZ")
        self.horizontalLayout_3.addWidget(self.tRoverPosZ)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(RoverTab)
        QtCore.QMetaObject.connectSlotsByName(RoverTab)

    def retranslateUi(self, RoverTab):
        _translate = QtCore.QCoreApplication.translate
        RoverTab.setWindowTitle(_translate("RoverTab", "Form"))
        self.label_4.setText(_translate("RoverTab", "OBS File:"))
        self.tRoverOBS.setPlaceholderText(_translate("RoverTab", "press the button aside to choose an .OBS file..."))
        self.btnChoseRoverOBS.setText(_translate("RoverTab", "..."))
        self.chkRoverNAV.setText(_translate("RoverTab", "Rover NAV File:"))
        self.tRoverNAV.setPlaceholderText(
            _translate("RoverTab", "select the checkbox aside to upload a custom .NAV file..."))
        self.btnChoseRoverNAV.setText(_translate("RoverTab", "..."))
        self.label_5.setText(_translate("RoverTab", "Pos X:"))
        self.label_6.setText(_translate("RoverTab", "Pos Y:"))
        self.label_7.setText(_translate("RoverTab", "Pos Z:"))

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Aggancio gli Eventi
        self.btnChoseRoverOBS.clicked.connect(self.chooseFileOBS)
        self.btnChoseRoverNAV.clicked.connect(self.chooseFileNAV)
        self.chkRoverNAV.clicked.connect(self.toggleFileNAV)

    def chooseFileOBS(self):
        if "PYCHARM_HOSTED" in os.environ:
            ret, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select File',
                options=QtWidgets.QFileDialog.DontUseNativeDialog,
            )
        else:
            ret, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select File'
            )
        if ret != "":
            self.tRoverOBS.setText(ret)

    def chooseFileNAV(self):
        if "PYCHARM_HOSTED" in os.environ:
            ret, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select File',
                options=QtWidgets.QFileDialog.DontUseNativeDialog,
            )
        else:
            ret, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select File'
            )
        if ret != "":
            self.tRoverNAV.setText(ret)

    def toggleFileNAV(self):
        if self.chkRoverNAV.isChecked():
            self.tRoverNAV.setEnabled(True)
        else:
            self.tRoverNAV.setEnabled(False)