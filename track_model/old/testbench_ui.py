import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from train import Train
from track_model import TrackModel, LineEnum, ColorEnum

class TestBench(QMainWindow):
    def __init__(self, tm : TrackModel):

        super().__init__()
        self.setWindowTitle("Track Model Testbench")
        self.setFixedSize(QSize(400,300))

        self.tm = tm
        self.speed_cmbx0_ti = None
        self.auth_cmbx0_ti = None
        self.train_cmbx0_ti = None

        # New Train Signal
        vbox = QVBoxLayout()   
        self.new_train_btn = QPushButton("New Train")
        self.new_train_btn.clicked.connect(self.on_new_train_clicked)
        vbox.addWidget(self.new_train_btn)

        # Set Speed
        hbox1 = QHBoxLayout()
        self.speed_cmbx0 = QComboBox()
        self.speed_cmbx0.currentIndexChanged.connect(self.on_speed_cmbx0_changed)
        hbox1.addWidget(self.speed_cmbx0)
        self.new_speed = QLineEdit()
        self.new_speed_btn = QPushButton("Set")
        self.new_speed_btn.clicked.connect(self.on_speed_cmbx0_clicked)
        hbox1.addWidget(self.new_speed)
        hbox1.addWidget(self.new_speed_btn)
        vbox.addLayout(hbox1)

        # Set Authority
        hbox2 = QHBoxLayout()
        self.auth_cmbx0 = QComboBox()
        self.auth_cmbx0.currentIndexChanged.connect(self.on_auth_cmbx0_changed)
        hbox2.addWidget(self.auth_cmbx0)
        self.new_auth = QLineEdit()
        self.new_auth_btn = QPushButton("Set")
        self.new_auth_btn.clicked.connect(self.on_auth_cmbx0_clicked)
        hbox2.addWidget(self.new_auth)
        hbox2.addWidget(self.new_auth_btn)
        vbox.addLayout(hbox2)

        # Get Speed and Authority
        hbox3 = QHBoxLayout()
        label = QLabel("Train: ")
        hbox3.addWidget(label)
        self.train_cmbx0 = QComboBox()
        self.train_cmbx0.currentIndexChanged.connect(self.on_train_cmbx0_changed)
        hbox3.addWidget(self.train_cmbx0)
        self.train_speed = QLabel()
        label = QLabel("Speed: ")
        hbox3.addWidget(label)
        hbox3.addWidget(self.train_speed)
        self.train_auth = QLabel()
        label = QLabel("Authority: ")
        hbox3.addWidget(label)
        hbox3.addWidget(self.train_auth)
        vbox.addLayout(hbox3)


        vbox2 = QVBoxLayout()
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox2.addItem(spacer)
        grid = QGridLayout()
        grid.addLayout(vbox, 0, 1)
        #grid.addLayout(vbox2, 0, 0)
  
        self.setLayout(grid)


    def on_new_train_clicked(self):
        tn = Train(50, 15, self.tm.TRAIN_INDEX)
        self.tm.train_list.append(tn)
        self.tm.TRAIN_INDEX += 1
        self.speed_cmbx0.clear()
        self.auth_cmbx0.clear()
        self.train_cmbx0.clear()
        result = [str(ts.get_id()) for ts in self.tm.train_list]
        self.speed_cmbx0.addItems(result)
        self.auth_cmbx0.addItems(result)
        self.train_cmbx0.addItems(result)

    def on_speed_cmbx0_changed(self, index):
        self.speed_cmbx0_ti = index

    def on_speed_cmbx0_clicked(self):
        t = self.tm.train_list[int(self.speed_cmbx0_ti)].set_speed_mps(float(self.new_speed.text()))
        if self.speed_cmbx0_ti == self.train_cmbx0_ti:
            self.on_train_cmbx0_changed(self.train_cmbx0_ti)

    def on_auth_cmbx0_changed(self, index):
        self.auth_cmbx0_ti = index

    def on_auth_cmbx0_clicked(self):
        t = self.tm.train_list[int(self.auth_cmbx0_ti)].set_authority_b(int(self.new_auth.text()))
        if self.auth_cmbx0_ti == self.train_cmbx0_ti:
            self.on_train_cmbx0_changed(self.train_cmbx0_ti)
    
    def on_train_cmbx0_changed(self, index):
        self.train_cmbx0_ti = index
        t = self.tm.train_list[int(self.train_cmbx0_ti)]
        self.train_speed.setText(str(t.get_speed_mps()))
        self.train_auth.setText(str(t.get_authority_b()))