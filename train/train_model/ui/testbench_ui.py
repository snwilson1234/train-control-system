from train.train_model.ui.ui_help import *
from dataclasses import dataclass
from train.train_model.inc.util import Conv_Globals
from train.core.mock_beacon import Beacon

@dataclass
class Direct_Info:
    grade_data : float = 0.0
    block_length_data: int = 0
    passengers_boarding_data: int  = 0
    track_power_fail_data: bool = False
    entered_new_block: bool = False

@dataclass
class PID_Gains:
    kp : float = 0.0
    ki : float = 0.0

class TestBench(QMainWindow):

    frame_margins = 15
    content_margins_arg = [frame_margins, frame_margins, frame_margins, frame_margins]

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test Bench")

        ##########################################
        #### Line Edits
        ##########################################
        self.station_side_le = QLineEdit()
        self.station_name_le = QLineEdit()
        self.tunnel_toggle_le = QLineEdit()
        self.grade_le = QLineEdit()
        self.block_length_le = QLineEdit()
        self.track_power_fail_le = QLineEdit()
        self.entered_new_block_le = QLineEdit()
        self.passengers_onboarding_le = QLineEdit()
        self.commanded_speed_le = QLineEdit()
        self.authority_le = QLineEdit()

        self.kp_le = QLineEdit()
        self.ki_le = QLineEdit()
        self.power_command_le = QLineEdit()

        self.set_temp_le = QLineEdit()

        self.out_commanded_speed_le = QLineEdit()
        self.out_actual_speed_le = QLineEdit()
        self.out_authority_le = QLineEdit()
        self.out_position_le = QLineEdit()
        self.out_station_name_le = QLineEdit()
        self.out_station_side_le = QLineEdit()
        self.out_tunnel_toggle_le = QLineEdit()
        self.input_power_command_le = QLineEdit()
        
        self.speed_up_le = QLineEdit()

        ##########################################
        #### Double Spin Boxes
        ##########################################
        self.commanded_speed_dsb = QDoubleSpinBox()
        self.commanded_speed_dsb.setFixedHeight(40)
        self.commanded_speed_dsb.setMaximum(1000.0)
        self.commanded_speed_dsb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ##########################################
        #### Text Edits
        ##########################################
        self.announcements_te = UI_Help.create_text_edit()
        self.advertisements_te =  UI_Help.create_text_edit()
        self.announcements_te.setFixedHeight(50)
        self.advertisements_te.setFixedHeight(50)

        ##########################################
        #### Data
        ##########################################
        self.DI = Direct_Info()
        self.gains = PID_Gains()

        self.authority_data = 0 
        self.commanded_speed_data = 0

        ##########################################
        #### Send Buttons
        ##########################################
        self.send_beacon_data_btn = QPushButton(text="Send Beacon Data")
        self.send_direct_info = QPushButton(text="Send Direct Info")
        self.send_announcement_btn = QPushButton(text="Send Announcement")
        self.send_advertisement_btn = QPushButton(text="Send Advertisement")
        self.send_track_circuit_btn = QPushButton(text="Send Track Circuit Data")
        self.send_all_inputs_btn = QPushButton(text="Send All Inputs")
        self.send_gains_btn = QPushButton(text="Send PID Gains")

        ##########################################
        #### Other Buttons
        ##########################################
        self.driver_ebrake_btn = QPushButton(text="EMERGENCY BRAKE")
        font = Fonts.normal_font
        font.setBold(True)
        self.driver_ebrake_btn.setFont(font)
        self.driver_ebrake_btn.setStyleSheet("background-color:#AA3333")

        self.exterior_lights_btn = AnimatedToggle()
        self.interior_lights_btn = AnimatedToggle()
        self.right_doors_btn = AnimatedToggle()
        self.left_doors_btn = AnimatedToggle()

        self.train_engine_fail_btn = QPushButton("Train Engine Failure")
        self.signal_pickup_failure_btn = QPushButton("Signal Pickup Failure")
        self.brake_failure_btn = QPushButton("Brake Failure")
        self.pass_ebrake_btn = QPushButton("Passenger EBrake")
        self.train_engine_fail_btn.setStyleSheet("")
        self.signal_pickup_failure_btn.setStyleSheet("")
        self.brake_failure_btn.setStyleSheet("")
        self.pass_ebrake_btn.setStyleSheet("")

        ##########################################
        #### Left Panel
        ##########################################
        left_panel_layout = QVBoxLayout()
        
        beacon_data_layout = QGridLayout()
        beacon_data_layout.addWidget(UI_Help.create_frame())
        beacon_data_frame_layout = QVBoxLayout()
        beacon_data_frame_layout.addWidget(UI_Help.create_label("Beacon Data", Fonts.tui_section_header, 'black'))
        beacon_data_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        beacon_data_frame_layout.addLayout(UI_Help.create_input_field("Station Side (char: R,L)", self.station_side_le))
        beacon_data_frame_layout.addLayout(UI_Help.create_input_field("Station Name (str)", self.station_name_le))
        beacon_data_frame_layout.addLayout(UI_Help.create_input_field("Tunnel Toggle (bool)", self.tunnel_toggle_le))
        beacon_data_frame_layout.addWidget(self.send_beacon_data_btn)
        beacon_data_layout.addLayout(beacon_data_frame_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)

        direct_info_layout = QGridLayout()
        direct_info_layout.addWidget(UI_Help.create_frame())
        direct_info_frame_layout = QVBoxLayout()
        direct_info_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        direct_info_frame_layout.addWidget(UI_Help.create_label("Direct Information", Fonts.tui_section_header, 'black'))
        direct_info_frame_layout.addLayout(UI_Help.create_input_field("Grade (%)", self.grade_le))
        direct_info_frame_layout.addLayout(UI_Help.create_input_field("Block Length (m)", self.block_length_le))
        direct_info_frame_layout.addLayout(UI_Help.create_input_field("Passengers Boarding (#)", self.passengers_onboarding_le))
        direct_info_frame_layout.addLayout(UI_Help.create_input_field("Track Power Failure (bool)", self.track_power_fail_le))
        direct_info_frame_layout.addLayout(UI_Help.create_input_field("Entered New Block (bool)", self.entered_new_block_le))
        direct_info_frame_layout.addWidget(self.send_direct_info)
        direct_info_layout.addLayout(direct_info_frame_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)

        trip_info_track_circuit_layout = QGridLayout()
        trip_info_track_circuit_layout.addWidget(UI_Help.create_frame())
        trip_info_track_circuit_frame_layout = QVBoxLayout()
        trip_info_track_circuit_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        trip_info_track_circuit_frame_layout.addWidget(UI_Help.create_label("Announcements", Fonts.tui_section_header, 'black'))
        trip_info_track_circuit_frame_layout.addWidget(self.announcements_te)
        trip_info_track_circuit_frame_layout.addWidget(self.send_announcement_btn)
        trip_info_track_circuit_frame_layout.addWidget(UI_Help.create_label("Advertisements", Fonts.tui_section_header, 'black'))
        trip_info_track_circuit_frame_layout.addWidget(self.advertisements_te)
        trip_info_track_circuit_frame_layout.addWidget(self.send_advertisement_btn)
        trip_info_track_circuit_frame_layout.addWidget(UI_Help.create_label("Track Circuit Data", Fonts.tui_section_header, 'black'))
        trip_info_track_circuit_frame_layout.addLayout(UI_Help.create_input_field("Commanded Speed (m/s)", self.commanded_speed_le))
        trip_info_track_circuit_frame_layout.addLayout(UI_Help.create_input_field("Authority (blocks)", self.authority_le))
        trip_info_track_circuit_frame_layout.addWidget(self.send_track_circuit_btn)
        trip_info_track_circuit_layout.addLayout(trip_info_track_circuit_frame_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)

        send_all_layout = QGridLayout()
        send_all_layout.addWidget(UI_Help.create_frame())
        send_all_frame_layout = QVBoxLayout()
        send_all_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        send_all_frame_layout.addWidget(UI_Help.create_label("Send All Inputs", Fonts.tui_section_header, 'black'))
        send_all_frame_layout.addWidget(self.send_all_inputs_btn)
        send_all_layout.addLayout(send_all_frame_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)

        train_model_settings_layout = QGridLayout()
        train_model_settings_layout.addWidget(UI_Help.create_frame())
        train_model_settings_frame_layout = QVBoxLayout()
        train_model_settings_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        train_model_settings_frame_layout.addLayout(UI_Help.create_input_field("Model Speed Up (Float)", self.speed_up_le, False))
        train_model_settings_layout.addLayout(train_model_settings_frame_layout, 0,0,1,1, Qt.AlignmentFlag.AlignTop)


        left_panel_layout.addWidget(UI_Help.create_label("Train Inputs", Fonts.tui_block_header))
        left_panel_layout.addLayout(beacon_data_layout)
        left_panel_layout.addLayout(direct_info_layout)
        left_panel_layout.addLayout(trip_info_track_circuit_layout)
        left_panel_layout.addLayout(send_all_layout)
        left_panel_layout.addWidget(UI_Help.create_label("Train Model Settings", Fonts.tui_block_header))
        left_panel_layout.addLayout(train_model_settings_layout)
        left_panel_layout.addStretch()        

        ##########################################
        #### Right Panel
        ##########################################
        right_panel_layout = QVBoxLayout()

        driver_layout = QGridLayout()
        driver_layout.addWidget(UI_Help.create_frame())
        driver_frame_layout = QVBoxLayout()
        driver_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        driver_commanded_speed_layout = QVBoxLayout()
        driver_commanded_speed_layout.addWidget(UI_Help.create_label("Commanded Speed (mph):", None))
        driver_commanded_speed_layout.addWidget(self.commanded_speed_dsb)
        driver_commanded_speed_layout.addLayout(UI_Help.create_input_field("Power Command (W):", self.input_power_command_le, True))
        driver_frame_layout.addLayout(driver_commanded_speed_layout)
        driver_frame_layout.addWidget(self.driver_ebrake_btn)
        driver_layout.addLayout(driver_frame_layout,0,0,1,1)
        
        train_engineer_layout = QGridLayout()
        train_engineer_layout.addWidget(UI_Help.create_frame())
        train_engineer_frame_layout = QVBoxLayout()
        train_engineer_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        train_engineer_frame_layout.addLayout(UI_Help.create_input_field("Kp", self.kp_le))
        train_engineer_frame_layout.addLayout(UI_Help.create_input_field("Ki", self.ki_le))
        train_engineer_frame_layout.addWidget(self.send_gains_btn)
        train_engineer_layout.addLayout(train_engineer_frame_layout,0,0,1,1)
        
        train_interfaces_layout = QGridLayout()
        train_interfaces_layout.addWidget(UI_Help.create_frame())
        train_interfaces_frame_layout = QVBoxLayout()
        train_interfaces_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        train_interfaces_frame_layout.addLayout(UI_Help.create_anim_btn_field("Exterior Lights", self.exterior_lights_btn))
        train_interfaces_frame_layout.addLayout(UI_Help.create_anim_btn_field("Interior Lights", self.interior_lights_btn))
        train_interfaces_frame_layout.addLayout(UI_Help.create_anim_btn_field("Right Doors", self.right_doors_btn))
        train_interfaces_frame_layout.addLayout(UI_Help.create_anim_btn_field("Left Doors", self.left_doors_btn))
        train_interfaces_frame_layout.addLayout(UI_Help.create_input_field("Set Temp (F)", self.set_temp_le))
        train_interfaces_layout.addLayout(train_interfaces_frame_layout, 0,0,1,1)

        train_outputs_layout = QGridLayout()
        train_outputs_layout.addWidget(UI_Help.create_frame())
        train_outputs_frame_layout = QVBoxLayout()
        train_outputs_frame_layout.setContentsMargins(*TestBench.content_margins_arg)
        train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Commanded Speed (m/s)", self.out_commanded_speed_le, True))
        train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Actual Speed (m/s)", self.out_actual_speed_le, True))
        train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Authority (blocks)", self.out_authority_le, True))
        # train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Position (m)", self.out_position_le, True))
        train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Station Side (char)", self.out_station_side_le, True))
        train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Station Name (str)", self.out_station_name_le, True))
        train_outputs_frame_layout.addLayout(UI_Help.create_input_field("Tunnel Toggle (bool)", self.out_tunnel_toggle_le, True))
        train_outputs_frame_layout.addWidget(self.train_engine_fail_btn)
        train_outputs_frame_layout.addWidget(self.brake_failure_btn)
        train_outputs_frame_layout.addWidget(self.signal_pickup_failure_btn)
        train_outputs_frame_layout.addWidget(self.pass_ebrake_btn)
        train_outputs_layout.addLayout(train_outputs_frame_layout,0,0,1,1)

        right_panel_layout.addWidget(UI_Help.create_label("Train Controller / Driver / Engineer", Fonts.tui_block_header))
        right_panel_layout.addLayout(driver_layout)
        right_panel_layout.addLayout(train_interfaces_layout)
        right_panel_layout.addLayout(train_engineer_layout)
        right_panel_layout.addWidget(UI_Help.create_label("Train Outputs (Read Only)", Fonts.tui_block_header))
        right_panel_layout.addLayout(train_outputs_layout, Qt.AlignmentFlag.AlignTop)
        right_panel_layout.addStretch()

        
        ##########################################
        #### Final Layout
        ##########################################
        tb_layout = QHBoxLayout()
        tb_layout.addLayout(left_panel_layout)
        tb_layout.addLayout(right_panel_layout)

        widget = Color('light blue')
        widget.setLayout(tb_layout)
        self.setCentralWidget(widget)


    ##########################################
    #### Direct Info 
    ##########################################

    def send_direct_info_btn_clicked(self) -> Direct_Info:
        try: self.DI.grade_data = float(self.grade_le.text())
        except ValueError: print("[TRAIN]: Invalid format in Grade")

        try: self.DI.block_length_data = int(self.block_length_le.text())
        except ValueError: print("[TRAIN]: Invalid format in block length")

        try: self.DI.passengers_boarding_data = int(self.passengers_onboarding_le.text())
        except ValueError: 
            self.DI.passengers_boarding_data = 0
            print("[TRAIN]: invalid format for passengers boarding")

        if(self.track_power_fail_le.text() == "True"):
            self.DI.track_power_fail_data = True
        elif(self.track_power_fail_le.text() == "False"):
            self.DI.track_power_fail_data = False
        else:
            print("[TRAIN]: invalid format for track power fail")

        if(self.entered_new_block_le.text() == "True"):
            self.DI.entered_new_block = True
        else:
            self.DI.entered_new_block = False

        return self.DI
    
    ##########################################
    #### Track Circuit 
    ##########################################
    
    def send_track_circuit_btn_clicked(self) -> tuple:
        try:
            self.authority_data = int(self.authority_le.text())
        except ValueError:
            print("[TRAIN]: Invalid format in authority")

        try:
            self.commanded_speed_data = float(self.commanded_speed_le.text())
        except ValueError:
            print("[TRAIN]: Invalid format in commanded_speed")

        return (self.commanded_speed_data, self.authority_data)
    
    def set_out_track_circuit_data(self, vals : tuple) -> None:
        self.out_commanded_speed_le.setText(str(vals[0]))
        self.out_authority_le.setText(str(vals[1]))

    ##########################################
    #### Train Engineer
    ##########################################

    def send_PID_gains_btn_clicked(self) -> tuple:
        
        try:
            self.gains.kp = float(self.kp_le.text())
        except ValueError:
            print("[TRAIN]: invalid kp format")

        try:
            self.gains.ki = float(self.ki_le.text())
        except ValueError:
            print("[TRAIN]: invalid ki format")

        return self.gains


    ##########################################
    #### Beacon
    ##########################################

    def send_beacon_data_btn_clicked(self) -> Beacon:
        s_name = self.station_name_le.text()
        s_side = self.station_side_le.text()
        print(f"[TRAIN]: s_side: {s_side}")

        if s_side != "L" and s_side != "R" and s_side != "LR":
            s_side = ""
            print("[TRAIN]: Error in station side data")

        toggle = self.tunnel_toggle_le.text()
        if toggle == "1":
            toggle = True
        elif toggle == "0":
            toggle = False
        else:
            toggle = False
            print("[TRAIN]: Error in tunnel toggle data")
        
        return Beacon(s_side, s_name, toggle)
    
    def update_beacon_out_data(self, data : tuple):
        self.out_station_side_le.setText(data[0])
        self.out_station_name_le.setText(data[1])
        self.out_tunnel_toggle_le.setText("True" if data[2] == "T" else "False")

    
    ##########################################
    #### Train Outputs
    ##########################################
    
    def brake_failure_toggle(self, state) -> None:
        if state:
            self.brake_failure_btn.setStyleSheet("background-color: #FF0000")
        else:
            self.brake_failure_btn.setStyleSheet("")

    def engine_failure_toggle(self, state) -> None:
        if state:
            self.train_engine_fail_btn.setStyleSheet("background-color: #FF0000")
        else:
            self.train_engine_fail_btn.setStyleSheet("")

    def signal_pickup_failure_toggle(self, state) -> None:
        if state:
            self.signal_pickup_failure_btn.setStyleSheet("background-color: #FF0000")
        else:
            self.signal_pickup_failure_btn.setStyleSheet("")

    def pass_ebrake_toggle(self, state) -> None:
        if state:
            self.pass_ebrake_btn.setStyleSheet("background-color: #FF0000")
        else:
            self.pass_ebrake_btn.setStyleSheet("")

    def set_text_out_actual_speed(self, val : float) -> None:
        self.out_actual_speed_le.setText(str(round(val,5)))

    # def set_out_position(self, val : float) -> None:
    #     self.out_position_le.setText(str(round(val,5)))


    ##############################################
    #### Train Controller / Driver & Interfaces
    ##############################################

    def commanded_speed_valueChange(self) -> float:
        return Conv_Globals.MPH_TO_MPS(self.commanded_speed_dsb.value())
    
    def driver_ebrake_btn_clicked(self, state):
        if state:
            self.driver_ebrake_btn.setStyleSheet("background-color: red")
        else:
            self.driver_ebrake_btn.setStyleSheet("background-color: #AA3333")

    def set_temp_changed(self) -> float:
        new_temp = 0.0
        try:
            new_temp = float(self.set_temp_le.text())
        except ValueError:
            new_temp = None

        return new_temp
    
    def set_controller_output_power(self, val : float) -> None:
        self.input_power_command_le.setText(str(round(val,3)))

    ##########################################
    #### Announcements and Ads 
    ##########################################

    def send_announcements_btn_clicked(self) -> str:
        return self.announcements_te.toPlainText()
    
    def send_advertisements_btn_clicked(self) -> str:
        return self.advertisements_te.toPlainText()


    ##########################################
    #### Train Model Settings
    ##########################################

    def model_speedup_value_change(self) -> float:
        new_val = 0

        try:
            new_val = float(self.speed_up_le.text())
        except ValueError:
            new_val = None

        return new_val
    
    def __del__(self):
        print(f"[TRAIN]: Train Model Test Bench Window deleted.")

        


    

    










    
