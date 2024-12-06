import sys

from PySide6.QtCore import QThread, QObject, Signal

from train.train_controller.train_controller_class import *
from train.train_controller.train_controller_class import DEFAULT_KP
from train.train_controller.train_controller_class import DEFAULT_KI
from train.train_model.ui.custom_widgets import AnimatedToggle, Color

sys.path.append('.')
from utils.UI import *
from common.beacon_info_enums import *

LOCK_PID = False


class RunTrainThread(QThread):
    train = None
    time = 1

    def __init__(self, train, time):
        super().__init__()
        self.train = train
        self.time = int(time)

    def run(self):
        self.train.run(self.time)



class TestBenchWindow(QMainWindow):

    def __init__(self, train):
        super().__init__()
        self.create_testbench_window(train)


    def create_testbench_window(self, train):


        self.setWindowTitle("Train Controller - Testbench")

        # Status Box
        train_status_no_edit = QTextEdit()
        train_status_no_edit.setReadOnly(True)

        # Inputs Layout
        inputs_left = QVBoxLayout()
        inputs_right = QVBoxLayout()

        # Driver Inputs - Auto/Manual, Buttons, Set speed
        driver_items = [str(Modes.AUTO), str(Modes.MANUAL)]
        driver_mode = create_combo_box("Driver Inputs", driver_items, train.set_mode)
        inputs_left.addLayout(driver_mode)

        # Driver Inputs
        driver_speed = QVBoxLayout()
        driver_speed_label = QLabel("Driver Set Speed (m/s)")
        driver_speed_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        driver_speed_input = QLineEdit()
        driver_speed_input.textEdited.connect(lambda: train.set_commanded_speed_m_s(float(driver_speed_input.text())))
        driver_speed_input.setText(str(train.get_commanded_speed_m_s()))
        train.signals.new_commanded_speed.connect(lambda: driver_speed_input.setText(str(train.get_commanded_speed_m_s())))
        driver_speed.addWidget(driver_speed_input)
        driver_speed.addWidget(driver_speed_label)
        inputs_left.addLayout(driver_speed)

        driver_ebrake_button = QPushButton("EBRAKE")
        def apply_driver_ebrake():
            driver_ebrake_button.clicked.connect(train.driver_ebrake_applied)
            train.signals.UI_ebrake_applied.emit()
        driver_ebrake_button.clicked.connect(apply_driver_ebrake())



        remove_ebrake_button = create_button("Remove Ebrake")

        driver_ebrake_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        driver_ebrake_button.clicked.connect(lambda: driver_ebrake_button.setDisabled(True))
        driver_ebrake_button.clicked.connect(lambda: remove_ebrake_button.setEnabled(True))
        inputs_left.addWidget(driver_ebrake_button)
        train.signals.new_status.connect(lambda: train_status_no_edit.setText(train.get_current_status()))

        remove_ebrake_button.setDisabled(True)
        remove_ebrake_button.clicked.connect(lambda: train.clear_driver_ebrake)
        remove_ebrake_button.clicked.connect(lambda: driver_ebrake_button.setEnabled(True))
        remove_ebrake_button.clicked.connect(lambda: remove_ebrake_button.setDisabled(True))
        remove_ebrake_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        inputs_left.addWidget(remove_ebrake_button)

        # CTC Inputs
        inputs_left.addWidget(QLabel("CTC Office Inputs"))
        commanded_speed_input = QLineEdit()
        commanded_speed_input.setText(str(train.get_commanded_speed_m_s()))
        commanded_speed_label = QLabel("Commanded Speed (m/s)")
        commanded_speed_layout = QVBoxLayout()
        commanded_speed_layout.addWidget(commanded_speed_input)
        commanded_speed_layout.addWidget(commanded_speed_label)
        commanded_speed_input.textChanged.connect(lambda: train.set_commanded_speed_CTC_m_s(float(commanded_speed_input.text())))

        inputs_left.addLayout(commanded_speed_layout)
        authority_label = QLabel("Authority")
        authority_input = QLineEdit()
        authority_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        authority_input.textChanged.connect(lambda: train.set_authority_blocks(int(authority_input.text())))
        authority_layout = QVBoxLayout()
        authority_layout.addWidget(authority_input)
        authority_layout.addWidget(authority_label)
        inputs_left.addLayout(authority_layout)

        # Train Model Inputs
        inputs_right.addWidget(QLabel("Train Model Inputs"))
        actual_vel_label = QLabel("Actual Velocity (m/s)")
        actual_vel_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        actual_vel_input = QLineEdit()
        actual_vel_input.setText(str(train.get_current_speed_m_s()))
        actual_vel_input.textChanged.connect(lambda: train.set_current_speed_m_s(float(actual_vel_input.text())) )
        inputs_right.addWidget(actual_vel_input)
        inputs_right.addWidget(actual_vel_label)

        # Failure Inputs
        inputs_right.addWidget(QLabel("Failures"))
        engine_failure_button = create_button("Engine Failure", train.receive_engine_failure)
        engine_failure_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        signal_pickup_failure_button = create_button("Signal Pickup Failure", train.receive_signal_pickup_failure)
        signal_pickup_failure_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        brake_failure_button = create_button("Brake Failure")
        brake_failure_button.clicked.connect(train.receive_brake_failure)
        brake_failure_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))

        clear_engine_button = create_button("Clear Engine Failure", train.clear_engine_failure)
        # clear_engine_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        clear_brake_button = create_button("Clear Brake Failure", train.clear_brake_failure)
        # clear_brake_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        clear_signal_button = create_button("Clear Engine Failure", train.clear_signal_pickup_failure)
        # clear_signal_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))
        train.signals.new_status.connect(train_status_no_edit.setText)


        inputs_right.addWidget(brake_failure_button)
        inputs_right.addWidget(engine_failure_button)
        inputs_right.addWidget(signal_pickup_failure_button)
        inputs_right.addWidget(clear_engine_button)
        inputs_right.addWidget(clear_brake_button)
        inputs_right.addWidget(clear_signal_button)


        # PID Gains
        PID_Kp = QLineEdit()
        PID_Kp.setText(str(train.Kp))
        PID_Kp_label = QLabel("Kp")
        PID_Kp_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        Kp_layout = QVBoxLayout()
        Kp_layout.addWidget(PID_Kp)
        Kp_layout.addWidget(PID_Kp_label)


        PID_Ki = QLineEdit()
        PID_Ki.setText(str(train.Ki))
        PID_Ki_label = QLabel("Ki")
        PID_Ki_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        Ki_layout = QVBoxLayout()
        Ki_layout.addWidget(PID_Ki)
        Ki_layout.addWidget(PID_Ki_label)
        PID_Gain_lock_button = QPushButton("Set")

        PID_Gain_reset_button = QPushButton("Reset")
        PID_Gain_reset_button.setDisabled(True)
        PID_Gain_lock_button.clicked.connect(
            lambda: self.set_PID_Gains(train=train, Kp=float(PID_Kp.text()), Ki=float(PID_Ki.text())))
        PID_Gain_lock_button.clicked.connect(lambda: PID_Ki.setReadOnly(True))
        PID_Gain_lock_button.clicked.connect(lambda: PID_Kp.setReadOnly(True))
        PID_Gain_lock_button.clicked.connect(lambda: PID_Gain_lock_button.setDisabled(True))
        PID_Gain_lock_button.clicked.connect(lambda: PID_Gain_reset_button.setEnabled(True))
        # PID_Gain_lock_button.clicked.connect(lambda: self.train_controller)
        PID_Gain_reset_button.clicked.connect(lambda: train.reset_PID_gains())
        PID_Gain_reset_button.clicked.connect(lambda: PID_Ki.setReadOnly(False))
        PID_Gain_reset_button.clicked.connect(lambda: PID_Kp.setReadOnly(False))
        PID_Gain_reset_button.clicked.connect(lambda: PID_Gain_lock_button.setEnabled(True))
        PID_Gain_reset_button.clicked.connect(lambda: PID_Gain_reset_button.setDisabled(True))
        PID_Gain_reset_button.clicked.connect(lambda: train.signals.reset_gains.emit())
        PID_Gain_lock_button.toggled.connect(PID_Ki.setDisabled)
        train.signals.set_gains.connect(lambda: PID_Ki.setReadOnly(True))
        train.signals.set_gains.connect(lambda: PID_Kp.setReadOnly(True))
        train.signals.set_gains.connect(lambda: PID_Ki.setText(str(train.Ki)))
        train.signals.set_gains.connect(lambda: PID_Kp.setText(str(train.Kp)))
        train.signals.set_gains.connect(lambda: PID_Gain_lock_button.setDisabled(True))
        train.signals.set_gains.connect(lambda: PID_Gain_reset_button.setEnabled(True))

        PID_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        gain_layout = QVBoxLayout()

        gain_layout.addLayout(Kp_layout)
        gain_layout.addLayout(Ki_layout)
        PID_layout.addLayout(gain_layout)
        button_layout.addWidget(PID_Gain_lock_button)
        button_layout.addWidget(PID_Gain_reset_button)
        PID_layout.addLayout(button_layout)
        inputs_left.addWidget(QLabel("PID Gains"))
        inputs_left.addLayout(PID_layout)

        # Beacon Inputs
        beacon_layout = QVBoxLayout()
        beacon_layout.addWidget(QLabel("Beacon Inputs"))
        beacon_layout.addLayout(create_combo_box(label="Next Station", on_click=train.set_next_station,
                                                 items=StationList.asValues()))
        beacon_layout.addLayout(create_combo_box(label="Station Side", on_click=train.set_door_side,
                                                 items=StationSide.asValues()))
        inputs_right.addLayout(beacon_layout)

        beacon_input_text = QLineEdit()
        beacon_input_button = QPushButton("Set")
        beacon_label = QLabel("Text Beacon Info")
        beacon_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        beacon_input_button.clicked.connect(lambda: train.receive_beacon_info( list(beacon_input_text.text().split(", "))))
        beacon_layout.addWidget(beacon_input_text)
        beacon_layout.addWidget(beacon_input_button)

        # Passenger Inputs
        inputs_left.addWidget(QLabel("Passenger Inputs"))
        passenger_ebrake_button = create_button("PASSENGER EBRAKE", train.passenger_ebrake_applied)
        remove_ebrake_passenger = create_button("Remove Ebrake")
        remove_ebrake_passenger.setDisabled(True)
        passenger_ebrake_button.clicked.connect(lambda: passenger_ebrake_button.setDisabled(True))
        passenger_ebrake_button.clicked.connect(lambda: remove_ebrake_passenger.setEnabled(True))
        passenger_ebrake_button.clicked.connect(lambda: train_status_no_edit.setText(train.get_current_status()))

        remove_ebrake_passenger.clicked.connect(lambda: remove_ebrake_passenger.setDisabled(True))
        remove_ebrake_passenger.clicked.connect(lambda: passenger_ebrake_button.setEnabled(True))
        remove_ebrake_passenger.clicked.connect(lambda: train_status_no_edit.setText(train.clear_passenger_ebrake().value))

        inputs_left.addWidget(passenger_ebrake_button)
        inputs_left.addWidget(remove_ebrake_passenger)

        # Add outputs
        outputs = QVBoxLayout()
        outputs.addWidget(QLabel("Outputs"))

        # Run simulation
        run_button = QPushButton("Get Power")

        outputs.addWidget(run_button)

        # Power Output
        power_output = QLineEdit()
        power_output.setReadOnly(True)
        power_output_label = QLabel("Power Output (W)")
        power_output_label.setAlignment(Qt.AlignRight)
        power_output.setText(str(train.power_command_w))

        run_button.clicked.connect(lambda: power_output.setText(str(get_power_cmd())))

        def get_power_cmd():
            actual_vel = float(actual_vel_input.text())
            power_cmd = train.output_power(actual_vel)
            return power_cmd

        outputs.addWidget(power_output)
        outputs.addWidget(power_output_label)
        train.signals.new_power.connect(power_output.setText)
        # outputs.addLayout(create_line_no_edit("Power Output"))

        # Velocity Output
        current_velocity = QLineEdit()
        current_velocity.setReadOnly(True)
        current_velocity_label = QLabel("Current Velocity (m/s)")
        current_velocity_label.setAlignment(Qt.AlignRight)
        current_velocity.setText(str(train.get_current_speed_m_s()))
        train.signals.current_speed_set.connect(current_velocity.setText)

        outputs.addWidget(current_velocity)
        outputs.addWidget(current_velocity_label)

        # Train Status Output
        # Status Layout
        train_status = QVBoxLayout()
        train_status_label = QLabel("Train Status")
        train_status_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        # train_status_no_edit = QTextEdit()
        train_status_no_edit.setText(str(train.get_current_status()))
        # train_status_no_edit.setReadOnly(True)
        train_status.addWidget(train_status_no_edit)
        train_status.addWidget(train_status_label)
        outputs.addLayout(train_status)

        # Non-Vital Operations
        outputs.addWidget(QLabel("Non-Vital Operations"))

        # Doors
        doors_layout = QHBoxLayout()
        # doors_layout.addWidget(QPushButton("Doors"))
        doors_output = QLineEdit("Door Status")
        doors_output.setReadOnly(True)
        doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status)
        doors_output.setAlignment(Qt.AlignRight)
        doors_layout.addWidget(doors_output)
        outputs.addLayout(doors_layout)
        door_label = QLabel("Doors")
        door_label.setAlignment(Qt.AlignRight)
        outputs.addWidget(door_label)
        train.signals.close_left_doors.connect(lambda: doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status))
        train.signals.close_right_doors.connect(lambda: doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status))
        train.signals.close_all_doors.connect(lambda: doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status))
        train.signals.open_left_doors.connect(lambda: doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status))
        train.signals.open_right_doors.connect(lambda: doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status))
        train.signals.open_all_doors.connect(lambda: doors_output.setText("Left door " + train.left_door_status + ". Right door " + train.right_door_status))



        # Lights
        lights_layout = QHBoxLayout()
        interior_lights_status = QLineEdit()
        interior_lights_status.setReadOnly(True)
        interior_lights_status.setText(train.get_interior_light_status())
        train.signals.toggle_interior_lights.connect(lambda: interior_lights_status.setText(train.get_interior_light_status()))

        interior_lights_label = QLabel("Interior Lights")
        interior_lights_label.setAlignment(Qt.AlignRight)
        lights_layout.addWidget(interior_lights_status)
        outputs.addLayout(lights_layout)
        outputs.addWidget(interior_lights_label)

        lights_exterior_layout = QHBoxLayout()
        exterior_lights_status = QLineEdit()
        exterior_lights_status.setReadOnly(True)
        exterior_lights_status.setText(train.get_exterior_light_status())
        train.signals.toggle_exterior_lights.connect(lambda: exterior_lights_status.setText(train.get_exterior_light_status()))

        exterior_lights_label = QLabel("Exterior Lights")
        exterior_lights_label.setAlignment(Qt.AlignRight)
        lights_exterior_layout.addWidget(exterior_lights_status)
        outputs.addLayout(lights_exterior_layout)
        outputs.addWidget(exterior_lights_label)


        # Temperature
        temp_button_layout = QVBoxLayout()
        temp_layout = QHBoxLayout()
        temp_display = QLineEdit()
        temp_display.setText(str(train.temperature))

        temp_layout.addWidget(temp_display)
        temp_layout.addLayout(temp_button_layout)
        train.signals.new_temp.connect(lambda: temp_display.setText(str(train.temperature)))

        outputs.addLayout(temp_layout)
        temp_label = QLabel("Temperature")
        temp_label.setAlignment(Qt.AlignRight)
        outputs.addWidget(temp_label)

        # Announcements
        announcements_layout = QVBoxLayout()
        ann_label = QLabel("Announcements")
        ann_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        ann_status = QLineEdit()
        ann_status.setReadOnly(True)
        train.signals.broadcast_announcements.connect(ann_status.setText)

        announcements_layout.addWidget(ann_status)
        announcements_layout.addWidget(ann_label)


        outputs.addLayout(announcements_layout)

        # Advertisements
        advertisements_layout = QVBoxLayout()
        ad_label = QLabel("Advertisements")
        ad_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        ad_status = QLineEdit()
        ad_status.setReadOnly(True)
        train.signals.broadcast_advertisements.connect(ad_status.setText)

        advertisements_layout.addWidget(ad_status)
        advertisements_layout.addWidget(ad_label)


        outputs.addLayout(advertisements_layout)


        inputs_left.addStretch()
        inputs_right.addStretch()
        outputs.addStretch()

        widgets = QGridLayout()
        # widgets.addLayout(inputs_left, 1, 0, Qt.AlignmentFlag.AlignTop)
        # widgets.addLayout(inputs_right, 1, 1, Qt.AlignmentFlag.AlignTop)
        # widgets.addLayout(outputs, 1, 2, Qt.AlignmentFlag.AlignTop)
        widgets.addLayout(inputs_left, 1, 0)
        widgets.addLayout(inputs_right, 1, 1)
        widgets.addLayout(outputs, 1, 2)


        widget = Color('light blue')
        widget.setLayout(widgets)
        self.setCentralWidget(widget)

    def failure_applied(self, train, status, status_widget):
        pass

    def set_train_status(self, train, status_widget):
        pass

    def on_driver_mode_changed(self, train, new_mode):
        print("[TRAIN]: CHANGING MODE")
        train.set_mode(new_mode)

    def set_PID_Gains(self, Kp, Ki, train):
        train.set_PID_gains(Kp=Kp, Ki=Ki)

    def run_simulation(self, train, runtime):
        # train_thread = RunTrainThread(train, runtime)
        # train_thread.run()
        pass

    def __del__(self):
        print(f"[TRAIN]: Train Controller Test Window Window deleted.")

