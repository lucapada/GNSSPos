import gzip
import os.path
import shutil
import subprocess
import sys
import time
import unlzw3
from pathlib import Path

import requests
from dotenv import load_dotenv
from EarthdataDownload import SessionWithHeaderRedirection


### --- GENERATED GUI WITH PYQT5 ---
from PyQt5 import QtCore, QtGui, QtWidgets
import RoverTab



class Ui_MainWindow(object):
    def setupUi(self):
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
        self.btnRUN = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(False)
        self.btnRUN.setFont(font)
        self.btnRUN.setObjectName("btnRUN")
        self.gridLayout.addWidget(self.btnRUN, 20, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 16, 0, 1, 1)
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
        self.btnAddRover = QtWidgets.QPushButton(self.centralwidget)
        self.btnAddRover.setObjectName("btnAddRover")
        self.horizontalLayout_15.addWidget(self.btnAddRover)
        self.btnDeleteRover = QtWidgets.QPushButton(self.centralwidget)
        self.btnDeleteRover.setEnabled(False)
        self.btnDeleteRover.setObjectName("btnDeleteRover")
        self.horizontalLayout_15.addWidget(self.btnDeleteRover)
        self.gridLayout.addLayout(self.horizontalLayout_15, 9, 0, 1, 1)
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
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 13, 0, 1, 1)
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
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 14, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 6, 0, 1, 1)
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
        self.btnRUN.setText(_translate("MainWindow", "RUN"))
        self.label_10.setText(_translate("MainWindow", "Rovers"))
        self.btnAddRover.setText(_translate("MainWindow", "Add Rover"))
        self.btnDeleteRover.setText(_translate("MainWindow", "Delete Selected Rover"))
        self.label.setText(_translate("MainWindow", "Working Directory:"))
        self.btnChoseDir.setText(_translate("MainWindow", "..."))
        self.label_2.setText(_translate("MainWindow", "Date Time:"))
        self.chkStartingTime.setText(_translate("MainWindow", "Starting Time:"))
        self.chkEndTime.setText(_translate("MainWindow", "End Time:"))
        self.chkTimeInterval.setText(_translate("MainWindow", "Time Interval:"))
        self.label_3.setText(_translate("MainWindow", "Download Address:"))
        self.btnPlaceholderHelp.setText(_translate("MainWindow", "?"))
        self.btnDownloadData.setText(_translate("MainWindow", "Download Data"))
        self.label_8.setText(_translate("MainWindow", "Permanent/Base Station Name:"))
        self.chkBaseOBS.setText(_translate("MainWindow", "OBS File"))
        self.btnChoseBaseOBS.setText(_translate("MainWindow", "..."))
        self.chkBaseNAV.setText(_translate("MainWindow", "NAV File"))
        self.btnChoseBaseNAV.setText(_translate("MainWindow", "..."))
        self.label_9.setText(_translate("MainWindow", "Base/Permanent Station"))
        self.label_11.setText(_translate("MainWindow", "General Settings"))
### --- END OF GENERATED CODE ---

    def __init__(self, MainWindow):
        """
        Metodo chiamato all'avvio del programma
        :param MainWindow:
        """
        self.MainWindow = MainWindow
        self.setupUi()
        self.MainWindow.show()

        # Disabilito Starting/Ending/Interval Time
        self.tStartingTime.setEnabled(False)
        self.tEndTime.setEnabled(False)
        self.cmbTimeInterval.setEnabled(False)
        self.tBaseOBS.setEnabled(False)
        self.tBaseNAV.setEnabled(False)

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
        self.dailyEphURL = "https://cddis.nasa.gov/archive/gnss/data/daily/%Y/%n/%yn/brdc%n0.%yn.Z"
        self.dailyOrbitURL = self.tDownloadAddress.text() + "%W/IGS0OPSULT_%Y%n0000_01D_15M_ORB.SP3.gz"
        self.dailyOrbitURL_old = self.tDownloadAddress.text() + "%W/igs%W%D.sp3.Z"

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

        self.ORBIT_PATH = ""
        self.EPH_PATH = ""

        load_dotenv()
        self.NASA_USER = os.getenv('NASA_USERNAME')
        self.NASA_PWD = os.getenv('NASA_PASSWORD')



    def printLog(self, messageText):
        """
        Stampa messageText nella statusbar.
        :param messageText:
        :return:
        """
        self.statusbar.setStyleSheet("")
        self.statusbar.showMessage(messageText)
    def printError(self, messageText):
        self.statusbar.setStyleSheet("background-color : pink")
        self.printLog("ERROR: " + messageText)
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
        diff = time.mktime((y, m, d, 0, 0, 0, 0, 0, 0)) - self.timeFromYMD(1980, 1, 1)
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

    def downloadGenericFiles(self):
        if os.path.isdir(self.tWorkingDir.text()):
            # 0) aggiorno le variabili con la selezione dei dati definitiva
            self.updateDateTimeInfo()
            # 1) accedo al portale NASA per il download dei dati
            session = SessionWithHeaderRedirection(self.NASA_USER, self.NASA_PWD)

            # 2) scarico il broadcast delle effemeridi giornaliere
            dailyEphPath = self.downloadData(session, self.buildURL(self.dailyEphURL), self.tWorkingDir.text(), "Daily Broadcast Ephemeris File")
            if dailyEphPath is not False:
                self.printLog("Daily Broadcast Ephemeris File downloaded in: " + dailyEphPath)
                # estraggo il file: è .Z
                decompressed_data = unlzw3.unlzw(Path(dailyEphPath))
                with open(dailyEphPath[0:len(dailyEphPath)-2], 'wb') as output:
                    output.write(decompressed_data)
                    self.EPH_PATH = dailyEphPath[0:len(dailyEphPath)-2]
            # 2) scarico le orbite giornaliere
            dailyOrbitPath = self.downloadData(session, self.buildURL(self.dailyOrbitURL), self.tWorkingDir.text(), "Daily .sp3 Orbit File")
            if dailyOrbitPath is False:
                self.printError("No .sp3 file in " + self.buildURL(self.dailyOrbitURL) + ". Trying with the oldest URL.")
                dailyOrbitPath = self.downloadData(session, self.buildURL(self.dailyOrbitURL_old), self.tWorkingDir.text(), "Daily .sp3 Orbit File")
                if dailyOrbitPath is False:
                    self.printError("No .sp3 file in " + self.buildURL(self.dailyOrbitURL_old))
                if dailyOrbitPath is not False:
                    self.printLog("Daily Orbit File downloaded in: " + dailyOrbitPath)
                    # estraggo il file: è .z
                    decompressed_data = unlzw3.unlzw(Path(dailyOrbitPath))
                    with open(dailyOrbitPath[0:len(dailyOrbitPath) - 2], 'wb') as output:
                        output.write(decompressed_data)
                        self.ORBIT_PATH = dailyOrbitPath[0:len(dailyOrbitPath) - 2]
            else:
                self.printLog("Daily Orbit File downloaded in: " + dailyOrbitPath)
                # estraggo il file: è .gz
                with gzip.open(dailyOrbitPath, "rb") as infile, open(dailyOrbitPath[0:len(dailyOrbitPath) - 3], "wb") as outfile:
                    shutil.copyfileobj(infile, outfile)
                    self.ORBIT_PATH = dailyOrbitPath[0:len(dailyOrbitPath) - 3]
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

    def run(self):
        # Controllo che:
        # 1) working directory sia impostata
        # 2) ci siano almeno 3 rover
        if os.path.isdir(self.tWorkingDir.text()) and self.tabWidget.count() >= 3:
            error = False
            # 0) gestisco la base/stazione permanente

            # 1) passo in rassegna tutti i rover e, mentre verifico i dati, creo un dizionario in cui metto tutto
            ROVER_DICT = {}
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
                    from serial.tools.list_ports_windows import comports
                    binPath = os.path.dirname(os.path.abspath(__file__)) + "/RTKLIB-demo5/rnx2rtkp.exe"
                # Mac & Linux are POSIX compliant (UNIX like systems)
                elif os.name == 'posix':
                    from serial.tools.list_ports_posix import comports
                    binPath = os.path.dirname(os.path.abspath(__file__)) + "/RTKLIB-demo5/rnx2rtkp"

                cfgFile = os.path.dirname(os.path.abspath(__file__)) + "/post-processing.conf"
                posFile = dataPath + self.tabWidget.tabText(r).replace(" ","_") + ".pos"

                timeSettings = ""
                if self.chkStartingTime.isChecked(): timeSettings += "-ts " + self.DATETIME_INFO['%Y'] + "/" + self.DATETIME_INFO['%m'] + "/" + self.DATETIME_INFO['%d'] + " " + self.tStartingTime.text() + ":00"
                if self.chkEndTime.isChecked(): timeSettings += "-te " + self.DATETIME_INFO['%Y'] + "/" + self.DATETIME_INFO['%m'] + "/" + self.DATETIME_INFO['%d'] + " " + self.tEndTime.text() + ":00"

                # TODO: NON STO CONSIDERANDO LA BASE
                cmd_text = r'%s -p 0 -x 0 -y 2 -k %s -o %s.pos %s -t -e %s %s %s' % (binPath, cfgFile, posFile, timeSettings, obsFile, navFile, self.ORBIT_PATH)

                # TODO: check if initial rtklibPath modification works on both linux and windows system (I modified on windows...)
                self.printLog("************* Generating Solution of '%s' *************" % (self.tabWidget.tabText(r)))
                self.printLog(cmd_text)
                subprocess.Popen(cmd_text, stdout=subprocess.PIPE, shell=True)
                # self.printLog(proc.communicate())
                self.printLog("************* '%s' DONE *************" % (self.tabWidget.tabText(r)))

                ROVER_DICT[r] = {
                    "OBS": obsFile,
                    "NAV": navFile,
                    "X": float(str(posX).replace(",",".")),
                    "Y": float(str(posY).replace(",",".")),
                    "Z": float(str(posZ).replace(",",".")),
                    "POS": posFile
                }

            # 2) implementazione algoritmo
            # if error is not False:
                # TODO: implementazione algoritmo
        else:
            self.printError("No Working Directory has been set up, or at least 3 receivers have not been entered.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    sys.exit(app.exec_())