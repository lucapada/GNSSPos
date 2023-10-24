import gzip
import os.path
import shutil
import sys
import time
import zipfile as z
import unlzw3
from pathlib import Path
import matplotlib.pyplot as plt
from pyproj import Transformer
import re
import contextily as ctx

import matplotlib.pyplot as plt
from pyproj import Transformer

import requests
from EarthdataDownload import SessionWithHeaderRedirection

### --- BEGIN OF GENERATED CODE ---
from PyQt5 import QtCore, QtGui, QtWidgets
import RoverTab
from Distances import Ui_DistancesWindow

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(571, 734)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.tWorkingDir = QtWidgets.QLineEdit(self.centralwidget)
        self.tWorkingDir.setObjectName("tWorkingDir")
        self.horizontalLayout.addWidget(self.tWorkingDir)
        self.btnChoseDir = QtWidgets.QToolButton(self.centralwidget)
        self.btnChoseDir.setObjectName("btnChoseDir")
        self.horizontalLayout.addWidget(self.btnChoseDir)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)
        self.btnRUN = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(False)
        self.btnRUN.setFont(font)
        self.btnRUN.setObjectName("btnRUN")
        self.gridLayout.addWidget(self.btnRUN, 20, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 14, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 16, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 6, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_8.addWidget(self.label_3)
        self.tDownloadAddress = QtWidgets.QLineEdit(self.centralwidget)
        self.tDownloadAddress.setObjectName("tDownloadAddress")
        self.horizontalLayout_8.addWidget(self.tDownloadAddress)
        self.btnPlaceholderHelp = QtWidgets.QToolButton(self.centralwidget)
        self.btnPlaceholderHelp.setObjectName("btnPlaceholderHelp")
        self.horizontalLayout_8.addWidget(self.btnPlaceholderHelp)
        self.btnDownloadData = QtWidgets.QPushButton(self.centralwidget)
        self.btnDownloadData.setObjectName("btnDownloadData")
        self.horizontalLayout_8.addWidget(self.btnDownloadData)
        self.gridLayout.addLayout(self.horizontalLayout_8, 4, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_7.addWidget(self.label_8)
        self.tBaseName = QtWidgets.QLineEdit(self.centralwidget)
        self.tBaseName.setObjectName("tBaseName")
        self.horizontalLayout_7.addWidget(self.tBaseName)
        self.gridLayout_4.addLayout(self.horizontalLayout_7, 0, 0, 1, 1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.chkBaseOBS = QtWidgets.QCheckBox(self.centralwidget)
        self.chkBaseOBS.setObjectName("chkBaseOBS")
        self.horizontalLayout_13.addWidget(self.chkBaseOBS)
        self.tBaseOBS = QtWidgets.QLineEdit(self.centralwidget)
        self.tBaseOBS.setObjectName("tBaseOBS")
        self.horizontalLayout_13.addWidget(self.tBaseOBS)
        self.btnChoseBaseOBS = QtWidgets.QToolButton(self.centralwidget)
        self.btnChoseBaseOBS.setObjectName("btnChoseBaseOBS")
        self.horizontalLayout_13.addWidget(self.btnChoseBaseOBS)
        self.gridLayout_4.addLayout(self.horizontalLayout_13, 1, 0, 1, 1)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.chkBaseNAV = QtWidgets.QCheckBox(self.centralwidget)
        self.chkBaseNAV.setObjectName("chkBaseNAV")
        self.horizontalLayout_14.addWidget(self.chkBaseNAV)
        self.tBaseNAV = QtWidgets.QLineEdit(self.centralwidget)
        self.tBaseNAV.setObjectName("tBaseNAV")
        self.horizontalLayout_14.addWidget(self.tBaseNAV)
        self.btnChoseBaseNAV = QtWidgets.QToolButton(self.centralwidget)
        self.btnChoseBaseNAV.setObjectName("btnChoseBaseNAV")
        self.horizontalLayout_14.addWidget(self.btnChoseBaseNAV)
        self.gridLayout_4.addLayout(self.horizontalLayout_14, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_4, 15, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.calendarDT = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendarDT.setObjectName("calendarDT")
        self.horizontalLayout_2.addWidget(self.calendarDT)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.chkStartingTime = QtWidgets.QCheckBox(self.centralwidget)
        self.chkStartingTime.setObjectName("chkStartingTime")
        self.horizontalLayout_3.addWidget(self.chkStartingTime)
        self.tStartingTime = QtWidgets.QTimeEdit(self.centralwidget)
        self.tStartingTime.setObjectName("tStartingTime")
        self.horizontalLayout_3.addWidget(self.tStartingTime)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.chkEndTime = QtWidgets.QCheckBox(self.centralwidget)
        self.chkEndTime.setObjectName("chkEndTime")
        self.horizontalLayout_4.addWidget(self.chkEndTime)
        self.tEndTime = QtWidgets.QTimeEdit(self.centralwidget)
        self.tEndTime.setObjectName("tEndTime")
        self.horizontalLayout_4.addWidget(self.tEndTime)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.chkTimeInterval = QtWidgets.QCheckBox(self.centralwidget)
        self.chkTimeInterval.setObjectName("chkTimeInterval")
        self.horizontalLayout_5.addWidget(self.chkTimeInterval)
        self.cmbTimeInterval = QtWidgets.QComboBox(self.centralwidget)
        self.cmbTimeInterval.setObjectName("cmbTimeInterval")
        self.horizontalLayout_5.addWidget(self.cmbTimeInterval)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 13, 0, 1, 1)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_15.addWidget(self.label_10)
        self.btnSetupDistances = QtWidgets.QPushButton(self.centralwidget)
        self.btnSetupDistances.setObjectName("btnSetupDistances")
        self.horizontalLayout_15.addWidget(self.btnSetupDistances)
        self.btnAddRover = QtWidgets.QPushButton(self.centralwidget)
        self.btnAddRover.setObjectName("btnAddRover")
        self.horizontalLayout_15.addWidget(self.btnAddRover)
        self.btnDeleteRover = QtWidgets.QPushButton(self.centralwidget)
        self.btnDeleteRover.setEnabled(False)
        self.btnDeleteRover.setObjectName("btnDeleteRover")
        self.horizontalLayout_15.addWidget(self.btnDeleteRover)
        self.gridLayout.addLayout(self.horizontalLayout_15, 9, 0, 1, 1)
        self.btnPlotPositions = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.btnPlotPositions.setFont(font)
        self.btnPlotPositions.setObjectName("btnPlotPositions")
        self.gridLayout.addWidget(self.btnPlotPositions, 21, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 571, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Working Directory:"))
        self.btnChoseDir.setText(_translate("MainWindow", "..."))
        self.label_11.setText(_translate("MainWindow", "General Settings"))
        self.btnRUN.setText(_translate("MainWindow", "RUN"))
        self.label_9.setText(_translate("MainWindow", "Base/Permanent Station"))
        self.label_3.setText(_translate("MainWindow", "Download Address:"))
        self.btnPlaceholderHelp.setText(_translate("MainWindow", "?"))
        self.btnDownloadData.setText(_translate("MainWindow", "Download Data"))
        self.label_8.setText(_translate("MainWindow", "Permanent/Base Station Name:"))
        self.chkBaseOBS.setText(_translate("MainWindow", "OBS File"))
        self.btnChoseBaseOBS.setText(_translate("MainWindow", "..."))
        self.chkBaseNAV.setText(_translate("MainWindow", "NAV File"))
        self.btnChoseBaseNAV.setText(_translate("MainWindow", "..."))
        self.label_2.setText(_translate("MainWindow", "Date Time:"))
        self.chkStartingTime.setText(_translate("MainWindow", "Starting Time:"))
        self.chkEndTime.setText(_translate("MainWindow", "End Time:"))
        self.chkTimeInterval.setText(_translate("MainWindow", "Time Interval:"))
        self.label_10.setText(_translate("MainWindow", "Rovers"))
        self.btnSetupDistances.setText(_translate("MainWindow", "Setup Distances"))
        self.btnAddRover.setText(_translate("MainWindow", "Add Rover"))
        self.btnDeleteRover.setText(_translate("MainWindow", "Delete Selected Rover"))
        self.btnPlotPositions.setText(_translate("MainWindow", "PLOT POSITIONS"))
### --- END OF GENERATED CODE ---

    def __init__(self, MainWindow):
        """
        Metodo chiamato all'avvio del programma
        :param MainWindow:
        """
        self.MainWindow = MainWindow
        self.setupUi(self.MainWindow)
        self.MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.MainWindow.show()

        # Disabilito Starting/Ending/Interval Time
        self.tStartingTime.setEnabled(False)
        self.tEndTime.setEnabled(False)
        self.cmbTimeInterval.setEnabled(False)
        self.tBaseOBS.setEnabled(False)
        self.tBaseNAV.setEnabled(False)
        self.btnPlotPositions.setEnabled(False)

        # Aggiungo i placeholder alle textbox
        self.tWorkingDir.setPlaceholderText("press the button aside to chose a directory...")
        self.tDownloadAddress.setPlaceholderText("select the data in the calendar, then write the address you want to get data from...")
        self.tBaseName.setPlaceholderText("insert the Permanent Station name here")
        self.tBaseOBS.setPlaceholderText("select the checkbox aside to enable custom .OBS file")
        self.tBaseNAV.setPlaceholderText("select the checkbox aside to enable custom .NAV file")
        # TODO: Preparo l'indirizzo e lo metto in sola lettura
        self.tDownloadAddress.setReadOnly(True)
        self.tDownloadAddress.setText("https://cddis.nasa.gov/archive/gnss/products/")
        # AAAVPPPTTT_YYYYDDDHHMM_LEN_SMP_CNT.FMT[.gz], guarda qui: http://acc.igs.org/repro3/Long_Product_Filenames_v1.0.pdf
        self.dailyEphURL = "https://cddis.nasa.gov/archive/gnss/data/daily/%Y/%n/%yn/brdc%n0.%yn.gz"
        self.dailyOrbitURLs = [
            self.tDownloadAddress.text() + "%W/IGS0OPSFIN_%Y%n0000_01D_15M_ORB.SP3.gz",
            self.tDownloadAddress.text() + "%W/IGS0OPSULT_%Y%n0000_01D_15M_ORB.SP3.gz",
            self.tDownloadAddress.text() + "%W/igs%W%D.sp3.Z",
        ]

        # aggiungo i valori per il timeinterval
        for i in [0, 0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 15, 30, 60]:
            self.cmbTimeInterval.addItem(str(i))
        
        # creo l'array che conterrà tutti i valori che dovrò aggiornare
        self.DATETIME_INFO = {}
        self.DATETIME_INFO['%Y'] = ""
        self.DATETIME_INFO['%y'] = ""
        self.DATETIME_INFO['%m'] = ""
        self.DATETIME_INFO['%D'] = ""
        self.DATETIME_INFO['%d'] = ""
        self.DATETIME_INFO['%n'] = ""
        self.DATETIME_INFO['%W'] = ""
        self.DATETIME_INFO['%H'] = ""
        self.DATETIME_INFO['%h'] = ""
        self.DATETIME_INFO['%M'] = ""
        self.DATETIME_INFO['%S'] = ""
        self.DATETIME_INFO['%ha'] = ""
        self.DATETIME_INFO['%hb'] = ""
        self.DATETIME_INFO['%hc'] = ""

        # Aggancio gli eventi agli elementi
        self.printLog("Select a Working Directory to start using the software.")
        self.btnChoseDir.clicked.connect(self.chooseWorkingDir)
        self.chkStartingTime.clicked.connect(self.toggleStartingTime)
        self.chkEndTime.clicked.connect(self.toggleEndTime)
        self.chkTimeInterval.clicked.connect(self.toggleTimeInterval)
        self.btnPlaceholderHelp.clicked.connect(self.showKWRPopup)
        self.btnDownloadData.clicked.connect(self.downloadGenericFiles)
        self.btnAddRover.clicked.connect(self.addRover)
        self.btnDeleteRover.clicked.connect(self.deleteSelectedRover)
        self.chkBaseNAV.clicked.connect(self.toggleBaseNAV)
        self.chkBaseOBS.clicked.connect(self.toggleBaseOBS)
        self.btnChoseBaseNAV.clicked.connect(self.chooseBaseNAV)
        self.btnChoseBaseOBS.clicked.connect(self.chooseBaseOBS)
        self.btnRUN.clicked.connect(self.run)
        self.btnSetupDistances.clicked.connect(self.openDistances)
        self.btnPlotPositions.clicked.connect(self.plotPositions)

        self.ORBIT_PATH = ""
        self.EPH_PATH = ""

        with open('.env', 'r') as envFile:
            envLinee = envFile.readlines()
            for envLine in envLinee:
                if envLine.find("NASA_USERNAME") >= 0:
                    self.NASA_USER = envLine.split('=')[1].strip()
                else:
                    self.NASA_PWD = envLine.split('=')[1].strip()
    
        self.distances = {}

    def printLog(self, messageText):
        """
        Stampa messageText nella statusbar.
        :param messageText:
        :return:
        """
        self.statusbar.setStyleSheet("")
        self.statusbar.showMessage(messageText)
        self.statusbar.update()
        time.sleep(1) # per dare tempo all'utente di leggere il messaggio...
    
    def printError(self, messageText):
        self.statusbar.setStyleSheet("background-color : pink")
        self.printLog("ERROR: " + messageText)
        time.sleep(1) # per dare tempo all'utente di leggere il messaggio...
    
    def chooseWorkingDir(self):
        """
        Metodo invocato su pressione del pulsante per la scelta della directory di lavoro.
        :return:
        """
        folder = QtWidgets.QFileDialog.getExistingDirectory(self.MainWindow, "Select Folder")
        self.tWorkingDir.setText(folder + "/")
        self.printLog("Working directory successfully set up. Select time information (calendar and time intervals).")
    
    def toggleStartingTime(self):
        """
        Abilita/disabilita il campo "starting time" a fianco.
        :return:
        """
        if self.chkStartingTime.isChecked():
            self.tStartingTime.setEnabled(True)
        else:
            self.tStartingTime.setEnabled(False)
    
    def toggleEndTime(self):
        """
        Abilita/disabilita il campo "end time" a fianco.
        :return:
        """
        if self.chkEndTime.isChecked():
            self.tEndTime.setEnabled(True)
        else:
            self.tEndTime.setEnabled(False)
    
    def toggleTimeInterval(self):
        """
        Abilita/disabilita il campo "time interval" a fianco.
        :return:
        """
        if self.chkTimeInterval.isChecked():
            self.cmbTimeInterval.setEnabled(True)
        else:
            self.cmbTimeInterval.setEnabled(False)

    def toggleBaseNAV(self):
        if self.chkBaseNAV.isChecked():
            self.tBaseNAV.setEnabled(True)
        else:
            self.tBaseNAV.setEnabled(False)

    def toggleBaseOBS(self):
        if self.chkBaseOBS.isChecked():
            self.tBaseOBS.setEnabled(True)
        else:
            self.tBaseOBS.setEnabled(False)

    def chooseBaseNAV(self):
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
            self.tBaseNAV.setText(ret)

    def chooseBaseOBS(self):
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
            self.tBaseOBS.setText(ret)
    
    def showKWRPopup(self):
        self.updateDateTimeInfo()
        popupDescription = ("%Y: Year (yyyy) [" +                str(self.DATETIME_INFO['%Y']) + "]\n"
                            "%y: Year (vv) [" +                  str(self.DATETIME_INFO['%y']) + "]\n"
                            "%m: Month (mm) [" +                 str(self.DATETIME_INFO['%m']) + "]\n"
                            "%D: Day of Week (0-6) [" +          str(self.DATETIME_INFO['%D']) + "]\n"
                            "%d: Day of Month (dd) [" +          str(self.DATETIME_INFO['%d']) + "]\n"
                            "%n: Day of Year (ddd) [" + str(self.DATETIME_INFO['%n']) + "]\n"
                            "%W: GPS Week No (wwww) [" + str(self.DATETIME_INFO['%W']) + "]\n"
                            "%h: Hour (00-23) [" +               str(self.DATETIME_INFO['%h']) + "]\n"
                            "%M: Minute (00-59) [" +             str(self.DATETIME_INFO['%M']) + "]\n"
                            "%S: Second (00:59) [" +             str(self.DATETIME_INFO['%S']) + "]\n")
                            # "%H: Hour Code (a,b,...,x) [" +      str(self.DATETIME_INFO['%H']) + "]\n"
                            # "%ha: 3H Hour (00,03,21) [" +        str(self.DATETIME_INFO['%ha']) + "]\n"
                            # "%hb: 6H Hour (00,06, 12, 18) [" +   str(self.DATETIME_INFO['%hb']) + "]\n"
                            # "%hc: 124 Hour (00,12) [" +          str(self.DATETIME_INFO['%hc']) + "]")
        QtWidgets.QMessageBox().information(self.MainWindow, "Keyword Replacement in File Path", popupDescription)

    def timeFromYMD(self, y, m, d):
        tm = time.struct_time((y, m, d, 0, 0, 0, 0, 0, 0))
        return time.mktime(tm)
    
    def getGPSWeek(self, y, m, d):
        SECS_PER_WEEK = 60 * 60 * 24 * 7
        diff = time.mktime((y, m, d, 0, 0, 0, 0, 0, 0)) - self.timeFromYMD(1980, 1, 6)
        return int(diff / SECS_PER_WEEK)
    
    def updateDateTimeInfo(self):
        self.DATETIME_INFO = {}
        self.DATETIME_INFO['%Y'] = self.calendarDT.selectedDate().year()
        self.DATETIME_INFO['%y'] = str(self.calendarDT.selectedDate().year())[2:4]
        self.DATETIME_INFO['%m'] = f"{self.calendarDT.selectedDate().month():02}"
        self.DATETIME_INFO['%D'] = f"{self.calendarDT.selectedDate().dayOfWeek():01}" # day of week
        self.DATETIME_INFO['%d'] = f"{self.calendarDT.selectedDate().day():02}" # day of month
        self.DATETIME_INFO['%n'] = f"{self.calendarDT.selectedDate().dayOfYear():03}" # day of year
        self.DATETIME_INFO['%W'] = self.getGPSWeek(self.calendarDT.selectedDate().year(), self.calendarDT.selectedDate().month(), self.calendarDT.selectedDate().day()) # GPS week
        if self.chkStartingTime.isChecked():
            self.DATETIME_INFO['%h'] = f"{self.tStartingTime.text().split(':')[0]:02}"
        else: self.DATETIME_INFO['%h'] = "00"
        if self.chkStartingTime.isChecked():
            self.DATETIME_INFO['%M'] = f"{self.tStartingTime.text().split(':')[1]:02}"
        else:
            self.DATETIME_INFO['%M'] = "00"
        self.DATETIME_INFO['%S'] = "00"
        self.DATETIME_INFO['%H'] = ""
        self.DATETIME_INFO['%ha'] = ""
        self.DATETIME_INFO['%hb'] = ""
        self.DATETIME_INFO['%hc'] = ""

    def buildURL(self, url):
        for k, v in self.DATETIME_INFO.items():
            url = str(url).replace(k, str(v))
        print(url)
        return url

    def downloadData(self, session, url, whereToSave, subject):
        # extract the filename from the url to be used when saving the file
        filename = url[url.rfind('/') + 1:]
        try:
            # submit the request using the session
            response = session.get(url, stream=True)
            self.printLog("Downloading " + subject + " from " + url + ": " + str(response.status_code))
            # raise an exception in case of http errors
            response.raise_for_status()
            # save the file
            path = str(whereToSave) + str(filename).lower()
            with open(path, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    fd.write(chunk)

            return path
        except requests.exceptions.HTTPError as e:
            # handle any errors here
            print(e)
            self.printError("HTTP Request Error")
            return False
        
    def extractFile(self, file):
        if file.split(".")[-1] == "gz":
            # estraggo il file: è .gz
            with gzip.open(file, "rb") as infile:
                with open(file[0:len(file) - 3], "wb") as outfile:
                    shutil.copyfileobj(infile, outfile)
                    return file[0:len(file) - 3]
        else:
            # estraggo il file: è .z
            # f = z.ZipFile(file)
            # f.extractall()
            # f.close()
            uncompressed_data = unlzw3.unlzw(Path(file).read_bytes())
            with open(file[0:len(file)-2], 'wb') as output:
                output.write(uncompressed_data)
            return file[0:len(file)-2]

    def downloadGenericFiles(self):
        if os.path.isdir(self.tWorkingDir.text()):
            # try:
                # 0) aggiorno le variabili con la selezione dei dati definitiva
                self.updateDateTimeInfo()
                # 1) accedo al portale NASA per il download dei dati
                self.printLog("Logging into EarthData NASA Portal...")
                session = SessionWithHeaderRedirection(self.NASA_USER, self.NASA_PWD)

                # 2.1) scarico il broadcast delle effemeridi giornaliere
                dailyEphPath = self.downloadData(session, self.buildURL(self.dailyEphURL), self.tWorkingDir.text(), "Daily Broadcast Ephemeris File")
                if dailyEphPath is not False:
                    self.printLog("Daily Broadcast Ephemeris File downloaded in: " + dailyEphPath)
                    self.EPH_PATH = self.extractFile(dailyEphPath)
                else: 
                    self.printError("No .n file in " + self.buildURL(self.dailyEphURL))
                # 2.2) scarico le orbite giornaliere
                for attempt, dailyOrbitURL in enumerate(self.dailyOrbitURLs):
                    dailyOrbitPath = self.downloadData(session, self.buildURL(dailyOrbitURL), self.tWorkingDir.text(), "Daily .sp3 Orbit File")
                    if dailyOrbitPath is False:
                        self.printError("No .sp3 file in " + self.buildURL(dailyOrbitURL) + ". %s" % ("Let's try with another URL." if attempt < len(2) else ""))
                    else: 
                        self.printLog("Daily Orbit File downloaded in: " + dailyOrbitPath)
                        self.ORBIT_PATH = self.extractFile(dailyOrbitPath)
                        break
            # except:
            #     self.printError("Exception during download of files.")
        else:
            self.printError("Checks whether the selected working directory exists and it is correct.")

    def addRover(self):
        self.tabWidget.addTab(RoverTab.Ui_RoverTab(), "Rover " + str(self.tabWidget.count() + 1))
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
        if self.tabWidget.count() > 1:
            self.btnDeleteRover.setEnabled(True)

    def deleteSelectedRover(self):
        qm = QtWidgets.QMessageBox
        selectedTab = self.tabWidget.tabText(self.tabWidget.currentIndex())
        if qm.question(self.MainWindow,'Delete Rover', 'Are you sure to delete the "' + selectedTab + '"?', qm.Yes | qm.No) == qm.Yes:
            self.tabWidget.removeTab(self.tabWidget.currentIndex())
            if self.tabWidget.count() == 1:
                self.btnDeleteRover.setEnabled(False)

    def openDistances(self):
        self.ui = Ui_DistancesWindow(self.tabWidget.count(), self)
        self.ui.show()

    def updateDistances(self, newDistances):
        self.distances = newDistances
        print("Distances Updated: ")
        print(self.distances)

    def checkDistances(self):
        for v in self.distances.values():
            if v <= 0.00:
                return False
        return True

    def readPositions(self):
        positions = {}
        for kR, vR in enumerate(self.posFiles):
            with open(vR, "r") as posFile:
                linee = posFile.readlines()
                
                timestamps = []
                lat = []
                long = []
                heights = []
                Qs = []
                ns = []
                sdn = []
                sde = []
                sdu = []
                sdne = []
                sdeu = []
                sdun = []
                age = []
                ratio = []

                for l in linee[1:]:
                    # https://epsg.io/4327
                    column = re.split(r'\s+', l.strip())

                    timestamps.append(column[0] + " " + column[1])
                    lat.append(float(column[2]))
                    long.append(float(column[3]))
                    heights.append(float(column[4]))
                    Qs.append(int(column[5]))
                    ns.append(int(column[6]))
                    sdn.append(float(column[7]))
                    sde.append(float(column[8]))
                    sdu.append(float(column[9]))
                    sdne.append(float(column[10]))
                    sdeu.append(float(column[11]))
                    sdun.append(float(column[12]))
                    age.append(float(column[13]))
                    ratio.append(float(column[14]))

                # Set tilemap limits (10% of the difference on each axis is added)
                delta_lat = 0.1 * (max(lat) - min(lat))
                delta_lon = 0.1 * (max(long) - min(long))

                min_lon = min(long) - delta_lon
                max_lon = max(long) + delta_lon
                min_lat = min(lat) - delta_lat
                max_lat = max(lat) + delta_lat

                positions[kR] = {
                    "timestamps":timestamps,
                    "lat":lat,
                    "long":long,
                    "heights":heights,
                    "Q":Qs,
                    "ns":ns,
                    "sdn":sdn,
                    "sde":sde,
                    "sdu":sdu,
                    "sdne":sdne,
                    "sdeu":sdeu,
                    "sdun":sdun,
                    "age":age,
                    "ratio":ratio,
                    "min_long": min_lon,
                    "min_lat":min_lat,
                    "max_long":max_lon,
                    "max_lat":max_lat,
                    "delta_lon":delta_lon,
                    "delta_lat":delta_lat
                }
        self.printLog("All .pos files loaded and ready to be used for the algorithm or plot.")
        return positions

    def plotPositions(self):
        # prendo le posizioni
        positions = self.readPositions()
        # genero tanti colori quante sono le posizioni da plottare
        colors = plt.cm.tab10.colors[:len(positions)]
        # converto le coordinate in EPSG:3857
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        # creo il grafico e rappresento tutti i rover
        # TODO: aggiungere la rappresentazione finale...
        fig, axs = plt.subplots(1,1,figsize=(8,8), dpi=90)
        for kR in positions:
            utm_x = []
            utm_y = []

            for kL in range(len(positions[kR]["lat"])):
                dx, dy = transformer.transform(positions[kR]["long"][kL],positions[kR]["lat"][kL])
                utm_x.append(dx)
                utm_y.append(dy)

            axs.plot(utm_x, utm_y, ":r.", label="Rover " + str(kR+1), markersize=2, color=colors[kR])

        ctx.add_basemap(axs, crs='EPSG:3857', source=ctx.providers.OpenStreetMap.Mapnik)

        plt.ylabel("Northing [m]")
        plt.xlabel("Easting [m]")
        plt.title("Position(s) Representation")
        plt.legend()
        plt.grid()
        plt.show()

    def run(self):
        # Controllo che:
        # 1) working directory sia impostata
        # 2) ci siano almeno 3 rover
        # 3) siano state inserite le distanze
        if os.path.isdir(self.tWorkingDir.text()) and self.tabWidget.count() >= 3 and self.checkDistances():
            error = False
            # 0) TODO: gestisco la base/stazione permanente

            # 1) passo in rassegna tutti i rover e, mentre verifico i dati, creo un dizionario in cui metto tutto
            ROVER_DICT = {}
            self.posFiles = []
            for r in range(self.tabWidget.count()):
                obsFile = self.tabWidget.widget(r).tRoverOBS.text()
                chkNav = self.tabWidget.widget(r).chkRoverNAV.isChecked()
                navFile = self.tabWidget.widget(r).tRoverNAV.text()
                posX = self.tabWidget.widget(r).tRoverPosX.text()
                posY = self.tabWidget.widget(r).tRoverPosY.text()
                posZ = self.tabWidget.widget(r).tRoverPosZ.text()

                if os.path.isfile(obsFile):
                    if chkNav is False:
                        navFile = self.EPH_PATH
                else:
                    self.printError("OBS file for " + self.tabWidget.tabText(r) + " is not valid.")
                    error = True
                    break

                # 1.1) genero le solution con RNX2RTKP
                # RTKLib tool configuration for both unix and windowsnt
                dataPath = self.tWorkingDir.text()
                # from WindowsNT
                if os.name == 'nt':
                    binPath = os.path.dirname(os.path.abspath(__file__)) + "/RTKLIB-demo5/rnx2rtkp.exe"
                # Mac & Linux are POSIX compliant (UNIX like systems)
                elif os.name == 'posix':
                    binPath = os.path.dirname(os.path.abspath(__file__)) + "/RTKLIB/rnx2rtkp"

                cfgFile = os.path.dirname(os.path.abspath(__file__)) + "/post_processing.conf"
                posFile = dataPath + self.tabWidget.tabText(r).replace(" ","_") + ".pos"

                timeSettings = ""
                if self.chkStartingTime.isChecked(): timeSettings += "-ts \"" + self.DATETIME_INFO['%Y'] + "/" + self.DATETIME_INFO['%m'] + "/" + self.DATETIME_INFO['%d'] + "\" \"" + self.tStartingTime.text() + ":00\""
                if self.chkEndTime.isChecked(): timeSettings += " -te \"" + self.DATETIME_INFO['%Y'] + "/" + self.DATETIME_INFO['%m'] + "/" + self.DATETIME_INFO['%d'] + "\" \"" + self.tEndTime.text() + ":00\""

                # TODO: NON STO CONSIDERANDO LA BASE
                # il comando ha questa struttura (da manuale RTKLIB):
                # -?        print help
                # -k file   input options from configuration file [off]
                # -o file   set output file [stdout]
                # -ts ds ts start day/time (ds=y/m/d ts=h:m:s) [obs start time]
                # -te de te end day/time   (de=y/m/d te=h:m:s) [obs end time]
                # -ti tint  time interval (sec) [all]
                # -p mode   mode (0:single,1:dgps,2:kinematic,3:static,4:static-start,
                #                 5:moving-base,6:fixed,7:ppp-kinematic,8:ppp-static,9:ppp-fixed) [2]
                # -m mask   elevation mask angle (deg) [15]
                # -sys s[,s...] nav system(s) (s=G:GPS,R:GLO,E:GAL,J:QZS,C:BDS,I:IRN) [G|R]
                # -f freq   number of frequencies for relative mode (1:L1,2:L1+L2,3:L1+L2+L5) [2]
                # -v thres  validation threshold for integer ambiguity (0.0:no AR) [3.0]
                # -b        backward solutions [off]
                # -c        forward/backward combined solutions [off]
                # -i        instantaneous integer ambiguity resolution [off]
                # -h        fix and hold for integer ambiguity resolution [off]
                # -e        output x/y/z-ecef position [latitude/longitude/height]
                # -a        output e/n/u-baseline [latitude/longitude/height]
                # -n        output NMEA-0183 GGA sentence [off]
                # -g        output latitude/longitude in the form of ddd mm ss.ss' [ddd.ddd]
                # -t        output time in the form of yyyy/mm/dd hh:mm:ss.ss [sssss.ss]
                # -u        output time in utc [gpst]
                # -d col    number of decimals in time [3]
                # -s sep    field separator [' ']
                # -r x y z  reference (base) receiver ecef pos (m) [average of single pos]
                #         rover receiver ecef pos (m) for fixed or ppp-fixed mode
                # -l lat lon hgt reference (base) receiver latitude/longitude/height (deg/m)
                #         rover latitude/longitude/height for fixed or ppp-fixed mode
                # -y level  output soltion status (0:off,1:states,2:residuals) [0]
                # -x level  debug trace level (0:off) [0]
                
                # cmd_text = r'%s -p 0 -x 0 -y 2 -k %s -o %s %s -t -e %s %s %s' % (binPath, cfgFile, posFile, timeSettings, obsFile, navFile, self.ORBIT_PATH)
                # cmd_text = r'%s -k "%s" -o "%s" %s -p 7 -e -t -y 2 "%s" "%s" "%s"' % (binPath, cfgFile, posFile, timeSettings, obsFile, navFile, self.ORBIT_PATH)
                cmd_text = r'%s -o "%s" %s -k %s -p 7 -f 2 -t -y 2 "%s" "%s" "%s"' % (binPath, posFile, timeSettings, cfgFile, obsFile, navFile, self.ORBIT_PATH)

                print(cmd_text)

                self.printLog("************* Generating Solution of '%s' *************" % (self.tabWidget.tabText(r)))
                self.printLog(cmd_text)
                # os.system(cmd_text)
                self.printLog(os.popen(cmd_text).read())
                self.printLog("************* '%s' DONE *************" % (self.tabWidget.tabText(r)))

                # ROVER_DICT[r] = {
                #     "OBS": obsFile,
                #     "NAV": navFile,
                #     "X": float(str(posX).replace(",",".")),
                #     "Y": float(str(posY).replace(",",".")),
                #     "Z": float(str(posZ).replace(",",".")),
                #     "POS": posFile
                # }

                self.posFiles.append(posFile)
            
            # abilito la possibilità di plottare il grafico...
            self.btnPlotPositions.setEnabled(True)

            # 2) carico i risultati letti nella struttura dati
            positions = self.readPositions()

            # 3) implementazione algoritmo
            # if error is not False:
                # TODO: implementazione algoritmo
        else:
            self.printError("No Working Directory has been set up, or at least 3 receivers have not been entered, or distances not inserted.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    sys.exit(app.exec_())