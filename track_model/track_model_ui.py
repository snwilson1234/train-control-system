import sys

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from track_model.track_model import TrackModel, ColorEnum, BreakEnum
from track_model.testbench_ui import TestBench
from track_model.resources import *
from PySide6.QtCore import QThreadPool
from train.train_model.ui.custom_widgets import AnimatedToggle, Color
from PySide6 import QtGui
from PySide6 import QtCore

class Block_Info(Enum):
    GREEN_YARD_CONNECTION = -2
    RED_YARD_CONNECTION = -3
    RED_LINE = 2
    GREEN_LINE = 0
    MAINTENANCE = -1
    RED_STATION = 3
    GREEN_STATION = 4

class TrackModelMainWindow(QMainWindow):

    def __del__(self):
        self.tm.delete_track()
        #pass

    def closeEvent(self, event):
        self.tm.delete_track()
        event.accept()

    def __init__(self, app):
        super(TrackModelMainWindow, self).__init__()

        self.setWindowTitle("Track Model")
        self.setFixedSize(QSize(1250,740))
        #self.resize(1000, 1000)
        self.move(10, 10)

        self.imported_lines = []
        self.broken_stuff = []
        
        tabs = QTabWidget()
        vboxr = QVBoxLayout()   
        spacer1 = QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed)
        spacer = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)
        spacer2 = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox1 = QHBoxLayout()

        # Import Track UI
        self.import_btn = QPushButton("Import Track")
        vboxr.addWidget(QLabel("Import Track:"))
        self.import_cmbx0 = QComboBox()
        self.import_cmbx0.currentTextChanged.connect(self.on_import_cmbx0_changed)
        self.import_cmbx0.addItems([ColorEnum.GREEN.value, ColorEnum.RED.value])
        self.import_cmbx0.setCurrentIndex(-1)
        hbox1.addWidget(self.import_cmbx0)
        hbox1.addItem(spacer1)
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.on_import_clicked)
        hbox1.addWidget(self.import_btn)
        vboxr.addLayout(hbox1)
        vboxr.addItem(spacer1)

        # Break/Fix Thing UI
        vboxr.addWidget(QLabel("Break/Fix Thing:"))
        hbox2 = QHBoxLayout()
        self.fail_cmbx0 = QComboBox()
        self.fail_cmbx0.currentTextChanged.connect(self.on_fail_cmbx0_changed)
        hbox2.addWidget(self.fail_cmbx0)
        hbox2.addItem(spacer1)

        self.fail_cmbx1 = QComboBox()
        self.fail_cmbx1.currentTextChanged.connect(self.on_fail_cmbx1_changed)
        hbox2.addWidget(self.fail_cmbx1)
        hbox2.addItem(spacer1)

        self.fail_cmbx2 = QComboBox()
        self.fail_cmbx2.currentTextChanged.connect(self.on_fail_cmbx2_changed)
        hbox2.addWidget(self.fail_cmbx2)
        vboxr.addLayout(hbox2)
        vboxr.addItem(spacer1)

        # Rail Failure UI
        self.rail_btn = QPushButton("Break Rail")
        self.rail_btn.clicked.connect(self.on_rail_clicked)
        self.fix_rail_btn = QPushButton("Fix Broken Rail")
        self.fix_rail_btn.clicked.connect(self.on_fix_rail_clicked)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.rail_btn)
        hbox3.addItem(spacer1)
        hbox3.addWidget(self.fix_rail_btn)
        vboxr.addLayout(hbox3)
        vboxr.addItem(spacer1)
        
        # Track Circuit Failure UI
        self.circuit_btn = QPushButton("Track Circuit Failure")
        self.circuit_btn.clicked.connect(self.on_circuit_clicked)
        self.fix_circuit_btn = QPushButton("Fix Track Circuit")
        self.fix_circuit_btn.clicked.connect(self.on_fix_circuit_clicked)
        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.circuit_btn)
        hbox4.addItem(spacer1)
        hbox4.addWidget(self.fix_circuit_btn)
        vboxr.addLayout(hbox4)
        vboxr.addItem(spacer1)

        # Power Failure UI
        self.power_btn = QPushButton("Power Failure")
        self.power_btn.clicked.connect(self.on_power_clicked)
        self.fix_power_btn = QPushButton("Fix Power Failure")
        self.fix_power_btn.clicked.connect(self.on_fix_power_clicked)
        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.power_btn)
        hbox5.addItem(spacer1)
        hbox5.addWidget(self.fix_power_btn)
        vboxr.addLayout(hbox5)
        vboxr.addItem(spacer1)

        # Fix Table UI
        vboxr.addWidget(QLabel("Requires Fixing:"))
        self.fixit_table = QTableWidget()
        self.fixit_table.setColumnCount(4)
        self.fixit_table.setColumnWidth(0, 70)
        self.fixit_table.setColumnWidth(1, 70)
        self.fixit_table.setColumnWidth(2, 70)
        self.fixit_table.setColumnWidth(3, 200)
        self.fixit_table.setMaximumHeight(70)
        vboxr.addWidget(self.fixit_table)
        vboxr.addItem(spacer)

        # Switch Table
        vboxr.addItem(spacer)
        vboxr.addWidget(QLabel("Switch Positions:"))
        self.switch_table = QTableWidget()
        self.switch_table.setColumnCount(3)
        self.switch_table.setRowCount(25)
        self.switch_table.setMaximumHeight(90)
        vboxr.addWidget(self.switch_table)

        # Lights Table
        vboxr.addItem(spacer)
        vboxr.addWidget(QLabel("Light Status:"))
        self.light_table = QTableWidget()
        self.light_table.setColumnCount(3)
        self.light_table.setRowCount(60)
        self.light_table.setMaximumHeight(90)
        vboxr.addWidget(self.light_table)

        # Railroad Crossings
        vboxr.addItem(spacer)
        vboxr.addWidget(QLabel("Railroad Crossings:"))
        self.crossing_table = QTableWidget()
        self.crossing_table.setColumnCount(3)
        self.crossing_table.setRowCount(3)
        self.crossing_table.setMaximumHeight(60)
        vboxr.addWidget(self.crossing_table)
        vboxr.addItem(spacer2)
        
        # Track Layout Image UI
        vboxl = QVBoxLayout()

        # Track Model Map UI
        w2 = QWidget()
        vbox4 = QVBoxLayout()
        self.data = [ [None] * 37 for _ in range(47)]

        self.model = TrackModelTable(self.data)
        self.map = QTableView()
        self.map.setModel(self.model)
        self.map.setShowGrid(True)
        self.map.horizontalHeader().setVisible(False)
        self.map.verticalHeader().setVisible(False)
        self.map.verticalHeader().setMaximumSectionSize(14)
        self.map.horizontalHeader().setMaximumSectionSize(19)
        self.map.resizeRowsToContents()
        self.map.resizeColumnsToContents()
        self.map.setFixedWidth(720)
        self.map.setFixedHeight(660)
        #self.map.setSizeAdjustPolicy(QSizeAdjustPolicy.Fixed)
        #self.map.resize(QSize(370, 470))

        self.delegate = TrackModelTableStyle()
        self.map.setItemDelegate(self.delegate)
        for i in range(0,8*2,2):
            self.map.setSpan(25+i,34,2,1)
        for i in range(0,8*2,2):
            self.map.setSpan(25+i,31,2,1)

        # Set red line from yard
        self.map.setSpan(12,32,3,1)

        # Set green line stuff from yard
        self.map.setSpan(20,32,2,1)
        self.map.setSpan(29,35,2,2)
        self.map.setSpan(20,36,11,1)
        self.map.setSpan(15,32,5,5)

        # Get station block to span two
        self.map.setSpan(33,33,2,1)
        vboxl.addWidget(self.map)

        # Tickets UI
        label = QLabel("Tickets: ")
        self.tickets1 = QLabel()
        self.tickets2 = QLabel()
        hbox7 = QHBoxLayout()
        vboxl.addItem(spacer2)
        hbox7.addWidget(label)
        hbox7.addWidget(self.tickets1)
        hbox7.addWidget(self.tickets2)
        vboxr.addLayout(hbox7)

        # Passengers UI
        label = QLabel("Passengers: ")
        self.passengers1 = QLabel()
        self.passengers2 = QLabel()
        hbox9 = QHBoxLayout()
        vboxl.addItem(spacer2)
        hbox9.addWidget(label)
        hbox9.addWidget(self.passengers1)
        hbox9.addWidget(self.passengers2)
        vboxr.addLayout(hbox9)

        # Block Occupancy List UI
        vbox6 = QVBoxLayout()
        label = QLabel("Block Occupancy:")
        self.blocks1 = QLabel()
        self.blocks2 = QLabel()
        self.blocks3 = QLabel()
        vbox6.addWidget(label)
        vbox6.addWidget(self.blocks1)
        vbox6.addWidget(self.blocks2)
        vbox6.addWidget(self.blocks3)

        # Set Track Heater
        hbox6 = QHBoxLayout()
        label = QLabel("Temperature (F): ")
        hbox6.addWidget(label)
        self.new_temp = QLineEdit()
        self.new_temp_btn = QPushButton("Set")
        self.new_temp_btn.clicked.connect(self.on_temp_clicked)
        hbox6.addWidget(self.new_temp)
        hbox6.addItem(spacer1)
        hbox6.addWidget(self.new_temp_btn)
        hbox6.addItem(spacer1)
        label = QLabel("Track Heater: ")
        hbox6.addWidget(label)
        self.heater_status = QLabel("OFF")
        hbox6.addItem(spacer1)
        hbox6.addWidget(self.heater_status)
        vboxr.addLayout(hbox6)

        # Layouts
        spacer = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox8 = QHBoxLayout()
        hbox8.addItem(spacer2)
        hbox8.addItem(spacer1)
        hbox8.addItem(vboxl)
        hbox8.addItem(spacer2)
        hbox8.addItem(spacer2)
        hbox8.addItem(vboxr)
        hbox8.addItem(spacer1)
        hbox8.addItem(spacer2)
        vbox2 = QVBoxLayout()
        vbox2.addItem(hbox8)

        grid = QGridLayout()
        w = QWidget()
        w = Color('light blue')
        w.setLayout(vbox2)
        self.setLayout(vbox2)
        
        # Track Model & Testbench
        self.tm = TrackModel(app)     
        self.tb = TestBench(self.tm)
        self.tb.move(820, 10)
        tabs.addTab(w, "Track Model")
        tabs.addTab(self.tb, "Testbench")

        self.setCentralWidget(tabs)
        self.show()

        # Signals & Threadpool
        self.threadpool = QThreadPool()
        self.connect_signals()
        self.threadpool.start(self.tm)
        


    # Connect Signals
    def connect_signals(self):
        self.tm.signals.update_bool_block_status.connect(self.update_block)
        self.tm.signals.update_bool_block_status.connect(self.repaint_map)
        self.tm.signals.update_tickets.connect(self.update_tickets)
        self.tm.signals.update_passengers.connect(self.update_passengers)
        self.tm.signals.update_switches.connect(self.update_switches)
        self.tm.signals.update_lights.connect(self.update_lights)
        self.tm.signals.update_crossings.connect(self.update_railroad)
    

    # Import Track Functions
    def on_import_clicked(self):
        fileName, filter = QFileDialog.getOpenFileName(self, "Import Track", "./track_model", "CSV (*.csv)")

        if not fileName == '':
            res = self.tm.import_track(fileName, self.import_cmbx0_line)

            if res: 
                self.fail_cmbx0.clear()
                self.fail_cmbx0.addItems(self.tm.get_line_list())
                
                if(self.import_cmbx0_line not in self.imported_lines):
                    self.imported_lines.append(self.import_cmbx0_line)

                self.update_block()
                self.update_switches()
                self.update_lights()

    # Import Combo Box
    def on_import_cmbx0_changed(self, text):
        self.import_cmbx0_line = ColorEnum.__call__(text)

        if self.import_cmbx0_line == ColorEnum.NONE:
            self.import_btn.setEnabled(False)
        else:
            self.import_btn.setEnabled(True)


    # Break/Fix Thing Functions
    def on_fail_cmbx0_changed(self, text):
        self.fail_cmbx0_line = text
        self.fail_cmbx1.clear()
        self.fail_cmbx1.addItems(self.tm.get_section_list(ColorEnum.__call__(text)))

    def on_fail_cmbx1_changed(self, text):
        self.fail_cmbx1_sec = text
        self.fail_cmbx2.clear()
        self.fail_cmbx2.addItems(self.tm.get_number_list(ColorEnum.__call__(self.fail_cmbx0_line), text))

    def on_fail_cmbx2_changed(self, text):
        self.fail_cmbx2_blk = text

    # Break Rail
    def on_rail_clicked(self):
        self.tm.break_thing(ColorEnum.__call__(self.fail_cmbx0_line), int(self.fail_cmbx2_blk), BreakEnum.RAIL)
        self.broken_stuff.append([self.fail_cmbx0_line, self.fail_cmbx1_sec, str(self.fail_cmbx2_blk), "Broken Rail"])
        self.update_block()
        self.update_fixit_table()

    # Break Track Circuit
    def on_circuit_clicked(self):
        self.tm.break_thing(ColorEnum.__call__(self.fail_cmbx0_line), int(self.fail_cmbx2_blk), BreakEnum.CIRCUIT)
        self.broken_stuff.append([self.fail_cmbx0_line, self.fail_cmbx1_sec, str(self.fail_cmbx2_blk), "Track Circuit Failure"])
        self.update_block()
        self.update_fixit_table()

    # Break Power
    def on_power_clicked(self):
        self.tm.break_thing(ColorEnum.__call__(self.fail_cmbx0_line), int(self.fail_cmbx2_blk), BreakEnum.POWER)
        self.broken_stuff.append([self.fail_cmbx0_line, self.fail_cmbx1_sec, str(self.fail_cmbx2_blk), "Power Failure"])
        self.update_block()
        self.update_fixit_table()
    
    # Fix Rail
    def on_fix_rail_clicked(self):
        try: 
            self.tm.fix_thing(ColorEnum.__call__(self.fail_cmbx0_line), int(self.fail_cmbx2_blk), BreakEnum.RAIL)
            self.broken_stuff.remove([self.fail_cmbx0_line, self.fail_cmbx1_sec, str(self.fail_cmbx2_blk), "Broken Rail"])
        except:
            return
        self.update_block()
        self.update_fixit_table() 

    # Fix Track Circuit
    def on_fix_circuit_clicked(self):
        try: 
            self.tm.fix_thing(ColorEnum.__call__(self.fail_cmbx0_line), int(self.fail_cmbx2_blk), BreakEnum.CIRCUIT)
            self.broken_stuff.remove([self.fail_cmbx0_line, self.fail_cmbx1_sec, str(self.fail_cmbx2_blk), "Track Circuit Failure"])
        except:
            return
        self.update_block()
        self.update_fixit_table()

    # Fix Power
    def on_fix_power_clicked(self):
        try: 
            self.tm.fix_thing(ColorEnum.__call__(self.fail_cmbx0_line), int(self.fail_cmbx2_blk), BreakEnum.POWER)
            self.broken_stuff.remove([self.fail_cmbx0_line, self.fail_cmbx1_sec, str(self.fail_cmbx2_blk), "Power Failure"])
        except:
            return
        
        self.update_block()
        self.update_fixit_table()


    # Update Failure Table
    def update_fixit_table(self):
        row = len(self.broken_stuff)
        self.fixit_table.setRowCount(row)
        for r in range(row):
            for c in range(4):
                self.fixit_table.setItem(r, c, QTableWidgetItem(self.broken_stuff[r][c]))


    # Block Status List Functions
    def update_block(self):
        if len(self.imported_lines) >= 1:
            assert isinstance(self.imported_lines[0], ColorEnum)
            self.blocks1.setText(str(self.imported_lines[0].value) + ": " + str(self.tm.bool_block_status[self.imported_lines[0].value][1:]))
        if len(self.imported_lines) >= 2:
            assert isinstance(self.imported_lines[1], ColorEnum)
            self.blocks2.setText(str(self.imported_lines[1].value) + ": " + str(self.tm.bool_block_status[self.imported_lines[1].value][1:]))
            


    # Tickets Functions
    def update_tickets(self, value):
        if len(self.imported_lines) >= 1:
            assert isinstance(self.imported_lines[0], ColorEnum)
            #self.tickets1.setText(str(self.tm.tickets[self.imported_lines[0].value]))
            self.tickets1.setText(str(value[self.imported_lines[0].value]))
            #self.tickets1.setText(str(self.imported_lines[0].value) + ": " + str(self.tm.tickets[self.imported_lines[0].value]))
        # if len(self.imported_lines) >= 2:
        #     assert isinstance(self.imported_lines[1], ColorEnum)
        #     self.tm.set_tickets(self.imported_lines[1], value)
        #     self.tickets2.setText(str(self.imported_lines[1].value) + ": " + str(self.tm.tickets[self.imported_lines[1].value]))

    
     # Passengers Functions
    def update_passengers(self, value):
        if len(self.imported_lines) >= 1:
            assert isinstance(self.imported_lines[0], ColorEnum)
            self.passengers1.setText("Onboarding: " + str(value[0]) + "   Disembarking: " + str(value[1])+ "   Total: " + str(value[2]))


    # Switches Functions
    def update_switches(self):
        len = 0
        for line in self.imported_lines:
            count = 0
            for i, switch in enumerate(self.tm.get_root_switch_list(line)):
                count += 1
                self.switch_table.setItem(len + i, 0, QTableWidgetItem(line.value))
                self.switch_table.setItem(len + i, 1, QTableWidgetItem(str(int(switch))))

                pos = int(self.tm.get_switch(line, switch))
                if pos == 0:
                    self.switch_table.setItem(len + i, 2, QTableWidgetItem("YARD"))
                else:
                    self.switch_table.setItem(len + i, 2, QTableWidgetItem(str(pos)))
            len += count


    # Lights Functions
    def update_lights(self):
        len = 0
        for line in self.imported_lines:
            count = 0
            for i, block in enumerate(self.tm.get_all_switch_list(line)):
                count += 1
                light = self.tm.get_light(line, block)
                self.light_table.setItem(len + i, 0, QTableWidgetItem(line.value))
                self.light_table.setItem(len + i, 1, QTableWidgetItem(str(int(block))))
                self.light_table.setItem(len + i, 2, QTableWidgetItem(light))
            len += count

    
    # Railroad Functions
    def update_railroad(self):
        len = 0 
        for line in self.imported_lines:
            count = 0
            for tup in self.tm.crossing_blocks[line.value]:
                count += 1
                self.crossing_table.setItem(len, 0, QTableWidgetItem(line.value))
                self.crossing_table.setItem(len, 1, QTableWidgetItem(str(int(tup[0]))))
                self.crossing_table.setItem(len, 2, QTableWidgetItem(str(int(tup[1]))))
            len += count
    

    # Track Heater Function
    def on_temp_clicked(self):
        num = int(self.new_temp.text())
        if num < 32:
            self.tm.track_heater = True
            self.heater_status.setText("ON")
        else:
            self.tm.track_heater = False
            self.heater_status.setText("OFF")
        


    # Redraw track model map
    def repaint_map(self):
        # Green Yard Connection
        self.data[20][32] = Block_Info.GREEN_YARD_CONNECTION
        self.data[21][32] = Block_Info.GREEN_YARD_CONNECTION
        for i in range(20, 31):
            self.data[i][36] = Block_Info.GREEN_YARD_CONNECTION
        self.data[29][35] = Block_Info.GREEN_YARD_CONNECTION
        self.data[30][35] = Block_Info.GREEN_YARD_CONNECTION


        # Red Yard Connection
        self.data[14][32] = Block_Info.RED_YARD_CONNECTION
        self.data[13][32] = Block_Info.RED_YARD_CONNECTION
        self.data[12][32] = Block_Info.RED_YARD_CONNECTION

        # Stations
        if(ColorEnum.GREEN in self.imported_lines):
            self.data[33][33] = Block_Info.GREEN_STATION
            self.data[41][32] = Block_Info.GREEN_STATION
            self.data[43][31] = Block_Info.GREEN_STATION
            self.data[43][26] = Block_Info.GREEN_STATION
            self.data[45][26] = Block_Info.GREEN_STATION
            self.data[45][14] = Block_Info.GREEN_STATION
            self.data[23][2] = Block_Info.GREEN_STATION
            self.data[8][4] = Block_Info.GREEN_STATION
            self.data[8][6] = Block_Info.GREEN_STATION
            self.data[1][7] = Block_Info.GREEN_STATION
            self.data[3][16] = Block_Info.GREEN_STATION
            self.data[23][30] = Block_Info.GREEN_STATION
            self.data[23][21] = Block_Info.GREEN_STATION
            self.data[22][11] = Block_Info.GREEN_STATION
            self.data[22][31] = Block_Info.GREEN_STATION
            self.data[22][31] = Block_Info.GREEN_STATION
            self.data[3][7] = Block_Info.GREEN_STATION
            self.data[4][10] = Block_Info.GREEN_STATION
            self.data[17][6] = Block_Info.GREEN_STATION
            self.data[25][11] = Block_Info.GREEN_STATION
            self.data[39][17] = Block_Info.GREEN_STATION
            self.data[1][8] = "15"
            self.data[1][9] = "14"
            self.data[1][10] = "13"
            self.data[1][12] = "12"
            self.data[1][13] = "11"
            self.data[1][14] = "10"
            self.data[3][5] = "17"
            self.data[3][10] = "1"
            self.data[3][17] = "9"
            self.data[4][4] = "18"
            #self.data[4][10] = "2"
            self.data[4][17] = "8"
            self.data[5][4] = "19"
            self.data[5][11] = "3"
            self.data[5][17] = "7"
            self.data[6][4] = "20"
            self.data[7][4] = "21"
            #self.data[8][4] = "22"
            self.data[9][4] = "23"
            self.data[7][13] = "4"
            self.data[7][14] = "5"
            self.data[7][15] = "6"
            self.data[10][4] = "24"
            self.data[11][4] = "25"
            self.data[12][4] = "26"
            self.data[13][4] = "27"
            self.data[14][4] = "28"
            self.data[15][6] = "29"
            self.data[15][3] = "150"
            self.data[16][2] = "149"
            self.data[16][6] = "30"
            #self.data[17][6] = "31"
            self.data[18][6] = "32"
            self.data[19][6] = "33"
            self.data[19][1] = "146"
            self.data[18][2] = "147"
            self.data[17][2] = "148"
            self.data[20][1] = "145"
            self.data[20][5] = "34"
            self.data[21][1] = "144"
            self.data[22][0] = "143"
            self.data[23][0] = "142"
            self.data[20][7] = "35"
            self.data[20][8] = "36"
            self.data[20][9] = "37"
            self.data[20][10] = "38"
            #self.data[20][11] = "39"
            self.data[20][12] = "40"
            self.data[20][13] = "41"
            self.data[20][14] = "42"
            self.data[20][15] = "43"
            self.data[20][17] = "44"
            self.data[20][19] = "45"
            self.data[20][20] = "46"
            self.data[20][21] = "47"
            self.data[20][22] = "48"
            self.data[20][23] = "49"
            self.data[20][24] = "50"
            self.data[20][25] = "51"
            self.data[20][26] = "52"
            self.data[20][27] = "53"
            self.data[20][28] = "54"
            self.data[20][29] = "55"
            self.data[20][30] = "56"
            self.data[20][31] = "57"
            self.data[23][33] = "59"
            self.data[25][2] = "141"
            self.data[25][3] = "140"
            self.data[25][4] = "139"
            self.data[25][5] = "138"
            self.data[25][6] = "137"
            self.data[25][7] = "136"
            self.data[25][8] = "135"
            self.data[25][9] = "134"
            self.data[25][10] = "133"
            #self.data[25][11] = "132"
            self.data[25][12] = "131"
            self.data[25][13] = "130"
            self.data[25][14] = "129"
            self.data[25][15] = "128"
            self.data[25][16] = "127"
            self.data[25][17] = "126"
            self.data[25][19] = "125"
            self.data[25][20] = "124"
            self.data[25][21] = "123"
            self.data[25][22] = "122"
            self.data[25][23] = "121"
            self.data[25][24] = "120"
            self.data[25][25] = "119"
            self.data[25][26] = "118"
            self.data[25][27] = "117"
            self.data[25][28] = "116"
            self.data[25][29] = "115"
            self.data[25][30] = "114"
            self.data[26][32] = "113"
            self.data[28][32] = "112"
            self.data[30][32] = "111"
            self.data[32][32] = "110"
            self.data[34][32] = "109"
            self.data[36][32] = "108"
            self.data[38][32] = "107"
            self.data[40][32] = "106"
            self.data[24][35] = "60"
            self.data[26][35] = "61"
            self.data[28][35] = "62"
            #self.data[30][35] = "63"
            self.data[32][35] = "64"
            self.data[34][35] = "65"
            self.data[36][35] = "66"
            self.data[38][35] = "67"
            self.data[40][35] = "68"
            self.data[39][12] = "93"
            self.data[39][14] = "94"
            self.data[39][15] = "95"
            #self.data[39][17] = "96"
            self.data[40][12] = "92"
            self.data[41][12] = "91"
            self.data[42][12] = "90"
            self.data[43][12] = "89"
            self.data[40][17] = "97"
            self.data[41][17] = "98"
            self.data[42][17] = "99"
            self.data[43][18] = "100"
            #self.data[45][14] = "88"
            self.data[45][15] = "87"
            self.data[45][16] = "86"
            self.data[45][18] = "85"
            self.data[45][19] = "84"
            self.data[45][20] = "83"
            self.data[45][21] = "82"
            self.data[45][22] = "81"
            self.data[45][23] = "80"
            self.data[45][24] = "79"
            self.data[45][25] = "78"
            #self.data[45][26] = "77"
            self.data[45][28] = "76"
            self.data[45][29] = "75"
            self.data[45][30] = "74"
            self.data[45][31] = "73"
            self.data[45][32] = "72"
            self.data[44][33] = "71"
            self.data[42][27] = "101"
            self.data[41][28] = "102"
            self.data[41][29] = "103"
            self.data[41][30] = "104"
        if(ColorEnum.RED in self.imported_lines):
            self.data[31][5] = Block_Info.RED_STATION
            self.data[31][3] = Block_Info.RED_STATION
            self.data[35][17] = Block_Info.RED_STATION
            self.data[37][17] = Block_Info.RED_STATION
            self.data[26][17] = Block_Info.RED_STATION
            self.data[26][19] = Block_Info.RED_STATION
            self.data[16][17] = Block_Info.RED_STATION
            self.data[16][19] = Block_Info.RED_STATION
            self.data[14][20] = Block_Info.RED_STATION
            self.data[12][20] = Block_Info.RED_STATION
            self.data[12][25] = Block_Info.RED_STATION
            self.data[8][31] = Block_Info.RED_STATION
            self.data[10][31] = Block_Info.RED_STATION
            self.data[14][25] = Block_Info.RED_STATION
            self.data[37][14] = Block_Info.RED_STATION
            self.data[35][14] = Block_Info.RED_STATION
            self.data[8][28] = "4"
            self.data[8][29] = "5"
            self.data[8][30] = "6"
            #self.data[8][31] = "7"
            self.data[10][33] = "8"
            self.data[11][33] = "9"
            self.data[10][26] = "3"
            self.data[11][25] = "2"
            #self.data[12][33] = "1"
            self.data[12][30] = "10"
            self.data[13][18] = "23"
            self.data[13][19] = "22"
            #self.data[14][20] = "21"
            self.data[14][21] = "20"
            self.data[14][22] = "19"
            self.data[14][23] = "18"
            self.data[14][24] = "17"
            #self.data[14][25] = "16"
            self.data[14][27] = "15"
            self.data[14][28] = "14"
            self.data[14][29] = "13"
            self.data[14][30] = "12"
            self.data[14][31] = "11"
            self.data[15][19] = "24"
            #self.data[16][19] = "25"
            self.data[17][19] = "26"
            self.data[18][19] = "27"
            self.data[19][19] = "28"
            self.data[19][16] = "76"
            self.data[22][15] = "73"
            self.data[22][19] = "31"
            self.data[23][16] = "72"
            self.data[23][19] = "32"
            #self.data[26][19] = "35"
            self.data[26][19] = "35"
            self.data[27][19] = "36"
            self.data[28][19] = "37"
            self.data[29][19] = "38"
            self.data[30][19] = "39"
            self.data[31][19] = "40"
            self.data[32][19] = "41"
            self.data[33][19] = "42"
            self.data[34][19] = "43"
            self.data[31][16] = "71"
            self.data[32][15] = "70"
            self.data[33][15] = "69"
            self.data[30][16] = "68"
            self.data[34][16] = "67"
            self.data[36][18] = "45"
            self.data[37][16] = "46"
            self.data[37][15] = "47"
            #self.data[37][14] = "48"
            self.data[37][13] = "49"
            self.data[37][12] = "50"
            self.data[37][11] = "51"
            self.data[37][10] = "52"
            self.data[35][10] = "66"
            self.data[37][6] = "55"
            self.data[37][7] = "54"
            self.data[37][8] = "53"
            self.data[35][4] = "56"
            self.data[34][3] = "57"
            self.data[33][3] = "58"
            self.data[32][3] = "59"
            #self.data[31][3] = "60"
            self.data[31][7] = "62"
            self.data[32][7] = "63"
            self.data[33][8] = "64"
            self.data[34][9] = "65"
            self.data[29][5] = "61"

        # Yard Blocks
        for i in range(15,20,1):
            for j in range(32,37,1):
                self.data[i][j] = "YARD"

        for line in self.imported_lines:
            index_to_map_dict = {}

            if line == ColorEnum.BLUE:
                index_to_map_dict = BLUE_LINE_INDEX_TO_MAP_DICT
            elif line == ColorEnum.GREEN:
                index_to_map_dict = GREEN_LINE_INDEX_TO_MAP_DICT
            elif line == ColorEnum.RED:
                index_to_map_dict = RED_LINE_INDEX_TO_MAP_DICT


            for i in range(1, len(self.tm.bool_block_status[line.value]), 1):
                pos = index_to_map_dict[i]

                if isinstance(pos, list):
                    for _,ele in enumerate(pos):
                        if self.tm.bool_block_status[line.value][i] == 1:
                            self.data[ele.row][ele.col] = 1
                            self.model.setData(self.model.createIndex(ele.row, ele.col), 1, Qt.DisplayRole)
                        elif line == ColorEnum.GREEN:
                            self.data[ele.row][ele.col] = 0
                            self.model.setData(self.model.createIndex(ele.row, ele.col), 0, Qt.DisplayRole)
                        elif line == ColorEnum.RED:
                            self.data[ele.row][ele.col] = 2
                            self.model.setData(self.model.createIndex(ele.row, ele.col), 2, Qt.DisplayRole)
                        
                else:
                    if self.tm.bool_block_status[line.value][i] == 1:
                        self.data[pos.row][pos.col] = 1
                        self.model.setData(self.model.createIndex(pos.row, pos.col), 1, Qt.DisplayRole)
                    elif line == ColorEnum.GREEN:
                        self.data[pos.row][pos.col] = 0
                        self.model.setData(self.model.createIndex(pos.row, pos.col), 0, Qt.DisplayRole)
                    elif line == ColorEnum.RED:
                        self.data[pos.row][pos.col] = 2
                        self.model.setData(self.model.createIndex(pos.row, pos.col), 2, Qt.DisplayRole)
                    


class TrackModelTableStyle(QStyledItemDelegate):
    count = 0
    def paint(self, painter, option, index):
        #print("[TRACK MODEL]: paint")
        option.displayAlignment = Qt.AlignCenter

        # Get the data from the model
        self.data = index.data(Qt.DisplayRole)

        # Get the background color based on the data
        self.color_maintenance = QtGui.QColor(QtCore.Qt.black)
        self.color_yellow = QtGui.QColor(QtCore.Qt.yellow)
        self.color_green_line = QtGui.QColor("#00af4d")
        self.yard_color = QtGui.QColor("#bbbbbd")
        self.color_red_line = QtGui.QColor("#ff0000")
        self.color_dark_red = QtGui.QColor("#9B0303")
        self.color_dark_green = QtGui.QColor("#355C00")
        self.color_station = QtGui.QColor("#999999")

        if self.data == None:
            pass
        elif self.data == "YARD":
            painter.fillRect(option.rect, self.yard_color)
        elif isinstance(self.data, str):
            option.displayAlignment = QtCore.Qt.AlignCenter
            painter.drawText(option.rect, self.data)
        elif self.data == 1:
            painter.fillRect(option.rect, self.color_yellow)
        elif self.data == Block_Info.GREEN_LINE.value:
            painter.fillRect(option.rect, self.color_green_line)
        elif self.data == Block_Info.MAINTENANCE.value:
            painter.fillRect(option.rect, self.color_maintenance)
        elif self.data == Block_Info.RED_LINE.value:
            painter.fillRect(option.rect, self.color_red_line)
        elif self.data == Block_Info.GREEN_YARD_CONNECTION.value:
            painter.fillRect(option.rect, self.yard_color)
        elif self.data == Block_Info.RED_YARD_CONNECTION.value:
            painter.fillRect(option.rect, self.yard_color)
        elif self.data == Block_Info.RED_STATION.value:
            painter.fillRect(option.rect, self.color_dark_red)
        elif self.data == Block_Info.GREEN_STATION.value:
            painter.fillRect(option.rect, self.color_dark_green)
        else:
            font = painter.font()
            font.setPointSize(font.pointSize()/2)
            painter.setFont(font)
            painter.drawText(option.rect, self.data)


class TrackModelTable(QAbstractTableModel):
    def __init__(self, data):
        super(TrackModelTable, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        
    def setData(self, index, value, role) -> bool:
        self.dataChanged.emit(index,index,value)
        return True

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])
    
    

if __name__ == "__main__":
    app = QApplication([])
    window = TrackModelMainWindow()
    window.show()
    sys.exit(app.exec())