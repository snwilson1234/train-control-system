import sys

from train.core.train import Train
from train.train_controller.train_controller_class import *
from train.train_model.ui.custom_widgets import AnimatedToggle, Color
from PySide6.QtCore import QTimer


sys.path.append('.')
from utils.UI import *


class DriverWindow(QMainWindow):

    def __init__(self, train: TrainController):
        super().__init__()
        self.train_controller = train
        self.timer = QTimer()

        self.__create_driver_window()

    def __create_driver_window(self):
        # self.train_controller.set_current_speed_m_s()
        self.__create_page()

    def __create_page(self):
        self.setWindowTitle("Train Controller - Driver Window")


        # page_layout = QVBoxLayout()

        top_left_layout = QHBoxLayout()
        cs_layout = QVBoxLayout()

        # Current Speed
        self.current_speed = QLineEdit()
        self.current_speed.setReadOnly(True)
        current_speed_label = QLabel("Current Speed (mph)")
        current_speed_label.setAlignment(Qt.AlignRight)
        self.current_speed.setText(str(self.train_controller.get_current_speed_mph()))
        self.train_controller.signals.current_speed_set.connect(lambda: self.current_speed.setText(str(self.train_controller.get_current_speed_mph())))

        cs_layout.addWidget(self.current_speed)
        cs_layout.addWidget(current_speed_label)

        # Speed Limit
        speed_limit_layout = QVBoxLayout()
        ## TODO: speed limit = CTC commanded speed
        speed_limit = QLineEdit()
        speed_limit.setText("70mph")
        self.train_controller.signals.new_CTC_speed.connect(lambda: speed_limit.setText(str(int(self.train_controller.get_ctc_commanded_speed_mph())) + "mph"))
        speed_limit.setReadOnly(True)
        speed_limit.setMinimumSize(75, 75)
        speed_limit.setMaximumSize(75, 75)
        speed_limit.setAlignment(Qt.AlignCenter)
        speed_limit_label = QLabel("Speed Limit")
        speed_limit_layout.addWidget(speed_limit)
        speed_limit_layout.addWidget(speed_limit_label)
        speed_limit_layout.setAlignment(Qt.AlignCenter)
        # cs_layout.addLayout(create_line_no_edit("Speed Limit", default_text="70 mph"))


        # Commanded Speed
        self.status_bar = QTextEdit()
        self.status_bar.setMinimumSize(400, 75)
        self.status_bar.setReadOnly(True)
        # ## TODO: signal here to receieve commanded speed
        status_bar_label = QLabel("Train Status")
        status_bar_label.setAlignment(Qt.AlignRight)
        self.status_bar.setText(str(self.train_controller.get_current_status()))

        status_layout = QVBoxLayout()
        status_layout.addWidget(self.status_bar)
        status_layout.addWidget(status_bar_label)

        def receive_status(status: str):
            self.status_bar.setText(status)
            if status == TrainStatus.DRIVER_EBRAKE:
                self.status_bar.setStyleSheet("background-color: red")

        self.train_controller.signals.new_status.connect(receive_status)



        # Doors
        ## TODO: update door status based on open_all_doors() signal

        door_right = AnimatedToggle()
        door_right_label = QLabel("Right")
        door_right_label.setAlignment(Qt.AlignCenter)
        door_left = AnimatedToggle()
        door_left_label = QLabel("Left")
        door_left_label.setAlignment(Qt.AlignCenter)

        left_button_layout = QVBoxLayout()
        left_button_layout.addWidget(door_left)
        left_button_layout.addWidget(door_left_label)

        right_button_layout = QVBoxLayout()
        right_button_layout.addWidget(door_right)
        right_button_layout.addWidget(door_right_label)

        door_layout = QHBoxLayout()
        door_layout.addLayout(left_button_layout)
        door_layout.addLayout(right_button_layout)
        door_total_layout = QVBoxLayout()
        door_label = QLabel("Doors")
        door_label.setAlignment(Qt.AlignCenter)
        door_total_layout.addWidget(door_label)
        door_total_layout.addLayout(door_layout)

        self.train_controller.signals.open_left_doors.connect(lambda: door_left.setChecked(True))
        self.train_controller.signals.open_right_doors.connect(lambda: door_right.setChecked(True))
        self.train_controller.signals.open_all_doors.connect(lambda: door_left.setChecked(True))
        self.train_controller.signals.open_all_doors.connect(lambda: door_right.setChecked(True))

        ## TODO: test w/ door closing from track model 

        # Driver input auto/manual mode
        door_right.clicked.connect(lambda: open_doors())
        door_left.clicked.connect(lambda: open_doors())
        # door_right.stateChanged.connect(lambda: open_doors())
        # door_left.stateChanged.connect(lambda: open_doors())
        def open_doors():
            if door_right.isChecked():
                if not self.train_controller.driver_open_door("Right"):
                    door_right.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.train_controller.driver_close_door("Right")
            if door_left.isChecked():
                if not self.train_controller.driver_open_door("Left"):
                    # don't set checked state
                    door_left.setCheckState(Qt.CheckState.Unchecked)

            else:
                self.train_controller.driver_close_door("Left")

        # Lights
        exterior_lights = AnimatedToggle()
        exterior_label = QLabel("Exterior")
        exterior_label.setAlignment(Qt.AlignCenter)
        interior_lights = AnimatedToggle()
        interior_label = QLabel("Interior")
        interior_label.setAlignment(Qt.AlignCenter)


        def set_light_status():
            if self.train_controller.interior_light_status == Lights.ON:
                interior_lights.setChecked(True)
            else:
                interior_lights.setCheckState(Qt.CheckState.Unchecked)

            if self.train_controller.exterior_light_status == Lights.ON:
                exterior_lights.setChecked(True)
            else:
                exterior_lights.setCheckState(Qt.CheckState.Unchecked)


        self.train_controller.signals.toggle_interior_lights.connect(set_light_status())

        exterior_layout = QVBoxLayout()
        exterior_layout.addWidget(exterior_lights)
        exterior_layout.addWidget(exterior_label)

        interior_layout = QVBoxLayout()
        interior_layout.addWidget(interior_lights)
        interior_layout.addWidget(interior_label)

        lights_layout = QHBoxLayout()
        lights_layout.addLayout(exterior_layout)
        lights_layout.addLayout(interior_layout)
        lights_total_layout = QVBoxLayout()
        lights_label = QLabel("Lights")
        lights_label.setAlignment(Qt.AlignCenter)
        lights_total_layout.addWidget(lights_label)
        lights_total_layout.addLayout(lights_layout)

        exterior_lights.stateChanged.connect(self.train_controller.toggle_exterior_lights)
        interior_lights.stateChanged.connect(self.train_controller.toggle_interior_lights)

        two_row_layout = QVBoxLayout()

        # Upcoming Station
        station_layout = QVBoxLayout()
        station_display = QLineEdit()
        station_display.setMinimumSize(400, 75)
        station_display.setReadOnly(True)
        station_layout.addWidget(station_display)
        station_label = QLabel("Next Station")
        self.train_controller.signals.new_station.connect(station_display.setText)
        station_display.setText(str(self.train_controller.next_station))
        station_label.setAlignment(Qt.AlignRight)
        station_layout.addWidget(station_label)
        station_layout.setAlignment(Qt.AlignVCenter)
        row_layout = QHBoxLayout()
        # row_layout.addLayout(station_layout)

        # Temperature
        temp_button_layout = QVBoxLayout()
        temp_layout = QHBoxLayout()
        temp_display = QLineEdit()
        temp_display.setText(str(self.train_controller.temperature) + "° F")
        temp_display.setAlignment(Qt.AlignCenter)
        temp_display.setMinimumSize(75, 50)
        temp_display.setMaximumSize(75, 50)
        self.train_controller.signals.new_temp.connect(lambda: temp_display.setText(str(self.train_controller.temperature) + "° F"))

        temp_layout.addWidget(temp_display)
        temp_layout.addLayout(temp_button_layout)
        ## TODO: set speed control to current speed
        ## TODO: make driver start in manual mode with commanded speed

        increase_button = create_button("▲", self.train_controller.increase_temp)
        increase_button.setMaximumWidth(100)
        increase_button.clicked.connect(lambda: temp_display.setText(str(self.train_controller.temperature) + "° F"))
        temp_button_layout.addWidget(increase_button)
        decrease_button = create_button("▼", self.train_controller.decrease_temp)
        decrease_button.setMaximumWidth(100)
        decrease_button.clicked.connect(lambda: temp_display.setText(str(self.train_controller.temperature) + "° F"))
        temp_button_layout.addWidget(decrease_button)



        temp_total_layout = QVBoxLayout()
        temp_total_layout.addLayout(temp_layout)
        temp_label = QLabel("Temperature")
        temp_label.setAlignment(Qt.AlignRight)
        temp_total_layout.addWidget(temp_label)

        # row_layout.addLayout(temp_total_layout)

        two_row_layout.addLayout(row_layout)
        # page_layout.addLayout(two_row_layout)

        power_layout = QVBoxLayout()
        power_output_status = QLineEdit()
        power_output_status.setReadOnly(True)
        power_output_status.setAlignment(Qt.AlignCenter)
        power_output_status.setMinimumSize(125, 100)
        power_output_status.setMaximumSize(125, 100)
        power_output_status.font().setPointSize(25)
        power_output_status.setText(str(self.train_controller.power_command_w) + " W")
        power_output_label = QLabel("Power Output")
        power_output_label.setAlignment(Qt.AlignCenter)
        self.train_controller.signals.new_power.connect(power_output_status.setText)
        power_layout.addWidget(power_output_status)
        power_layout.addWidget(power_output_label)

        brake = QPushButton("Brake")
        brake.setMinimumSize(200, 200)
        brake.setMaximumSize(400, 300)

        def on_press():
            print("[TRAIN]: brake pressed")
            self.timer.start(1000)
        def on_release():
            self.timer.stop()
        def every_second_while_pressed():
            print("[TRAIN]: setting commanded speed")
            self.train_controller.set_commanded_speed_m_s(float(self.train_controller.get_commanded_speed_m_s() - 2.5))

        brake.pressed.connect(on_press)
        brake.released.connect(on_release)
        self.timer.timeout.connect(every_second_while_pressed)

        driver_ebrake_clear = QPushButton("Clear EBRAKE")
        driver_ebrake_clear.setDisabled(True)

        driver_ebrake = QPushButton("EBRAKE")
        driver_ebrake.setStyleSheet("background-color: rgb(255,140,140)")
        driver_ebrake.setMinimumSize(100, 200)
        driver_ebrake.setMaximumSize(100, 500)


        def apply_driver_ebrake():
            print("[TRAIN]: ui driver ebrake")
            driver_ebrake.clicked.connect(lambda: driver_ebrake_clear.setEnabled(True))
            driver_ebrake.clicked.connect(lambda: driver_ebrake.setDisabled(True))
            driver_ebrake.clicked.connect(self.train_controller.driver_ebrake_applied)

        driver_ebrake.clicked.connect(apply_driver_ebrake())
        # self.train_controller.signals.UI_ebrake_applied.connect(apply_driver_ebrake())


        driver_ebrake_clear.setMaximumSize(100,200)

        def clear_driver_ebrake():
            clear_enabled = self.train_controller.clear_driver_ebrake()
            if clear_enabled:
                driver_ebrake_clear.clicked.connect(driver_ebrake.setEnabled(True))
                driver_ebrake_clear.clicked.connect(driver_ebrake_clear.setDisabled(True))

        driver_ebrake_clear.clicked.connect(clear_driver_ebrake)



        mode_toggle = AnimatedToggle()
        mode_status = QLineEdit()
        mode_status.setReadOnly(True)
        mode_status.setText(str(self.train_controller.mode))

        mode_toggle.stateChanged.connect(lambda: self.__toggle_mode())
        mode_toggle.stateChanged.connect(lambda: mode_status.setText(str(self.train_controller.mode)))


        # Driver Input Velocity
        velocity_button_layout = QVBoxLayout()
        driver_velocity_layout = QHBoxLayout()
        self.input_velocity = QLineEdit()
        self.input_velocity.setReadOnly(True)
        self.input_velocity.setText(str(self.train_controller.get_current_speed_mph()))

        driver_velocity_layout.addWidget(self.input_velocity)
        driver_velocity_layout.addLayout(velocity_button_layout)

        self.increase_vel_button = create_button("▲")
        self.increase_vel_button.clicked.connect(self.__increase_velocity_button_clicked)
        velocity_button_layout.addWidget(self.increase_vel_button)
        self.decrease_vel_button = create_button("▼")
        self.decrease_vel_button.clicked.connect(self.__decrease_velocity_button_clicked)
        velocity_button_layout.addWidget(self.decrease_vel_button)

        velocity_total_layout = QVBoxLayout()
        velocity_total_layout.addLayout(driver_velocity_layout)
        vel_label = QLabel("Speed Control (mph)")
        vel_label.setAlignment(Qt.AlignCenter)
        velocity_total_layout.addWidget(vel_label)
        velocity_total_layout.setAlignment(Qt.AlignCenter)

        # new layout
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(self.current_speed)
        speed_layout.addWidget(current_speed_label)

        first_row_layout = QHBoxLayout()
        first_row_layout.addLayout(speed_layout)
        first_row_layout.addLayout(door_total_layout)
        first_row_layout.addLayout(lights_total_layout)

        # second row- speed limit/temp
        second_row_layout = QHBoxLayout()
        second_row_layout.addLayout(status_layout)
        second_row_layout.addLayout(speed_limit_layout)
        second_row_layout.addLayout(temp_total_layout)

        # bottom section- next station, power, brakes, speed control
        bottom_layout = QHBoxLayout()
        last_rows_layout = QVBoxLayout()
        third_row_layout = QHBoxLayout()
        third_row_layout.addLayout(station_layout)
        third_row_layout.addLayout(power_layout)
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.addWidget(brake)
        fourth_row_layout.addLayout(velocity_total_layout)
        last_rows_layout.addLayout(third_row_layout)
        last_rows_layout.addLayout(fourth_row_layout)
        bottom_layout.addLayout(last_rows_layout)
        bottom_layout.addWidget(driver_ebrake)
        bottom_layout.addWidget(driver_ebrake_clear)

        # fifth- toggle
        fifth_row_layout = QHBoxLayout()
        fifth_row_layout.addWidget(mode_toggle)
        fifth_row_layout.addWidget(mode_status)
        fifth_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        new_page_layout = QVBoxLayout()

        # first_row_layout.addStretch()
        # second_row_layout.addStretch()
        bottom_layout.addStretch()
        fifth_row_layout.addStretch()

        new_page_layout.addLayout(first_row_layout)
        new_page_layout.addLayout(second_row_layout)
        new_page_layout.addLayout(bottom_layout)
        new_page_layout.addLayout(fifth_row_layout)

        new_page_layout.addStretch()

        mode_toggle.toggle()
        mode_toggle.toggle()


        widget = Color('light blue')
        widget.setLayout(new_page_layout)
        self.setCentralWidget(widget)


    def __increase_velocity_button_clicked(self):
        if self.train_controller.mode is Modes.MANUAL:
            self.train_controller.increase_commanded_speed_mph()
            self.input_velocity.setText(str(round(self.train_controller.get_commanded_speed_mph(),2)))
        else:
            print("[TRAIN]: Train not in Manual mode. Toggle mode to AUTO to adjust speed.")

    def __decrease_velocity_button_clicked(self):
        if self.train_controller.mode is Modes.MANUAL:
            self.train_controller.decrease_commanded_speed_mph()
            self.input_velocity.setText(str(round(self.train_controller.get_commanded_speed_mph(),2)))
        else:
            print("[TRAIN]: Train not in Manual mode. Toggle mode to AUTO to adjust speed.")

    def __toggle_mode(self):
        if self.train_controller.mode is Modes.AUTO:
            print("[TRAIN]: set to manual")
            self.train_controller.set_mode(Modes.MANUAL)
            self.input_velocity.setText(str(self.train_controller.get_commanded_speed_mph()))
            self.input_velocity.setStyleSheet("background-color:rgb(184,232,181);")
            self.current_speed.setStyleSheet("background-color:None;")
            self.increase_vel_button.setEnabled(True)
            self.decrease_vel_button.setEnabled(True)


        else:
            print("[TRAIN]: set to auto")
            self.train_controller.set_mode(Modes.AUTO)
            self.input_velocity.setText("--")
            self.input_velocity.setStyleSheet("background-color:None;")
            self.current_speed.setStyleSheet("background-color:rgb(184,232,181);")
            self.increase_vel_button.setDisabled(True)
            self.decrease_vel_button.setDisabled(True)


    def __del__(self):
        print(f"[TRAIN]: Train Controller Driver Window deleted.")



import unittest

class TestStringMethods(unittest.TestCase):
    def test_velocity(self):
        app = QApplication(sys.argv)
        train = TrainController()
        train_controller_window = DriverWindow(train)
        train_controller_window.show()
        prev_vel = train.commanded_speed_mph
        train_controller_window.increase_vel_button.click()
        self.assertEqual(train.commanded_speed_mph, prev_vel + 1)
