from PyQt5 import QtCore, QtWidgets

class Ui_DistancesWindow(QtWidgets.QMainWindow):
    def __init__(self, numRovers, parentWindow):
        super().__init__()
        self.numRovers = numRovers
        self.parentWindow = parentWindow
        self.distances = self.parentWindow.distances
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.initUI(numRovers, parentWindow)

    def initUI(self, numRovers, parentWindow):
        # Crea un layout verticale
        layoutVerticale = QtWidgets.QVBoxLayout()
        
        # Crea etichette e caselle di testo
        for i in range(self.numRovers):
            for j in range(self.numRovers):
                if i < j:
                    layoutOrizzontale = QtWidgets.QHBoxLayout()
                    label = QtWidgets.QLabel()
                    label.setText("Rover %d - Rover %d (in meters): " % (i+1, j+1))
                    text_box = QtWidgets.QDoubleSpinBox()
                    text_box.setObjectName("distance_%d_%d" % (i, j))
                    text_box.setValue(float(self.distances.get("%d_%d" % (i, j), 0.00)))
                    text_box.valueChanged.connect(self.setDistance)
                    layoutOrizzontale.addWidget(label)
                    layoutOrizzontale.addWidget(text_box)
                    layoutVerticale.addLayout(layoutOrizzontale)

        # Creo pulsante per chiusura form
        button = QtWidgets.QPushButton()
        button.setText("Close")
        button.clicked.connect(self.close)
        layoutVerticale.addWidget(button)

        # Imposta il layout principale della finestra
        widget = QtWidgets.QWidget()
        widget.setLayout(layoutVerticale)
        self.setCentralWidget(widget)

        self.setWindowTitle('Setup Distances')
        self.setGeometry(200, 200, 300, 200)  # Imposta le dimensioni della finestra

    def setDistance(self, val):
        # print(self.focusWidget().objectName())
        self.distances[self.focusWidget().objectName()[9:]] = float(val)
        self.parentWindow.updateDistances(self.distances)