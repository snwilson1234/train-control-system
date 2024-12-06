import sys
import os
import ast
#local imports
from track_controller.ui_help import *
from track_controller.ctc_office_sim import *
from track_controller.track import *
from track_controller.wayside_controller_backend import *

#pyside imports
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtGui import QDesktopServices
from track_controller.interpreter import *

class TrackControllerUI(QMainWindow):
    def __init__(self, green_line_system, red_line_system):
        super().__init__()

        self.green_line_system = green_line_system
        self.red_line_system = red_line_system

        self.setWindowTitle("Track Controller UI")
        #self.setFixedSize(QSize(1500,900))
        #PAGES OF UI
        self.upload_page = UploadPage(self.green_line_system, self.red_line_system)

        self.controller_view = ControllerView(self.green_line_system, self.red_line_system)

        #MAIN LAYOUTS
        self.page_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()
        self.stacklayout = QStackedLayout()

        self.page_layout.addLayout(self.button_layout)
        self.page_layout.addLayout(self.stacklayout)

        #setting up controller view page
        self.btn_controller_view = QPushButton("Controller View")
        self.btn_controller_view.pressed.connect(self.activate_tab_1)
        self.button_layout.addWidget(self.btn_controller_view)
        self.stacklayout.addWidget(self.controller_view)

        #setting up upload page
        self.btn_upload_page = QPushButton("Upload")
        self.btn_upload_page.pressed.connect(self.activate_tab_2)
        self.button_layout.addWidget(self.btn_upload_page)
        self.stacklayout.addWidget(self.upload_page)


        self.main_widget = Color('light blue')
        self.main_widget.setLayout(self.page_layout)
        self.setCentralWidget(self.main_widget)

    #activating stack layout tabs
    def activate_tab_1(self):
        self.stacklayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stacklayout.setCurrentIndex(1)

    def activate_tab_3(self):
        self.stacklayout.setCurrentIndex(2)

class TrackControllerTestBench(QMainWindow):
    def __init__(self, green_line_system, red_line_system):
        super().__init__()
        self.green_line_system = green_line_system
        self.red_line_system = red_line_system

        self.setWindowTitle("Track Controller Test Bench")
        
        
        ##########################################
        #### MAIN LAYOUTS + TITLE
        ##########################################
        self.main_layout = QGridLayout()
        self.ins_outs_layout = QHBoxLayout()
        self.page_title = UI_Help.create_label("TEST BENCH",Fonts.section_font)
        
        ##########################################
        #### CTC INPUTS
        ##########################################
        self.ctc = CTCOffice()

        self.ctc_layout = QGridLayout()
        self.ctc_logs = QTextEdit()
        
        self.txtin_ctc_train_info = QLineEdit("[3,50,15]")
        self.btn_ctc_train_info = QPushButton("Get Train Info\nfrom CTC")
        self.txtin_dispatch_train = QLineEdit("[5,1]")
        self.btn_dispatch_train = QPushButton("CTC Dispatch (wayside 4)")
        self.btn_clear_ctc_logs = QPushButton("Clear")

        self.ctc_layout.addWidget(UI_Help.create_frame(),0,0,1,1)
        self.internal_ctc_layout = QVBoxLayout()
        self.internal_ctc_layout.setContentsMargins(20,20,20,20)
        self.internal_ctc_layout.setSpacing(25)
        self.internal_ctc_layout.addWidget(UI_Help.create_label("CTC Inputs", Fonts.section_font))
        
        self.internal_ctc_layout.addWidget(self.txtin_ctc_train_info)
        self.txtin_ctc_train_info.setFont(Fonts.subsection_font)
        self.internal_ctc_layout.addWidget(self.btn_ctc_train_info)
        self.btn_ctc_train_info.setFont(Fonts.subsection_font)
        self.internal_ctc_layout.addWidget(self.txtin_dispatch_train)
        self.txtin_dispatch_train.setFont(Fonts.subsection_font)
        self.internal_ctc_layout.addWidget(self.btn_dispatch_train)
        self.btn_dispatch_train.setFont(Fonts.subsection_font)
        
        self.internal_ctc_layout.addWidget(self.ctc_logs)
        self.internal_ctc_layout.addWidget(self.btn_clear_ctc_logs)
        self.btn_clear_ctc_logs.setFont(Fonts.subsection_font)
        self.ctc_layout.addLayout(self.internal_ctc_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)

        ##########################################
        #### TRACK INPUTS
        ##########################################
        

        track_model_layout = QGridLayout()
        self.track_logs = QTextEdit()

        self.txtin_get_occupancies = QTextEdit("[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
        self.txtin_get_occupancies.setFont(Fonts.subsection_font)
        self.btn_get_occupancies = QPushButton("Update Block\nStatus List")
        self.btn_get_occupancies.setFont(Fonts.subsection_font)
        self.txtin_get_sw_pos = QLineEdit("0")
        self.txtin_get_sw_pos.setFont(Fonts.subsection_font)
        self.btn_get_sw_pos = QPushButton("Switch\nPosition")
        self.btn_get_sw_pos.setFont(Fonts.subsection_font)
        self.txtin_get_railway = QLineEdit("0")
        self.txtin_get_railway.setFont(Fonts.subsection_font)
        self.btn_get_railway = QPushButton("Railway\nStatus")
        self.btn_get_railway.setFont(Fonts.subsection_font)
        self.txtin_get_light = QLineEdit("[1,1,0]")
        self.txtin_get_light.setFont(Fonts.subsection_font)
        self.btn_get_light = QPushButton("Light\nStatus")
        self.btn_get_light.setFont(Fonts.subsection_font)
        self.btn_clear_tm_logs = QPushButton("Reset Track")
        self.btn_clear_tm_logs.setFont(Fonts.subsection_font)
        
        
        track_model_layout.addWidget(UI_Help.create_frame(),0,0,1,1)
        self.internal_track_model_layout = QVBoxLayout()
        self.internal_track_model_layout.setContentsMargins(20,20,20,20)
        self.internal_track_model_layout.setSpacing(20)
        self.internal_track_model_layout.addWidget(UI_Help.create_label("Track Inputs", Fonts.section_font))
        self.internal_track_model_layout.addWidget(self.txtin_get_occupancies)
        self.internal_track_model_layout.addWidget(self.btn_get_occupancies)
        self.internal_track_model_layout.addWidget(self.txtin_get_sw_pos)
        self.internal_track_model_layout.addWidget(self.btn_get_sw_pos)
        self.internal_track_model_layout.addWidget(self.txtin_get_railway)
        self.internal_track_model_layout.addWidget(self.btn_get_railway)
        self.internal_track_model_layout.addWidget(self.txtin_get_light)
        self.internal_track_model_layout.addWidget(self.btn_get_light)
        self.internal_track_model_layout.addWidget(self.track_logs)
        self.internal_track_model_layout.addWidget(self.btn_clear_tm_logs)
        #self.track_logs.setFixedHeight(265)

        track_model_layout.addLayout(self.internal_track_model_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)
        
        #Dynamic Textbox to show output of PLC
        self.controller_dropdown_layout = QGridLayout()
        self.internal_controller_dropdown_layout = QVBoxLayout()
        self.start_stop_layout = QHBoxLayout()
        self.pickers_layout = QHBoxLayout()

        self.line_dropdown = QComboBox()
        self.controller_dropdown = QComboBox(self.line_dropdown)


        self.pickers_layout.addWidget(self.line_dropdown)
        self.pickers_layout.addWidget(self.controller_dropdown)
        
        
        self.line_list = ["Green","Red"]
        self.default_list = ["Wayside 1", "Wayside 2", "Wayside 3", "Wayside 4", "Wayside 5", "Wayside 6"]
        self.line_dropdown.addItems(self.line_list)
        self.line_dropdown.currentIndexChanged.connect(self.change_tc_list)
        self.controller_dropdown.currentIndexChanged.connect(self.change_tc_view)
        self.controller_dropdown.addItems(self.default_list)

        self.internal_controller_dropdown_layout.setContentsMargins(20,20,20,20)
        self.internal_controller_dropdown_layout.setSpacing(20)
        

        self.controller_dropdown_layout.addWidget(UI_Help.create_frame(),0,0,1,1)
        self.internal_controller_dropdown_layout.addWidget(UI_Help.create_label("Controller To Test", Fonts.section_font))
        self.internal_controller_dropdown_layout.addLayout(self.pickers_layout)
        
        self.internal_controller_dropdown_layout.addLayout(self.start_stop_layout)

        self.controller_dropdown_layout.addLayout(self.internal_controller_dropdown_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)

        #SETTING MAIN LAYOUTS
        self.ins_outs_layout.addLayout(self.ctc_layout)
        self.ins_outs_layout.addLayout(self.controller_dropdown_layout)
        self.ins_outs_layout.addLayout(track_model_layout)
        self.main_layout.addWidget(self.page_title, 0, 0)
        self.main_layout.addLayout(self.ins_outs_layout, 1, 0)
        
        self.connect_backend()
        #self.setLayout(self.main_layout)

        self.main_widget = Color('light blue')
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def connect_backend(self):
        #CTC buttons
        self.btn_ctc_train_info.clicked.connect(self.btn_ctc_train_info_clicked)
        self.btn_dispatch_train.pressed.connect(self.btn_dispatch_train_clicked)
        self.btn_clear_ctc_logs.pressed.connect(self.btn_clear_ctc_logs_clicked)

        #Track buttons
        self.btn_get_occupancies.pressed.connect(self.btn_get_occupancies_clicked)
        self.btn_get_railway.pressed.connect(self.btn_get_railway_clicked)
        self.btn_clear_tm_logs.pressed.connect(self.btn_clear_tm_logs_clicked)

    ##BUTTON FUNCTIONALITY
    def btn_ctc_train_info_clicked(self):
        entered_list = ast.literal_eval(self.txtin_ctc_train_info.text())
        tc_idx = self.controller_dropdown.currentIndex()

        if self.line_dropdown.currentIndex() == 0:
            self.green_line_system.controller_list[tc_idx].set_block_speed_auth(entered_list[0],entered_list[1],entered_list[2])
        else:
            self.red_line_system.controller_list[tc_idx].set_block_speed_auth(entered_list[0],entered_list[1],entered_list[2])

    def btn_dispatch_train_clicked(self):
        if self.line_dropdown.currentIndex() == 0:
            self.green_line_system.controller_list[3].set_switch(1)
        else:
            self.red_line_system.controller_list[1].set_switch(1)
        
    def btn_get_occupancies_clicked(self):
        entered_list = self.txtin_get_occupancies.toPlainText()
        tc_idx = self.controller_dropdown.currentIndex()
        if self.line_dropdown.currentIndex() == 0:
            self.green_line_system.controller_list[tc_idx].set_block(ast.literal_eval(entered_list))
        else:
            self.red_line_system.controller_list[tc_idx].set_block(ast.literal_eval(entered_list))

    def btn_get_railway_clicked(self):
        entered_val = self.txtin_get_occupancies.toPlainText()
        tc_idx = self.controller_dropdown.currentIndex()
        if self.line_dropdown.currentIndex() == 0:
            self.green_line_system.controller_list[tc_idx].set_crossing(entered_val)
        else:
            self.red_line_system.controller_list[tc_idx].set_crossing(entered_val)

    def btn_clear_tm_logs_clicked(self):
        self.track_logs.clear()

    def btn_clear_ctc_logs_clicked(self):
        self.ctc_logs.clear()

    def change_tc_list(self, index):
        self.controller_dropdown.clear()
        if index == 0:
            self.controller_dropdown.addItems(["Wayside 1","Wayside 2","Wayside 3","Wayside 4","Wayside 5","Wayside 6"])
        elif index == 1:
            self.controller_dropdown.addItems(["Wayside 7","Wayside 8","Wayside 9","Wayside 10","Wayside 11"])
    
    def change_tc_view(self, index):
        if self.line_dropdown.currentIndex() == 0:
            if index == 0:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 1:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 2:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 3:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 4:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 5:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
        elif self.line_dropdown.currentIndex() == 1:
            if index == 0:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 1:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0]")
            elif index == 2:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 3:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")
            elif index == 4:
                self.txtin_get_occupancies.setText("[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]")

class UploadPage(QWidget):
    def __init__(self, green_line_system, red_line_system):
        super().__init__()
        self.green_line_system = green_line_system
        self.red_line_system = red_line_system

        self.main_layout = QVBoxLayout(self)
        self.page_title = UI_Help.create_label("UPLOAD PAGE",Fonts.section_font)

        self.line_dropdown = QComboBox()
        self.controller_dropdown = QComboBox(self.line_dropdown)
        
        self.dropdown_layout = QGridLayout()#main dropdown layout
        self.internal_dropdown_layout = QVBoxLayout()#align subsection title over dropdowns
        
        self.pickers_layout = QHBoxLayout()#dropdowns next to each other, line->controller
        self.internal_dropdown_layout.setContentsMargins(20,20,20,20)
        self.internal_dropdown_layout.setSpacing(10)
        self.pickers_layout.addWidget(self.line_dropdown)
        self.pickers_layout.addWidget(self.controller_dropdown)
        self.internal_dropdown_layout.addWidget(UI_Help.create_label("Choose Controller and Path For Upload:",Fonts.subsection_font))
        self.internal_dropdown_layout.addLayout(self.pickers_layout)

        self.import_layout = QHBoxLayout()
    
        self.txtin_import_file = QLineEdit()

        self.btn_import_file = QPushButton("Import")
        self.btn_import_file.setFont(Fonts.subsection_font)

        self.import_layout.addWidget(self.txtin_import_file)
        self.import_layout.addWidget(self.btn_import_file)

        self.internal_dropdown_layout.addLayout(self.import_layout)
        self.dropdown_frame = UI_Help.create_frame()
        self.dropdown_layout.addWidget(self.dropdown_frame,0,0,1,1)
        self.dropdown_layout.addLayout(self.internal_dropdown_layout,0,0,1,1)# Qt.AlignmentFlag.AlignTop)

        #Dropdown connections
        self.line_list = ["Green","Red"]
        self.line_dropdown.addItems(self.line_list)
        self.line_dropdown.currentIndexChanged.connect(self.change_tc_list)

        self.controller_list = ["Wayside 1","Wayside 2","Wayside 3","Wayside 4","Wayside 5","Wayside 6"]#default selection
        self.controller_dropdown.addItems(self.controller_list)

        #File read section
        self.file_read_layout = QGridLayout()
        self.internal_file_read_layout = QVBoxLayout()
        self.internal_file_read_layout.setContentsMargins(20,20,20,20)
        self.internal_file_read_layout.setSpacing(10)

        self.test_file_read = QTextEdit()
        self.test_file_read.setFont(Fonts.subsection_font)

        self.btn_upload_file = QPushButton("Upload File To Selected Controller")
        self.btn_upload_file.setFont(Fonts.subsection_font)

        self.internal_file_read_layout.addWidget(UI_Help.create_label("File will show here when chosen:",Fonts.subsection_font))
        self.internal_file_read_layout.addWidget(self.test_file_read)
        self.internal_file_read_layout.addWidget(self.btn_upload_file)

        self.file_read_frame = UI_Help.create_frame()
        self.file_read_layout.addWidget(self.file_read_frame,0,0,1,1)
        self.file_read_layout.addLayout(self.internal_file_read_layout,0,0,1,1)

        self.main_layout.addWidget(self.page_title)
        self.main_layout.addLayout(self.dropdown_layout)
        self.main_layout.addLayout(self.file_read_layout)

        #CONNECTIONS
        self.btn_import_file.clicked.connect(self.import_file)
        self.btn_upload_file.clicked.connect(self.upload_file)

        self.setLayout(self.main_layout)
    
    def change_tc_list(self, index):
        self.controller_dropdown.clear()
        if index == 0:
            self.controller_dropdown.addItems(["Wayside 1","Wayside 2","Wayside 3","Wayside 4","Wayside 5","Wayside 6"])
        elif index == 1:
            self.controller_dropdown.addItems(["Wayside 7","Wayside 8","Wayside 9","Wayside 10","Wayside 11"])
    
    #opens file explorer of directory entered in file_path
    def import_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Text File', '', 'Text Files (*.txt)')
        if filename:
            with open(filename, 'r') as file:
                self.test_file_read.setText(file.read())
                #self.txtin_import_file.setText(os.path.basename(filename))
                self.txtin_import_file.setText(filename)
    
    def upload_file(self):
        selected_controller = self.controller_dropdown.currentText()
        selected_controller = selected_controller.replace("Wayside ","")
        if int(selected_controller) in [1,2,3,4,5,6]:
            self.green_line_system.controller_list[int(selected_controller)-1].set_main_program(self.txtin_import_file.text())
        else:
            self.red_line_system.controller_list[int(selected_controller)-1].set_main_program(self.txtin_import_file.text())

#class ViewSignals(QObject):
#    manual_switch_sig = Signal(int,int,int,str)

class ControllerView(QWidget):
    def __init__(self, green_line_system, red_line_system):
        super().__init__()
        self.green_line_system = green_line_system
        self.red_line_system = red_line_system
        self.main_layout = QVBoxLayout(self)
        self.page_title = UI_Help.create_label("CONTROLLER VIEW",Fonts.section_font)

        #self.signals = ViewSignals()
        # Program Run Timing
        self.green_timer = QTimer()
        self.green_timer.timeout.connect(self.loop_green_waysides)
        self.green_timer.setInterval(1000)
        self.red_timer = QTimer()
        self.red_timer.timeout.connect(self.loop_red_waysides)
        self.red_timer.setInterval(1000)
        self.is_paused = False

        ##########################################
        #### TRACK CONTROLLER DROP DOWN
        ##########################################
        self.line_dropdown = QComboBox()
        self.controller_dropdown = QComboBox(self.line_dropdown)
        
        self.dropdown_layout = QGridLayout()#main dropdown layout
        self.internal_dropdown_layout = QVBoxLayout()#align subsection title over dropdowns
        
        self.pickers_layout = QHBoxLayout()#dropdowns next to each other, line->controller
        self.internal_dropdown_layout.setContentsMargins(20,20,20,20)
        self.internal_dropdown_layout.setSpacing(20)
        self.pickers_layout.addWidget(self.line_dropdown)
        self.pickers_layout.addWidget(self.controller_dropdown)
        self.internal_dropdown_layout.addWidget(UI_Help.create_label("Choose Controller To View:",Fonts.subsection_font))
        self.internal_dropdown_layout.addLayout(self.pickers_layout)
        self.dropdown_frame = UI_Help.create_frame()
        #self.dropdown_frame.setFixedHeight(75)
        self.dropdown_layout.addWidget(self.dropdown_frame,0,0,1,1)
        self.dropdown_layout.addLayout(self.internal_dropdown_layout,0,0,1,1)# Qt.AlignmentFlag.AlignTop)

        #Dropdown connections
        self.line_list = ["Green","Red"]
        self.line_dropdown.addItems(self.line_list)
        self.line_dropdown.currentIndexChanged.connect(self.change_tc_list)

        self.controller_list = ["Wayside 1","Wayside 2","Wayside 3","Wayside 4","Wayside 5","Wayside 6"]#default selection
        self.controller_dropdown.addItems(self.controller_list)
        self.prev_controller_idxs = None
        self.first_run = True
        self.controller_dropdown.currentIndexChanged.connect(self.change_tc_view)

        ##########################################
        #### PROGRAM INFO
        ##########################################

        ###MAIN FILE LAYOUT
        self.main_file_layout = QGridLayout()
        self.internal_main_file_layout = QVBoxLayout()
        self.internal_main_file_layout.setContentsMargins(20,20,20,20)
        self.internal_main_file_layout.setSpacing(10)

        self.tc_plc_main_file_view = QTextEdit()

        self.main_file_label = UI_Help.create_label("Main File:",Fonts.subsection_font)
        self.internal_main_file_layout.addWidget(self.main_file_label)
        self.internal_main_file_layout.addWidget(self.tc_plc_main_file_view)

        self.main_file_frame = UI_Help.create_frame()
        #self.main_file_frame.setFixedHeight(350)
        self.main_file_layout.addWidget(self.main_file_frame,0,0,1,1)
        self.main_file_layout.addLayout(self.internal_main_file_layout,0,0,1,1)


        ###MAINTENANCE MODE LAYOUT
        self.maintenance_layout = QGridLayout()
        self.internal_maintenance_layout = QVBoxLayout()
        self.internal_maintenance_layout.setContentsMargins(20,20,20,20)
        self.internal_maintenance_layout.setSpacing(1)

        self.tc_maintenance_toggle = UI_Help.create_anim_btn_feild("Maintenance mode",AnimatedToggle())
        #self.tc_maintenance_toggle = QCheckBox("test")

        #self.internal_maintenance_layout.addWidget(self.maintenance_label)
        self.internal_maintenance_layout.addLayout(self.tc_maintenance_toggle)

        self.tc_maintenance_toggle.itemAt(1).widget().stateChanged.connect(self.handle_animated_toggle)

        self.switch_button_layout = QVBoxLayout()
        self.tc_switch_label = UI_Help.create_label("Current Position: Left",Fonts.subsection_font)
        self.btn_set_switch = QPushButton("Toggle Switch")
        self.btn_set_switch.setFont(Fonts.subsection_font)

        self.btn_set_switch.clicked.connect(self.handle_set_switch_btn)

        self.switch_button_layout.addWidget(self.tc_switch_label)
        self.switch_button_layout.addWidget(self.btn_set_switch)
        self.internal_maintenance_layout.addLayout(self.switch_button_layout)

        self.maintenance_frame = UI_Help.create_frame()
        self.maintenance_layout.addWidget(self.maintenance_frame,0,0,1,1)
        self.maintenance_layout.addLayout(self.internal_maintenance_layout,0,0,1,1)

        ###VAR FILE LAYOUT
        self.var_file_layout = QGridLayout()
        self.internal_var_file_layout = QVBoxLayout()
        self.internal_var_file_layout.setContentsMargins(20,20,20,20)
        self.internal_var_file_layout.setSpacing(10)

        self.tc_plc_var_file_view = QTextEdit()

        self.var_file_label = UI_Help.create_label("PLC Variables:",Fonts.subsection_font)
        self.internal_var_file_layout.addWidget(self.var_file_label)
        self.internal_var_file_layout.addWidget(self.tc_plc_var_file_view)

        self.var_file_frame = UI_Help.create_frame()
        #self.var_file_frame.setFixedHeight(350)
        self.var_file_layout.addWidget(self.var_file_frame,0,0,1,1)
        self.var_file_layout.addLayout(self.internal_var_file_layout,0,0,1,1)

        self.files_layout = QHBoxLayout()#main file layout
        self.files_layout.addLayout(self.main_file_layout)
        self.files_layout.addLayout(self.maintenance_layout)
        self.files_layout.addLayout(self.var_file_layout)

        ###OUTPUT LAYOUT
        self.output_layout = QGridLayout()
        self.internal_output_layout = QVBoxLayout()
        self.internal_output_layout.setContentsMargins(20,20,20,20)
        self.internal_output_layout.setSpacing(10)

        self.tc_plc_output_view = QTextEdit()
        self.btn_tc_temp_run = QPushButton("Start Selected\nSystem")
        self.btn_tc_temp_stop = QPushButton("Stop Selected\nSystem")

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.btn_tc_temp_run)
        self.button_layout.addWidget(self.btn_tc_temp_stop)
        self.btn_tc_temp_run.clicked.connect(self.run_selected_system)
        self.btn_tc_temp_stop.clicked.connect(self.stop_selected_system)

        #real defaults
        self.tc_plc_main_file_view.setText(self.green_line_system.controller_list[0].main_body)
        self.tc_plc_var_file_view.setText(self.green_line_system.controller_list[0].var_body)
        #self.tc_plc_output_view.setText("program not running")

        self.line_dropdown.setCurrentIndex(0)
        self.controller_dropdown.setCurrentIndex(0)
        self.tc_plc_output_view.setText("WAYSIDE 1 OUTPUT")

        self.output_label = UI_Help.create_label("Program Output:",Fonts.subsection_font)
        self.internal_output_layout.addWidget(self.output_label)
        self.internal_output_layout.addWidget(self.tc_plc_output_view)
        self.internal_output_layout.addLayout(self.button_layout)

        self.output_frame = UI_Help.create_frame()
        self.output_layout.addWidget(self.output_frame,0,0,1,1)
        self.output_layout.addLayout(self.internal_output_layout,0,0,1,1)
        
        ###BUILDING MAIN LAYOUT (COMBINING LAYOUTS)
        self.main_layout.addWidget(self.page_title)
        self.main_layout.addLayout(self.dropdown_layout)
        self.main_layout.addLayout(self.files_layout)
        self.main_layout.addLayout(self.output_layout)

        self.setLayout(self.main_layout)

    def handle_set_switch_btn(self):
        #curr_controller = [self.line_dropdown,self.controller_dropdown]

        if self.tc_switch_label.text() == "Current Position: Left":
            self.tc_switch_label.setText("Current Position: Right")
        else:
            self.tc_switch_label.setText("Current Position: Left")

    def handle_animated_toggle(self):
        if self.tc_maintenance_toggle.itemAt(1).widget()._handle_position == 0.0:
            if self.line_dropdown.currentIndex() == 0:
                self.green_timer.stop()
            elif self.line_dropdown.currentIndex() == 1:
                self.red_timer.stop()
        else:
            if self.line_dropdown.currentIndex() == 0:
                self.green_timer.start(1000)
            elif self.line_dropdown.currentIndex() == 1:
                self.red_timer.start(1000)
    
    def change_tc_list(self, index):
        self.controller_dropdown.clear()
        if index == 0:
            self.controller_dropdown.addItems(["Wayside 1","Wayside 2","Wayside 3","Wayside 4","Wayside 5","Wayside 6"])
        elif index == 1:
            self.controller_dropdown.addItems(["Wayside 7","Wayside 8","Wayside 9","Wayside 10","Wayside 11"])

    def change_tc_view(self, controller):
        if controller != -1:
            self.tc_plc_output_view.clear()

            if self.line_dropdown.currentIndex() == 0:
                self.tc_plc_output_view.append(f"WAYSIDE {self.green_line_system.controller_list[controller].id} OUTPUT")
            else:
                self.tc_plc_output_view.append(f"WAYSIDE {self.red_line_system.controller_list[controller].id} OUTPUT")

            if self.line_dropdown.currentIndex() == 0:
                if self.green_line_system.controller_list[controller].main_body:
                    self.tc_plc_main_file_view.setText(self.green_line_system.controller_list[controller].main_body)
                else:
                    self.tc_plc_main_file_view.setText("green no file uploaded")
                
                if self.green_line_system.controller_list[controller].var_body:
                    self.tc_plc_var_file_view.setText(self.green_line_system.controller_list[controller].var_body)
                else:
                    self.tc_plc_var_file_view.setText("green no file uploaded")
                
                if not self.first_run:
                    if self.prev_controller_idxs[0] == 0:
                        if self.green_line_system.controller_list[self.prev_controller_idxs[1]].program != None:
                            self.green_line_system.controller_list[self.prev_controller_idxs[1]].program.signals.return_val_sig.disconnect(self.show_output)
                    elif self.prev_controller_idxs[0] == 1:
                        if self.red_line_system.controller_list[self.prev_controller_idxs[1]].program != None:
                            self.red_line_system.controller_list[self.prev_controller_idxs[1]].program.signals.return_val_sig.disconnect(self.show_output)  
                    
                if self.green_line_system.controller_list[controller].program != None:
                    self.green_line_system.controller_list[controller].program.signals.return_val_sig.connect(self.show_output)
                
            elif self.line_dropdown.currentIndex() == 1:
                if self.red_line_system.controller_list[controller].main_body:
                    self.tc_plc_main_file_view.setText(self.red_line_system.controller_list[controller].main_body)
                else:
                    self.tc_plc_main_file_view.setText("red no file uploaded")
                
                if self.red_line_system.controller_list[controller].var_body:
                    self.tc_plc_var_file_view.setText(self.red_line_system.controller_list[controller].var_body)
                else:
                    self.tc_plc_var_file_view.setText("red no file uploaded")
                
                if not self.first_run:
                    if self.prev_controller_idxs[0] == 0:
                        if self.green_line_system.controller_list[self.prev_controller_idxs[1]].program != None:
                            self.green_line_system.controller_list[self.prev_controller_idxs[1]].program.signals.return_val_sig.disconnect(self.show_output)
                    elif self.prev_controller_idxs[0] == 1:
                        if self.red_line_system.controller_list[self.prev_controller_idxs[1]].program != None:
                            self.red_line_system.controller_list[self.prev_controller_idxs[1]].program.signals.return_val_sig.disconnect(self.show_output)

                if self.red_line_system.controller_list[controller].program != None:
                    self.red_line_system.controller_list[controller].program.signals.return_val_sig.connect(self.show_output)
            
            if self.prev_controller_idxs != [self.line_dropdown.currentIndex(),self.controller_dropdown.currentIndex()]:
                self.prev_controller_idxs = [self.line_dropdown.currentIndex(),self.controller_dropdown.currentIndex()]

            self.first_run = False

    def show_output(self, text):
        tc_idx = self.controller_dropdown.currentIndex()
        if self.line_dropdown.currentIndex() == 0:
            self.tc_plc_main_file_view.setText(self.green_line_system.controller_list[tc_idx].main_body)
            self.tc_plc_var_file_view.setText(self.green_line_system.controller_list[tc_idx].var_body)
        else:
            self.tc_plc_main_file_view.setText(self.red_line_system.controller_list[tc_idx].main_body)
            self.tc_plc_var_file_view.setText(self.red_line_system.controller_list[tc_idx].var_body)

        self.tc_plc_output_view.clear()
        self.tc_plc_output_view.append("============================================")
        self.tc_plc_output_view.append(f"LOCATION: {text[10].elements[0]}    SPEED: {text[10].elements[1]}    AUTHORITY: {text[10].elements[2]}")
        self.tc_plc_output_view.append(f"UPDATED SWITCH POSITION: {text[11]}")
        self.tc_plc_output_view.append(f"UPDATED LIGHTS LIST: {text[12]}")
        if (self.line_dropdown.currentIndex() == 0 and self.controller_dropdown.currentIndex() == 0) or (self.line_dropdown.currentIndex() == 1 and self.controller_dropdown.currentIndex() == 3):
            self.tc_plc_output_view.append(f"UPDATED CROSSING VAL: {text[13]}")
        #self.tc_plc_output_view.append(f"SWITCH LOCATION: {text[14]}")
        self.tc_plc_output_view.append("============================================")

    def handle_system_pause(self, state : bool):
        self.is_paused = state
        print(f"[TRACK CONTROLLER]: Received new pause/resume, state = {state}")
        if self.is_paused:
            self.green_timer.stop()
            # self.red_timer.stop()
        else:
            self.green_timer.start()
            # self.red_timer.start()


    def run_selected_system(self):
        self.tc_plc_output_view.clear()
        curr_controller_selected = self.controller_dropdown.currentIndex()

        if self.line_dropdown.currentIndex() == 0:
            self.green_stop_flag = False
            self.green_line_system.create_waysides()
            self.tc_plc_output_view.append(f"WAYSIDE {self.green_line_system.controller_list[curr_controller_selected].id} OUTPUT")
            if self.green_line_system.controller_list[curr_controller_selected].program != None:
                self.green_line_system.controller_list[curr_controller_selected].program.signals.return_val_sig.connect(self.show_output)

            self.green_timer.start()

        elif self.line_dropdown.currentIndex() == 1:
            self.red_stop_flag = False
            self.red_line_system.create_waysides()
            self.tc_plc_output_view.append(f"WAYSIDE {self.red_line_system.controller_list[curr_controller_selected].id} OUTPUT")
            if self.red_line_system.controller_list[curr_controller_selected].program != None:
                self.red_line_system.controller_list[curr_controller_selected].program.signals.return_val_sig.connect(self.show_output)

            self.red_timer.start()
        
        self.prev_controller_idxs = [self.line_dropdown.currentIndex(), self.controller_dropdown.currentIndex()]

    def loop_green_waysides(self):
        self.green_line_system.run_waysides_one_step()

    def loop_red_waysides(self):
        self.red_line_system.run_waysides_one_step()

    def stop_selected_system(self):
        if self.line_dropdown.currentIndex() == 0:
            self.green_stop_flag = True
            self.green_line_system.stop_waysides()
            self.green_timer.stop()
        else:
            self.red_stop_flag = True
            self.red_line_system.stop_waysides()
            self.red_timer.stop()