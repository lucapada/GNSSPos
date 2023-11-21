from PyQt5 import QtCore, QtWidgets

class CustomTimeDialog(QtWidgets.QDialog):
    def __init__(self, parentWindow):
        super().__init__()
        self.parentWindow = parentWindow
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Set Start Moving Time')
        layout = QtWidgets.QVBoxLayout()

        self.checkbox = QtWidgets.QCheckBox("Do you want to set a custom start moving time?")
        self.label = QtWidgets.QLabel('Insert the timestamp from which the rover started moving:')
        self.textbox = QtWidgets.QLineEdit()

        self.textbox.setText(self.parentWindow.startMovingTime)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addWidget(self.textbox)

        self.ok_button = QtWidgets.QPushButton('OK')
        self.ok_button.clicked.connect(self.close_dialog)
        layout.addWidget(self.ok_button)

        self.label.setVisible(False)
        self.textbox.setVisible(False)
        self.checkbox.stateChanged.connect(self.show_hide)

        self.setLayout(layout)

    def show_hide(self, state):
        if state == QtCore.Qt.Checked:
            self.label.setVisible(True)
            self.textbox.setVisible(True)
            self.parentWindow.isStartMovingTimeSet = True
        else:
            self.label.setVisible(False)
            self.textbox.setVisible(False)
            self.parentWindow.isStartMovingTimeSet = False

    def close_dialog(self):
        text = self.textbox.text()
        self.parentWindow.startMovingTime = text
        self.close()