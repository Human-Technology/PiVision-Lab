from PySide6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QListWidget,QListWidgetItem
from PySide6.QtCore import QTimer, Qt, Signal

class MainPanel(QWidget):
    item_checked = Signal(str)
    item_unchecked = Signal(str)

    def __init__(self):
        super().__init__()
        mainLayout = QVBoxLayout()
        
        #----- Top Panel ----------------------
        northPanel = QWidget()
        northLayout = QVBoxLayout()
        self.qlTitleCombo = QLabel("Select a Model")
        self.comboModels = QComboBox()
        self.comboModels.setCurrentText("Models")
        northLayout.addWidget(self.qlTitleCombo)
        northLayout.addWidget(self.comboModels)
        northPanel.setLayout(northLayout)
        #------------------------------------------

        #----- Center Panel ---------------------
        centerPanel = QWidget()
        centerLayout = QVBoxLayout()
        self.image_label = QLabel()
        self.qlTitleListObjects = QLabel("Detectable Objects")
        self.listObjects = QListWidget()
        self.listObjects.itemChanged.connect(self.on_item_changed)  # Connect the signal
        centerLayout.addWidget(self.image_label)
        centerLayout.addWidget(self.qlTitleListObjects)
        centerLayout.addWidget(self.listObjects)
        centerPanel.setLayout(centerLayout)
        #-----------------------------------------
        self.timer = QTimer()

        #------ Bottom Panel -------------------
        southPanel = QWidget()
        southLayout = QVBoxLayout()
        self.btn_iniciar = QPushButton("Start Camera")
        southLayout.addWidget(self.btn_iniciar)
        southPanel.setLayout(southLayout)
        #-----------------------------------------

        mainLayout.addWidget(northPanel)
        mainLayout.addWidget(centerPanel)
        mainLayout.addWidget(southPanel)

        self.setLayout(mainLayout)

    def set_items(self, listObjects:list):
        for object in listObjects:
            item = QListWidgetItem(object)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.listObjects.addItem(item)

    def on_item_changed(self, item):
        if item.checkState() == Qt.Checked:
            self.item_checked.emit(item.text())
        else:
            self.item_unchecked.emit(item.text())
