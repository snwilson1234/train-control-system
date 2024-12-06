import sys
import random

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from track_model.train import TrainTM
from track_model.track_model import TrackModel, ColorEnum
from train.train_model.ui.main_app import Main_App
from train.train_model.ui.custom_widgets import AnimatedToggle, Color

class TestBench(QMainWindow):
    def __init__(self, tm : TrackModel):

        super().__init__()
        self.setWindowTitle("Track Model Testbench")

        self.tm = tm
        self.line = None
        self.lines = []
        self.speed_cmbx0_ti = None
        self.auth_cmbx0_ti = None
        self.train_cmbx0_ti = None
        self.light_cmbx1_blk = None
        self.light_cmbx2_c = None
        self.train = None

        # Track Line Selection
        vbox = QVBoxLayout()
        spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox.addItem(spacer)
        hbox8 = QHBoxLayout()
        label = QLabel("Line: ")
        hbox8.addWidget(label)
        self.line_cmbx0 = QComboBox()
        self.line_cmbx0.currentIndexChanged.connect(self.on_line_cmbx0_changed)
        hbox8.addWidget(self.line_cmbx0)
        vbox.addItem(hbox8)
        vbox.addItem(spacer)

        # Generate Tickets Signal
        self.ticket_btn = QPushButton("Generate Tickets")
        self.ticket_btn.clicked.connect(self.on_ticket_clicked)
        vbox.addWidget(self.ticket_btn)
        vbox.addItem(spacer)

        # New Train Signal
        self.new_train_btn = QPushButton("New Train")
        self.new_train_btn.clicked.connect(self.on_new_train_clicked)
        vbox.addWidget(self.new_train_btn)
        vbox.addItem(spacer)

        # Set Speed
        spacer2 = QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox.addItem(spacer2)
        hbox1 = QHBoxLayout()
        label = QLabel("Train: ")
        hbox1.addWidget(label)
        self.train_cmbx0 = QComboBox()
        self.train_cmbx0.currentIndexChanged.connect(self.on_train_cmbx0_changed)
        hbox1.addWidget(self.train_cmbx0)
        vbox.addItem(hbox1)
        vbox.addItem(spacer)
        label = QLabel("New Speed (m/s): ")
        hbox7 = QHBoxLayout()
        hbox7.addWidget(label)
        self.new_speed = QLineEdit()
        self.new_speed_btn = QPushButton("Set")
        self.new_speed_btn.clicked.connect(self.on_speed_cmbx0_clicked)
        hbox7.addWidget(self.new_speed)
        hbox7.addWidget(self.new_speed_btn)
        vbox.addItem(hbox7)

        # Set Authority
        hbox2 = QHBoxLayout()
        vbox.addItem(spacer2)
        label = QLabel("New Authority (blocks): ")
        hbox2.addWidget(label)
        self.new_auth = QLineEdit()
        self.new_auth_btn = QPushButton("Set")
        self.new_auth_btn.clicked.connect(self.on_auth_cmbx0_clicked)
        hbox2.addWidget(self.new_auth)
        hbox2.addWidget(self.new_auth_btn)
        vbox.addLayout(hbox2)

        # Get Speed and Authority and Position
        hbox3 = QHBoxLayout()
        vbox.addItem(spacer2)
        self.train_line = QLabel()
        label = QLabel("Line: ")
        hbox3.addWidget(label)
        hbox3.addWidget(self.train_line)
        vbox.addLayout(hbox3)
        hbox12 = QHBoxLayout()
        self.train_speed = QLabel()
        label = QLabel("Speed (m/s): ")
        hbox12.addWidget(label)
        hbox12.addWidget(self.train_speed)
        vbox.addLayout(hbox12)
        hbox13 = QHBoxLayout()
        self.train_auth = QLabel()
        label = QLabel("Authority: ")
        hbox13.addWidget(label)
        hbox13.addWidget(self.train_auth)
        vbox.addLayout(hbox13)

        # Block Information
        hbox9 = QHBoxLayout()
        self.train_pos = QLabel()
        label = QLabel("Block: ")
        hbox9.addWidget(label)
        hbox9.addWidget(self.train_pos)
        vbox.addLayout(hbox9)
        hbox14 = QHBoxLayout()
        self.speed_lim = QLabel()
        label = QLabel("Speed Limit (m/s): ")
        hbox14.addWidget(label)
        hbox14.addWidget(self.speed_lim)
        vbox.addLayout(hbox14)
        hbox15 = QHBoxLayout()
        self.blk_length = QLabel()
        label = QLabel("Length (m): ")
        hbox15.addWidget(label)
        hbox15.addWidget(self.blk_length)
        vbox.addLayout(hbox15)
        hbox16 = QHBoxLayout()
        self.blk_dir = QLabel()
        label = QLabel("Bidirectional: ")
        hbox16.addWidget(label)
        hbox16.addWidget(self.blk_dir)
        vbox.addLayout(hbox16)

        # Beacon Table
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox.addItem(spacer)
        vbox.addWidget(QLabel("Beacons:"))
        self.beacon_table = QTableWidget()
        self.beacon_table.setColumnCount(3)
        self.beacon_table.setRowCount(1)
        self.beacon_table.setFixedHeight(60)
        self.beacon_table.setHorizontalHeaderItem(0, QTableWidgetItem('Side'))
        self.beacon_table.setHorizontalHeaderItem(1, QTableWidgetItem('Station'))
        self.beacon_table.setHorizontalHeaderItem(2, QTableWidgetItem('Tunnel'))
        vbox.addWidget(self.beacon_table)
        vbox.addItem(spacer)

        # Set Switch Positions
        vbox.addItem(spacer)
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox.addItem(spacer)
        hbox4 = QHBoxLayout()
        label = QLabel("Switches: ")
        self.switch_cmbx2 = QComboBox()
        self.switch_cmbx1 = QComboBox()
        self.switch_cmbx1.currentTextChanged.connect(self.on_switch_cmbx1_changed)
        vbox.addWidget(label)
        hbox4.addWidget(self.switch_cmbx1)
        self.switch_cmbx2.currentTextChanged.connect(self.on_switch_cmbx2_changed)
        hbox4.addWidget(self.switch_cmbx2)
        self.switch_btn = QPushButton("Set")
        self.switch_btn.clicked.connect(self.on_switch_clicked)
        hbox4.addWidget(self.switch_btn)
        vbox.addLayout(hbox4)

        # Set Lights Positions
        spacer = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)
        vbox.addItem(spacer)
        hbox5 = QHBoxLayout()
        label = QLabel("Lights: ")
        vbox.addWidget(label)
        self.light_cmbx2 = QComboBox()
        self.light_cmbx2.addItems(['R', 'G'])
        self.light_cmbx2_c = self.light_cmbx2.currentText()

        self.light_cmbx1 = QComboBox()
        self.light_cmbx1.currentTextChanged.connect(self.on_light_cmbx1_changed)
        hbox5.addWidget(self.light_cmbx1)
        self.light_cmbx2.currentTextChanged.connect(self.on_light_cmbx2_changed)
        hbox5.addWidget(self.light_cmbx2)

        self.light_btn = QPushButton("Set")
        self.light_btn.clicked.connect(self.on_light_clicked)
        hbox5.addWidget(self.light_btn)
        vbox.addLayout(hbox5)
        vbox.addItem(spacer)

        # Layouts
        vbox2 = QVBoxLayout()
        spacer = QSpacerItem(800, 40, QSizePolicy.Fixed, QSizePolicy.Fixed)
        vbox2.addItem(spacer)
        vbox3 = QVBoxLayout()
        spacer = QSpacerItem(100, 40, QSizePolicy.Fixed, QSizePolicy.Fixed)
        vbox3.addItem(spacer)
        grid = QGridLayout()
        grid.addLayout(vbox, 0, 1)
        grid.addLayout(vbox2, 0, 0)
        grid.addLayout(vbox3, 0, 2)
        
        self.connect_signals()
        w = QWidget()
        w = Color('light blue')
        w.setLayout(grid)
        self.setCentralWidget(w)


    # Connect Signals
    def connect_signals(self):
        self.tm.signals.import_track.connect(self.import_track)
        self.tm.signals.update_beacon.connect(self.update_beacon_table)
        self.tm.signals.new_train.connect(self.update_new_trains)
        self.tm.signals.update_block_status.connect(self.update_trains)

    # Import Track Slot
    def import_track(self, value):
        assert isinstance(value, ColorEnum)
        self.lines.append(value.value)
        self.line = value
        self.line_cmbx0.clear()
        self.line_cmbx0.addItems(self.lines)
        self.switch_cmbx1.clear()
        self.switch_cmbx1.addItems(str(s) for s in self.tm.get_root_switch_list(value))
        self.light_cmbx1.clear()
        self.light_cmbx1.addItems(str(s) for s in self.tm.get_all_switch_list(value))
        self.switch_cmbx1.setCurrentIndex(-1)
        self.light_cmbx1.setCurrentIndex(-1)
        self.light_cmbx2.setCurrentIndex(-1)


    # Update Train List
    def update_new_trains(self):
        result = [str(ts.id) for ts in self.tm.trains[self.line.value]]
        self.train_cmbx0.clear()
        self.train_cmbx0.addItems(result)


    # Update Trains
    def update_trains(self):
        for train in self.tm.trains[self.line.value]:
            if train.id == self.train:
                tmtr = train
        assert isinstance(self.tm.train_factory, Main_App)
        try:
            train = self.tm.train_factory.qthread_manager.peek_model(self.train)
            self.blk_length.setText(str(self.tm.get_block_length(self.line, tmtr.block_i)))
            self.speed_lim.setText(str(self.tm.get_block_speed(self.line, tmtr.block_i)))
            self.train_pos.setText(str(tmtr.block_i))
            dir = self.tm.get_switch_passing_direction(self.line, tmtr.block_i)
            if dir == 3:
                self.blk_dir.setText("Yes")
            else:
                self.blk_dir.setText("No")
        except:
            pass
        
        

    # Change Line
    def on_line_cmbx0_changed(self, text):
        self.line = ColorEnum.__call__(self.lines[text])

    # Ticket Button
    def on_ticket_clicked(self):
        self.tm.set_tickets(self.line, random.randint(1, 100))
        self.tm.signals.update_tickets.emit(self.tm.tickets)

    # New Train Button
    def on_new_train_clicked(self):
        self.tm.new_train_ctc(self.line.value, 70, 5, 120)
        result = [str(ts.id) for ts in self.tm.trains[self.line.value]]
        self.train_cmbx0.clear()
        self.train_cmbx0.addItems(result)


    # Set New Speed Slots
    def on_speed_cmbx0_changed(self, index):
        self.speed_cmbx0_ti = index

    def on_speed_cmbx0_clicked(self):
        assert isinstance(self.tm.train_factory, Main_App)
        train = self.tm.train_factory.qthread_manager.peek_model(self.speed_cmbx0_ti)
        train.set_track_circuit_data(int(self.new_speed.text()), train.authority_blocks)
        if self.speed_cmbx0_ti == self.train_cmbx0_ti:
            self.on_train_cmbx0_changed(self.train_cmbx0_ti)


    # Set New Authority Slots
    def on_auth_cmbx0_changed(self, index):
        self.auth_cmbx0_ti = index

    def on_auth_cmbx0_clicked(self):
        assert isinstance(self.tm.train_factory, Main_App)
        train = self.tm.train_factory.qthread_manager.peek_model(self.auth_cmbx0_ti)
        train.set_track_circuit_data(train.commanded_speed_mps, int(self.new_auth.text()))
        if self.auth_cmbx0_ti == self.train_cmbx0_ti:
            self.on_train_cmbx0_changed(self.train_cmbx0_ti)


    # Change Train Index
    def on_train_cmbx0_changed(self, index):
        try:
            assert isinstance(self.tm.train_factory, Main_App)
            self.train_cmbx0_ti = index
            self.train = index
            train = self.tm.train_factory.qthread_manager.peek_model(self.train)
            self.train_speed.setText(str(train.commanded_speed_mps))
            self.train_auth.setText(str(train.authority_blocks))
            train_tm = self.tm.trains[self.line.value][int(self.train_cmbx0_ti)]
            assert isinstance(train_tm, TrainTM)
            self.train_pos.setText(str(train_tm.block_i))
            self.train_line.setText(self.line.value + "   ")
        except:
            pass


    # Set Switch Functions
    def on_switch_cmbx1_changed(self, text):
        self.switch_cmbx1_sw = text
        self.switch_cmbx2.clear()
        if len(self.lines) > 0 and text:
            try:
                self.switch_cmbx2.addItems([str(s) for s in self.tm.get_switch_positions(self.line, text)])
            except:
                pass

    def on_switch_cmbx2_changed(self, text):
        self.switch_cmbx_p = text

    def on_switch_clicked(self):
        self.tm.set_switch_tm(self.line, int(self.switch_cmbx1_sw), int(self.switch_cmbx_p))
        pos = self.tm.get_switch_positions(self.line, int(self.switch_cmbx1_sw))
        self.tm.signals.update_switches.emit()


    # Set Lights Functions
    def on_light_cmbx1_changed(self, text):
        self.light_cmbx1_blk = text

    def on_light_cmbx2_changed(self, text):
        self.light_cmbx2_c = text

    def on_light_clicked(self):
        self.tm.set_light_tm(self.line, int(self.light_cmbx1_blk), self.light_cmbx2_c)
        self.tm.signals.update_lights.emit()


    # Update Beacon Functions
    def update_beacon_table(self, value):
        assert isinstance(value, list)
        for i, item in enumerate(value):
            self.beacon_table.setItem(0, i, QTableWidgetItem(str(item)))



    
