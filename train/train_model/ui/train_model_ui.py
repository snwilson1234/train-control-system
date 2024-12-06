
from train.train_model.ui.testbench_ui import *
from train.train_model.inc.train_model_enum import Unit, Lights, Door
from train.core.train import Train
from train.train_model.ui.graph_window import Train_Control_Graph, Temp_Control_Graph
from train.train_model.ui.train_specs_popup import Train_Specs_Window

class Train_Model_Signals(QObject):
    temp_changed = Signal(float)

class Train_Model_Main_Window(QMainWindow):
    def __init__(self, identifier):
        super().__init__()
        self.identifier = identifier

        # Main window
        self.setWindowTitle("Train Model Home")
        # self.setFixedSize(QSize(1500,1000))

        # Test Bench
        self.tb = TestBench()

        # Signals
        self.sig = Train_Model_Signals()

        # Graphing Windows
        self.control_graph = None
        self.temp_graph = None        

        # Train Specs Window
        self.train_specs = Train_Specs_Window()

        ##########################################
        #### Top Panel Data and Buttons
        ##########################################
        
        self.air_conditioning_on_disp = UI_Help.create_label("ON", Fonts.top_panel_font)
        self.actual_temp_disp = UI_Help.create_label("70.4 F", Fonts.top_panel_font)
        self.set_temp_disp = UI_Help.create_label("68.7 F", Fonts.top_panel_font)

        self.crew_count_disp = UI_Help.create_label("23", Fonts.top_panel_font)
        self.passenger_count_disp = UI_Help.create_label("123", Fonts.top_panel_font)

        self.right_door_disp = UI_Help.create_label("CLOSED", Fonts.top_panel_font)
        self.left_door_disp = UI_Help.create_label("CLOSED", Fonts.top_panel_font)

        self.exterior_lights_disp = UI_Help.create_label("OFF",Fonts.top_panel_font)
        self.interior_lights_disp = UI_Help.create_label("OFF",Fonts.top_panel_font)

        self.view_train_specs_btn = QPushButton(text="View Train Specs")
        self.view_train_specs_btn.setFont(Fonts.subsection_font)
        self.view_train_specs_btn.setFixedWidth(self.view_train_specs_btn.sizeHint().width() + 20)
        self.view_train_specs_btn.setCheckable(True)

        self.view_temp_graph_btn = QPushButton(text="View Temp Control Graph")
        self.view_temp_graph_btn.setFont(Fonts.subsection_font)
        self.view_temp_graph_btn.setFixedWidth(self.view_temp_graph_btn.sizeHint().width() +10)

        self.view_control_graph_btn = QPushButton(text="View Control Graph")
        self.view_control_graph_btn.setFont(Fonts.subsection_font)
        self.view_control_graph_btn.setFixedWidth(self.view_control_graph_btn.sizeHint().width() + 20)
        


        ##########################################
        #### Interaction Buttons
        ##########################################

        # TODO: make function for button creation
        self.train_engine_fail_btn = QPushButton(text="Train Engine Failure")
        self.brake_fail_btn = QPushButton(text="Brake Failure")
        self.signal_pickup_fail_btn = QPushButton(text = "Signal Pickup Failure")
        self.ebrake_btn = QPushButton(text= "EMERGENCY BRAKE")

        # Customize Interaction Buttons
        self.train_engine_fail_btn.setFont(Fonts.subsection_font)
        # self.train_engine_fail_btn.setStyleSheet("background-color:#5555FF")
        self.brake_fail_btn.setFont(Fonts.subsection_font)
        # self.brake_fail_btn.setStyleSheet("background-color:#5555FF")
        self.signal_pickup_fail_btn.setFont(Fonts.subsection_font)
        # self.signal_pickup_fail_btn.setStyleSheet("background-color:#5555FF")
        self.ebrake_btn.setStyleSheet("background-color:#AA3333")
        self.ebrake_btn.setFont(Fonts.subsection_font)

        ##########################################
        #### Train Status Data
        ##########################################
        self.brake_applied_label = UI_Help.create_label("NO", Fonts.large_bold_font, "green")
        self.brake_status_label = UI_Help.create_label("NOMINAL", Fonts.large_bold_font, "green")
        self.engine_running_label = UI_Help.create_label("RUNNING", Fonts.large_bold_font, "green")
        self.power_disp = UI_Help.create_QLCDNumber(90.543, 7)
        self.power_unit = UI_Help.create_label("kW", Fonts.unit_font)
        self.antenna_running_label = UI_Help.create_label("NOMINAL", Fonts.large_bold_font, "green")

        ##########################################
        #### Trip Info Data
        ##########################################

        self.next_station_label = UI_Help.create_label("NONE", Fonts.station_font, 'blue')
        self.announcements_str = "the next station is STATION DORMONT"
        self.announcements_label = UI_Help.create_label(self.announcements_str, Fonts.normal_font)
        self.announcements_label.setWordWrap(True)
        self.advertisements_str = "this is words - OH MY GOD BUY A COKE FOR 1 DOLLAR"
        self.advertisements_label = UI_Help.create_label(self.advertisements_str, Fonts.normal_font)
        self.advertisements_label.setWordWrap(True)

        ##########################################
        #### Train Telemetry Data
        ##########################################
        
        self.telemetry_data_unit = Unit.IMPERIAL
        self.current_mass_disp = UI_Help.create_QLCDNumber(40.874, 6)
        self.current_mass_unit = UI_Help.create_label("lbs", Fonts.unit_font)
        self.grade_disp = UI_Help.create_QLCDNumber(-0.06025, 8) # needs to store this number -0.06025
        self.grade_unit = UI_Help.create_label("%", Fonts.unit_font)
        #actual speed, commanded speed, acceleration, authority
        self.actual_speed_disp = UI_Help.create_QLCDNumber(122.79, 6) 
        self.actual_speed_unit = UI_Help.create_label("mph", Fonts.unit_font)
        self.commanded_speed_disp = UI_Help.create_QLCDNumber(150.00, 6) 
        self.command_speed_unit = UI_Help.create_label("mph", Fonts.unit_font)
        self.acceleration_disp = UI_Help.create_QLCDNumber(0.7, 5) 
        self.acceleration_unit = UI_Help.create_label("G's", Fonts.unit_font) 
        self.authority_disp = UI_Help.create_QLCDNumber(5, 4)
        self.authority_unit = UI_Help.create_label("Blocks", Fonts.unit_font) 


        ##########################################
        #### Start of Main Layout
        ##########################################
        layout = QGridLayout()
        # layout.setSpacing(0)
        # layout.addWidget(Train_Model_Main_Window.create_frame(), 0,0,3,4)
        
        ##########################################
        #### Top Panel Layout
        ##########################################
        top_panel_layout = QGridLayout()
        top_panel_layout.addWidget(UI_Help.create_frame(),0,0)
        
        nested_top_panel_layout = QGridLayout()
        nested_top_panel_layout.setContentsMargins(10,10,10,10)

        image = QLabel()
        pixmap = QPixmap('./train/train_model/ui/tram_blueprint.png')
        pixmap = pixmap.scaled(1800, 200, Qt.AspectRatioMode.KeepAspectRatio)
        image.setPixmap(pixmap)
        image.setScaledContents(True)
        nested_top_panel_layout.addWidget(image,0,0,4,11, Qt.AlignmentFlag.AlignCenter)

        nested_top_panel_layout.addWidget( UI_Help.create_label("FLEXITY 2 TRAM",Fonts.section_font, 'black'), 0, 0, 1, 11)
        
        field_set = QVBoxLayout()
        field_set.addLayout(UI_Help.create_field("Air Conditioning: ", Fonts.top_panel_NB_font, self.air_conditioning_on_disp, Qt.AlignmentFlag.AlignLeft))
        field_set.addLayout(UI_Help.create_field("Set Temperature: ", Fonts.top_panel_NB_font, self.set_temp_disp, Qt.AlignmentFlag.AlignLeft))
        field_set.addLayout(UI_Help.create_field("Actual Temperature: ", Fonts.top_panel_NB_font, self.actual_temp_disp, Qt.AlignmentFlag.AlignLeft))
        field_set.addWidget(self.view_temp_graph_btn, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        field_set.addStretch()
        nested_top_panel_layout.addLayout(field_set,0,0,4,11, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        field_set = QVBoxLayout()
        field_set.addLayout(UI_Help.create_field("Crew Count: ", Fonts.top_panel_NB_font, self.crew_count_disp, Qt.AlignmentFlag.AlignLeft))
        field_set.addLayout(UI_Help.create_field("Passenger Count: ", Fonts.top_panel_NB_font, self.passenger_count_disp, Qt.AlignmentFlag.AlignLeft))
        nested_top_panel_layout.addLayout(field_set,0,0,4,11, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        field_set = QVBoxLayout()
        field_set.addLayout(UI_Help.create_field("Right Doors: ", Fonts.top_panel_NB_font, self.right_door_disp, Qt.AlignmentFlag.AlignRight))
        field_set.addLayout(UI_Help.create_field("Left Doors: ", Fonts.top_panel_NB_font, self.left_door_disp, Qt.AlignmentFlag.AlignRight))
        nested_top_panel_layout.addLayout(field_set,0,0,4,11, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        field_set = QVBoxLayout()
        field_set.addLayout(UI_Help.create_field("Exterior Lights: ", Fonts.top_panel_NB_font, self.exterior_lights_disp, Qt.AlignmentFlag.AlignRight))
        field_set.addLayout(UI_Help.create_field("Interior Lights: ", Fonts.top_panel_NB_font, self.interior_lights_disp, Qt.AlignmentFlag.AlignRight))
        nested_top_panel_layout.addLayout(field_set,0,0,4,11, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        nested_top_panel_layout.addWidget(self.view_train_specs_btn, 0,0,4,11, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        nested_top_panel_layout.setRowMinimumHeight(0, 200)

        top_panel_layout.addLayout(nested_top_panel_layout,0,0)
        layout.setRowMinimumHeight(0, 285)
        layout.addLayout(top_panel_layout, 0, 0, 1, 4)
        
        ##########################################
        #### Interactions Layout
        ##########################################

        interactions_layout = QGridLayout()

        interactions_layout.addWidget(UI_Help.create_frame(),0,0,1,1)
        internal_interactions_layout = QVBoxLayout()
        internal_interactions_layout.setContentsMargins(20,10,20,10)
        # interactions_label = QLabel("Interactions")
        # interactions_label.setFont(section_font)
        # interactions_label.setAlignment()
        internal_interactions_layout.addWidget(
            UI_Help.create_label("Interactions", Fonts.section_font)
        )
        internal_interactions_layout.addWidget(self.train_engine_fail_btn)
        internal_interactions_layout.addWidget(self.brake_fail_btn)
        internal_interactions_layout.addWidget(self.signal_pickup_fail_btn)
        internal_interactions_layout.addWidget(self.ebrake_btn)
        
        interactions_layout.addLayout(internal_interactions_layout,0,0,1,1, Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(interactions_layout, 1,0, 1, 1)

        ##########################################
        #### Train Status Layout
        ##########################################
        train_status_layout = QGridLayout()
        train_status_layout.addWidget(UI_Help.create_frame(),0,0)
        
        nested_train_status_layout = QGridLayout()
        nested_train_status_layout.setContentsMargins(10,10,10,10)
        nested_train_status_layout.addWidget(UI_Help.create_label("Train Status", Fonts.section_font), 0,0,1,5)
        
        train_status_brake_layout = QVBoxLayout()
        train_status_brake_layout.addWidget(UI_Help.create_label("Brake Applied", Fonts.subsection_font))
        train_status_brake_layout.addWidget(self.brake_applied_label)
        train_status_brake_layout.addWidget(UI_Help.create_label("Brake Status", Fonts.subsection_font))
        train_status_brake_layout.addWidget(self.brake_status_label)
        nested_train_status_layout.addLayout(train_status_brake_layout, 1,0,3,1, Qt.AlignmentFlag.AlignTop)

        train_status_engine_running_layout = QVBoxLayout()
        train_status_engine_running_layout.addWidget(UI_Help.create_label("Engine Status", Fonts.subsection_font))
        train_status_engine_running_layout.addWidget(self.engine_running_label)
        nested_train_status_layout.addLayout(UI_Help.create_number_disp_layout(self.power_disp, self.power_unit, "Engine Output Power", Fonts.subsection_font), 1,1,2,3, Qt.AlignmentFlag.AlignHCenter)
        nested_train_status_layout.addLayout(train_status_engine_running_layout,3, 1, 1, 3, Qt.AlignmentFlag.AlignTop)

        train_status_antenna_running_layout = QVBoxLayout()
        train_status_antenna_running_layout.addWidget(UI_Help.create_label("Antenna Status", Fonts.subsection_font))
        train_status_antenna_running_layout.addWidget(self.antenna_running_label)
        nested_train_status_layout.addLayout(train_status_antenna_running_layout, 1,4,3,1, Qt.AlignmentFlag.AlignTop)

        train_status_layout.addLayout(nested_train_status_layout, 0,0)
        layout.addLayout(train_status_layout, 1,1,1, 2)



        ##########################################
        #### Trip Info Layout
        ##########################################
        trip_info_layout = QGridLayout()
        trip_info_layout.addWidget(UI_Help.create_frame(),0,0,1,1)
        internal_trip_info_layout = QVBoxLayout()
        internal_trip_info_layout.setContentsMargins(10,20,10,20)
        internal_trip_info_layout.addWidget(
            UI_Help.create_label("Trip Information", Fonts.section_font)
        )
        internal_trip_info_layout.addWidget(
            UI_Help.create_label("Next Stop", Fonts.subsection_font)
        )
        internal_trip_info_layout.addWidget(self.next_station_label)
        internal_trip_info_layout.addWidget(
            UI_Help.create_label("Announcements", Fonts.subsection_font)
        )
        internal_trip_info_layout.addWidget(self.announcements_label)
        internal_trip_info_layout.addWidget(
            UI_Help.create_label("Words from Our Sponsors", Fonts.subsection_font)
        )
        internal_trip_info_layout.addWidget(self.advertisements_label)

        trip_info_layout.addLayout(internal_trip_info_layout, 0,0,1,1, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(trip_info_layout, 1,3,1, 1)
        
        ##########################################
        #### Train Telemetry Layout
        ##########################################
        
        train_telemetry_layout = QGridLayout()
        train_telemetry_layout.addWidget(UI_Help.create_frame(),0,0)
        nested_train_telemetry_layout = QGridLayout()
        nested_train_telemetry_layout.setContentsMargins(20,15,20,10)


        train_telemetry_title_layout = QHBoxLayout()
        train_telemetry_title_layout.addWidget(
            UI_Help.create_label("Train Telemetry", Fonts.section_font)
        )
        nested_train_telemetry_layout.addLayout(train_telemetry_title_layout, 0,0,1,6, Qt.AlignmentFlag.AlignHCenter)

        train_telemetry_data_V_layout = QVBoxLayout()
        train_telemetry_data_V_layout.addSpacerItem(QSpacerItem(1,20))

        train_telemetry_data_layout = QHBoxLayout()
        train_telemetry_data_layout.addLayout(UI_Help.create_number_disp_layout(self.current_mass_disp, self.current_mass_unit, "Current Mass", Fonts.subsection_font))
        train_telemetry_data_layout.addLayout(UI_Help.create_number_disp_layout(self.grade_disp, self.grade_unit, "Grade", Fonts.subsection_font))
        train_telemetry_data_layout.addLayout(UI_Help.create_number_disp_layout(self.actual_speed_disp, self.actual_speed_unit, "Actual Speed", Fonts.subsection_font))
        train_telemetry_data_layout.addLayout(UI_Help.create_number_disp_layout(self.commanded_speed_disp, self.command_speed_unit, "Commanded Speed", Fonts.subsection_font))
        train_telemetry_data_layout.addLayout(UI_Help.create_number_disp_layout(self.acceleration_disp, self.acceleration_unit, "Acceleration", Fonts.subsection_font))
        train_telemetry_data_layout.addLayout(UI_Help.create_number_disp_layout(self.authority_disp, self.authority_unit, "Authority", Fonts.subsection_font))
        
        train_telemetry_data_V_layout.addLayout(train_telemetry_data_layout)
        nested_train_telemetry_layout.addLayout(train_telemetry_data_V_layout, 1,0,1,6)

        self.unit_toggle = AnimatedToggle()
        self.unit_toggle.setFixedWidth(80)
        imperial_label = QLabel("IMPERIAL")
        imperial_label.setFont(Fonts.subsection_font)
        metric_label = QLabel("METRIC")
        metric_label.setFont(Fonts.subsection_font)
        train_telemetry_bottom_bar_layout = QHBoxLayout()
        train_telemetry_bottom_bar_layout.addWidget(imperial_label)
        train_telemetry_bottom_bar_layout.addWidget(self.unit_toggle)
        train_telemetry_bottom_bar_layout.addWidget(metric_label)
        nested_train_telemetry_layout.addLayout(train_telemetry_bottom_bar_layout, 0,0,1,6, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        nested_train_telemetry_layout.addWidget(self.view_control_graph_btn, 0,0,1,6, Qt.AlignmentFlag.AlignLeft)

        train_telemetry_layout.addLayout(nested_train_telemetry_layout,0,0,1,1)
        layout.addLayout(train_telemetry_layout,2,0,1,4)

        ##########################################
        #### End Layouts
        ##########################################

        # Set the background color
        widget = Color('light blue')
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Start up the backend and initialize UIs
        self.init_backend(identifier)
        self.connect_backend()
        self.start_backend()
        self.init_testbench_fields()
        self.init_main_ui_fields()

    ##########################################
    #### CLASS SUPPORT
    ##########################################

    def show_all_windows(self):
        self.show()
        self.tb.show()

    def delete(self):
        if self.control_graph != None:
            self.control_graph.destroy(True, True)
        
        if self.temp_graph != None:
            self.temp_graph.destroy(True, True)

        self.tb.destroy(True, True)
        self.destroy(True, True)
        del(self)



    ##########################################
    #### BACKEND, SLOTS, SIGNALS
    ##########################################

    def init_backend(self, identifier):
        self.train = Train(identifier)

    def init_main_ui_fields(self):
        self.crew_count_disp.setText(str(self.train.train_model.crew_count))
        self.passenger_count_disp.setText(str(self.train.train_model.passenger_count))


    def init_testbench_fields(self): 
        self.tb.out_commanded_speed_le.setText(str(self.train.train_model.get_track_circuit_data()[0]))
        self.tb.out_authority_le.setText(str(self.train.train_model.get_track_circuit_data()[1])) 
        self.tb.kp_le.setText(str(self.train.controller.Kp))
        self.tb.ki_le.setText(str(self.train.controller.Ki))
        self.announcements_label.setText("No announcements at this time.")
        self.advertisements_label.setText("No advertisements at this time.")

    def connect_backend(self) -> None:
        # Signals from the thread
        # self.train.signals.actual_velocity.connect(self.actual_speed_disp.display)
        # self.train.signals.commanded_velocity.connect(self.commanded_speed_disp.display)
        # self.train.signals.acceleration.connect(self.acceleration_disp.display)
        # self.train.signals.grade.connect(self.grade_disp.display)
        # self.train.signals.current_mass.connect(self.current_mass_disp.display)
        self.train.signals.power.connect(self.power_disp.display)
        # self.train.signals.brake_applied.connect(self.brake_applied_label.setText)
        self.train.signals.updated.connect(self.update_control_graph)
        self.train.signals.updated.connect(self.update_telemetry)
        self.train.signals.updated.connect(self.update_temp_control_data)
        self.train.signals.updated.connect(self.update_temp_graph)

        # Signals from the UI
        self.train_engine_fail_btn.clicked.connect(self.train_engine_failure_btn_clicked)
        self.brake_fail_btn.clicked.connect(self.brake_failure_toggle_btn_clicked)
        self.ebrake_btn.clicked.connect(self.passenger_ebrake_btn_clicked)
        self.signal_pickup_fail_btn.clicked.connect(self.signal_pickup_toggle_btn_clicked)
        self.unit_toggle.stateChanged.connect(self.handle_unit_toggle)
        self.view_train_specs_btn.clicked.connect(self.toggle_train_specs_popup)
        self.view_control_graph_btn.clicked.connect(self.handle_control_graphing)
        self.view_temp_graph_btn.clicked.connect(self.handle_temp_graphing)
        

        # Signals from Test UI
        self.tb.send_direct_info.clicked.connect(self.handle_direct_info_send)
        self.tb.send_track_circuit_btn.clicked.connect(self.handle_track_circuit_send)
        self.tb.send_beacon_data_btn.clicked.connect(self.handle_beacon_data_send)
        self.tb.send_advertisement_btn.clicked.connect(self.handle_advertisements_send)
        self.tb.send_announcement_btn.clicked.connect(self.handle_announcements_send)
        self.tb.send_gains_btn.clicked.connect(self.handle_PID_send)
        self.tb.send_all_inputs_btn.clicked.connect(self.handle_send_all)

        self.tb.commanded_speed_dsb.valueChanged.connect(self.set_commanded_speed)
        self.tb.driver_ebrake_btn.clicked.connect(self.driver_ebrake_clicked)
        self.tb.exterior_lights_btn.stateChanged.connect(self.exterior_lights_clicked)
        self.tb.interior_lights_btn.stateChanged.connect(self.interior_lights_clicked)
        self.tb.right_doors_btn.stateChanged.connect(self.right_door_clicked)
        self.tb.left_doors_btn.stateChanged.connect(self.left_door_clicked)
        self.tb.set_temp_le.textChanged.connect(self.update_set_temp)
        self.tb.speed_up_le.textChanged.connect(self.update_model_speed)

        # Signals to the Test UI
        self.train.signals.actual_velocity.connect(self.tb.set_text_out_actual_speed)
        # self.train.signals.position.connect(self.tb.set_out_position)
        self.train.signals.controller_power_command.connect(self.tb.set_controller_output_power)

        # Signals from the Train Model
        self.train.train_model.sig.air_conditioning_status.connect(self.update_air_cond_state)
        self.train.train_model.sig.passengers_changed.connect(self.update_passenger_displays)
        self.train.train_model.sig.grade_updated.connect(self.grade_disp.display)
        # Signals from the Train Controller
        self.train.controller.signals.open_left_doors.connect(self.update_left_door_state)
        self.train.controller.signals.open_right_doors.connect(self.update_right_door_state)
        self.train.controller.signals.open_all_doors.connect(self.update_left_door_state)
        self.train.controller.signals.open_all_doors.connect(self.update_right_door_state)
        self.train.controller.signals.close_left_doors.connect(self.update_left_door_state)
        self.train.controller.signals.close_right_doors.connect(self.update_right_door_state)
        self.train.controller.signals.close_all_doors.connect(self.update_left_door_state)
        self.train.controller.signals.close_all_doors.connect(self.update_right_door_state)

        self.train.controller.signals.toggle_exterior_lights.connect(self.update_exterior_light)
        self.train.controller.signals.toggle_interior_lights.connect(self.update_interior_lights)

        self.train.controller.signals.broadcast_advertisements.connect(self.update_advertisements)
        self.train.controller.signals.broadcast_announcements.connect(self.update_announcements)
        self.train.controller.signals.broadcast_station_name.connect(self.update_station_name)

        self.train.controller.signals.new_commanded_speed.connect(self.update_telemetry)
        self.train.controller.signals.new_CTC_speed.connect(self.update_telemetry)


        



    def start_backend(self) -> None:
        pass

    ##########################################
    #### Handling Send Buttons
    ##########################################

    def handle_send_all(self) -> None:
        self.handle_beacon_data_send()
        self.handle_direct_info_send()
        self.handle_announcements_send()
        self.handle_advertisements_send()
        self.handle_track_circuit_send()


    def handle_direct_info_send(self) -> None:
        info = self.tb.send_direct_info_btn_clicked()
        self.train.train_model.set_grade(info.grade_data)
        self.train.train_model.set_block_length(info.block_length_data)
        self.train.train_model.onboard_passengers(info.passengers_boarding_data)
        self.train.train_model.handle_track_power_failure(info.track_power_fail_data)
        if info.entered_new_block: self.train.train_model.entered_new_block()
        self.update_engine_fail_status()
        self.update_passenger_displays()


    def handle_track_circuit_send(self) -> None:
        new_data = self.tb.send_track_circuit_btn_clicked()
        self.train.train_model.set_track_circuit_data(*new_data)
        self.tb.set_out_track_circuit_data(self.train.train_model.get_track_circuit_data())
        self.train.controller.set_commanded_speed_CTC_m_s(self.train.train_model.get_track_circuit_data()[0])

    def handle_beacon_data_send(self) -> None:
        beacon = self.tb.send_beacon_data_btn_clicked()
        self.train.train_model.set_beacon_data(beacon.get_data_string())
        self.tb.update_beacon_out_data(self.train.train_model.get_beacon_data())
        self.next_station_label.setText(self.train.train_model.get_station_name().upper())

    def handle_announcements_send(self) -> None:
        self.train.train_model.set_announcements(self.tb.send_announcements_btn_clicked())
        self.announcements_label.setText(self.train.train_model.get_announcements())

    def handle_advertisements_send(self) -> None:
        self.train.train_model.set_advertisement(self.tb.send_advertisements_btn_clicked())
        self.advertisements_label.setText(self.train.train_model.get_advertisement())

    def update_announcements(self) -> None:
        self.announcements_label.setText(self.train.train_model.get_announcements())

    def update_advertisements(self) -> None:
        self.advertisements_label.setText(self.train.train_model.get_advertisement())

    def update_station_name(self) -> None:
        self.next_station_label.setText(self.train.train_model.get_station_name())

    def handle_PID_send(self) -> None:
        gains = self.tb.send_PID_gains_btn_clicked()
        self.train.controller.set_PID_gains(gains.kp, gains.ki)



    ##########################################
    #### Failures and Ebrake
    ##########################################
    
    def update_engine_fail_status(self) -> None:
        new_state = self.train.train_model.get_engine_failure()

        if(new_state):
            self.train_engine_fail_btn.setStyleSheet("background:#FF0000")
            self.engine_running_label.setText("NOT RUNNING")
            self.engine_running_label.setStyleSheet("color: red")
        else:
            self.train_engine_fail_btn.setStyleSheet("")
            self.engine_running_label.setText("RUNNING")
            self.engine_running_label.setStyleSheet("color: green")

        self.tb.engine_failure_toggle(new_state)

    
    def train_engine_failure_btn_clicked(self) -> None:
        self.train.train_model.toggle_engine_failure()
        self.update_engine_fail_status()
        

    def brake_failure_toggle_btn_clicked(self) -> None:
        self.train.train_model.toggle_brake_failure()
        new_state = self.train.train_model.get_brake_failure()

        if(new_state):
            self.brake_fail_btn.setStyleSheet("background:#FF0000")
            self.brake_status_label.setText("FAILED")
            self.brake_status_label.setStyleSheet("color: red")
        else:
            self.brake_fail_btn.setStyleSheet("")
            self.brake_status_label.setText("NOMINAL")
            self.brake_status_label.setStyleSheet("color: green")

        self.tb.brake_failure_toggle(new_state)

    def signal_pickup_toggle_btn_clicked(self) -> None:
        self.train.train_model.toggle_signal_pickup_failure()
        new_state = self.train.train_model.get_signal_pickup_failure()

        if(new_state):
            self.signal_pickup_fail_btn.setStyleSheet("background:#FF0000")
            self.antenna_running_label.setText("OFFLINE")
            self.antenna_running_label.setStyleSheet("color: red")
        else:
            self.signal_pickup_fail_btn.setStyleSheet("")
            self.antenna_running_label.setText("NOMINAL")
            self.antenna_running_label.setStyleSheet("color: green")

        self.tb.signal_pickup_failure_toggle(new_state)

    def passenger_ebrake_btn_clicked(self) -> None:
        self.train.train_model.toggle_pass_ebrake()
        new_state = self.train.train_model.get_pass_ebrake()

        if(new_state):
            self.ebrake_btn.setStyleSheet("background:#FF0000")
        else:
            self.ebrake_btn.setStyleSheet("background:#AA3333")

        self.tb.pass_ebrake_toggle(new_state)

    ##############################################
    #### Train Controller / Driver & Interfaces
    ##############################################

    def set_commanded_speed(self) -> None:
        self.train.controller.set_commanded_speed_m_s(self.tb.commanded_speed_valueChange())

    def driver_ebrake_clicked(self) -> None:
        self.train.train_model.toggle_driver_ebrake()
        self.tb.driver_ebrake_btn_clicked(self.train.train_model.get_driver_ebrake())

    def exterior_lights_clicked(self, state : Qt.CheckState) -> None:
        if state == Qt.CheckState.Checked.value:
            self.train.train_model.set_ext_lights(Lights.ON)
            self.exterior_lights_disp.setText("ON")
        else:
            self.train.train_model.set_ext_lights(Lights.OFF)
            self.exterior_lights_disp.setText("OFF")

    def interior_lights_clicked(self, state : Qt.CheckState) -> None:
        if state == Qt.CheckState.Checked.value:
            self.train.train_model.set_int_lights(Lights.ON)
            self.interior_lights_disp.setText("ON")
        else:
            self.train.train_model.set_int_lights(Lights.OFF)
            self.interior_lights_disp.setText("OFF")

    def update_exterior_light(self) -> None:
        if self.train.train_model.get_ext_lights():
            self.exterior_lights_disp.setText("ON")
        else:
            self.exterior_lights_disp.setText("OFF")


    def update_interior_lights(self) -> None:
        if self.train.train_model.get_int_lights():
            self.interior_lights_disp.setText("ON")
        else:
            self.interior_lights_disp.setText("OFF")


    def right_door_clicked(self, state : Qt.CheckState) -> None:
        if state == Qt.CheckState.Checked.value:
            self.train.train_model.set_right_door(Door.OPEN)
            self.right_door_disp.setText("OPEN")
            self.update_passenger_displays()
        else:
            self.train.train_model.set_right_door(Door.CLOSE)
            self.right_door_disp.setText("CLOSED")

    def update_right_door_state(self) -> None:
        if self.train.train_model.get_right_door():
            self.right_door_disp.setText("OPEN")
        else:
            self.right_door_disp.setText("CLOSED")
        self.update_passenger_displays()

    def left_door_clicked(self, state : Qt.CheckState) -> None:
        if state == Qt.CheckState.Checked.value:
            self.train.train_model.set_left_door(Door.OPEN)
            self.left_door_disp.setText("OPEN")
            self.update_passenger_displays()
        else:
            self.train.train_model.set_left_door(Door.CLOSE)
            self.left_door_disp.setText("CLOSED")
    
    def update_left_door_state(self) -> None:
        if self.train.train_model.get_left_door():
            self.left_door_disp.setText("OPEN")
        else:
            self.left_door_disp.setText("CLOSED")
        self.update_passenger_displays()

    def update_passenger_displays(self) -> None:
        self.passenger_count_disp.setText(str(self.train.train_model.get_passenger_count()))
        self.crew_count_disp.setText(str(self.train.train_model.get_crew_count()))

    def update_temp_control_data(self) -> None:
        self.set_temp_disp.setText(str(self.train.train_model.set_temp_F))
        self.actual_temp_disp.setText(str(round(self.train.train_model.actual_temp_F,3)))

    def update_set_temp(self) -> None:
        new_val = self.tb.set_temp_changed()
        if(new_val is None): return
        if len(str(new_val)) < 4: return
        self.train.train_model.set_temp(new_val)

    def update_air_cond_state(self, state : bool) -> None:
        if state: self.air_conditioning_on_disp.setText("ON")
        else: self.air_conditioning_on_disp.setText("OFF")

    ##########################################
    #### Graphing
    ##########################################

    def update_temp_graph(self):
        if self.temp_graph != None:
            self.temp_graph.update(self.train.time_sec, self.train.train_model.set_temp_F, self.train.train_model.actual_temp_F)
            if self.temp_graph.pending_delete: self.handle_temp_graphing()

    def update_control_graph(self) -> None:
        if self.control_graph != None:
            self.control_graph.update(self.train.time_sec, self.train.train_model.velocity_mps, self.train.power_command, self.train.controller.commanded_speed_m_s)
            if self.control_graph.pending_delete: self.handle_control_graphing()

    def handle_temp_graphing(self) -> None:
        if self.temp_graph is None:
            self.temp_graph = Temp_Control_Graph()
            self.temp_graph.show()
            self.temp_graph.setGeometry(300,300,1000,500)
            self.view_temp_graph_btn.setText("Hide Temp Control Graph")
        else:
            self.temp_graph.destroy()
            self.temp_graph = None
            self.view_temp_graph_btn.setText("View Temp Control Graph")

    def handle_control_graphing(self) -> None:
        if self.control_graph is None:
            self.control_graph = Train_Control_Graph()
            self.control_graph.show()
            self.control_graph.setGeometry(300,300,1000,500)
            self.view_control_graph_btn.setText("Hide Control Graph")
        else:
            self.control_graph.destroy()
            self.control_graph = None
            self.view_control_graph_btn.setText("View Control Graph")


    ##########################################
    #### Telemetry
    ##########################################

    def handle_unit_toggle(self) -> None:
        if self.telemetry_data_unit is Unit.IMPERIAL:
            self.telemetry_data_unit = Unit.METRIC
            self.actual_speed_unit.setText("m/s")
            self.command_speed_unit.setText("m/s")
            self.current_mass_unit.setText("kg")
        else:
            self.telemetry_data_unit = Unit.IMPERIAL
            self.actual_speed_unit.setText("mph")
            self.command_speed_unit.setText("mph")
            self.current_mass_unit.setText("lbs")

    def update_telemetry(self) -> None:
        if self.telemetry_data_unit is Unit.IMPERIAL:
            self.actual_speed_disp.display(Conv_Globals.MPS_TO_MPH(self.train.train_model.velocity_mps))
            self.commanded_speed_disp.display(Conv_Globals.MPS_TO_MPH(self.train.controller.get_overall_speed_m_s()))
            self.current_mass_disp.display(Conv_Globals.KG_TO_LBS(self.train.train_model.mass_kg))
        else:
            self.actual_speed_disp.display(self.train.train_model.velocity_mps)
            self.commanded_speed_disp.display(self.train.controller.get_overall_speed_m_s())
            self.current_mass_disp.display(self.train.train_model.mass_kg)

        # no units
        self.acceleration_disp.display(self.train.train_model.accel_no_grade_mps2/9.8)
        self.grade_disp.display(self.train.train_model.grade)
        self.authority_disp.display(self.train.train_model.authority_blocks)
        self.brake_applied_label.setText(self.train.train_model.brake_applied)


    ##########################################
    #### Train Model Settings
    ##########################################

    def update_model_speed(self) -> None:
        val = self.tb.model_speedup_value_change()
        if val == None or val <= 0:
            return
        
        self.train.speed_up = val


    ##########################################
    #### Train Specs
    ##########################################

    def toggle_train_specs_popup(self, state) -> None:
        if state:
            self.train_specs.show()
            self.view_train_specs_btn.setChecked(False)
        else:
            self.train_specs.hide()

    
    def __del__(self):
        print(f"[TRAIN]: Train model UI with identifier {self.identifier} has been deleted.")
