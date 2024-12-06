import sys
sys.path.append('.')

from time import sleep
# from core.mock_train_controller import Train_Controller
from train.train_controller.train_controller_class import TrainController
from train.core.train_model import Train_Model
from train.train_model.inc.run_control import monitor_loop

from PySide6.QtCore import QRunnable, Slot, QObject, Slot, Signal

class Train_Signals(QObject):
    updated = Signal()
    actual_velocity = Signal(float)
    # commanded_velocity = Signal(float)
    # acceleration = Signal(float)
    # grade = Signal(float)
    # current_mass = Signal(float)
    power = Signal(float)
    # position = Signal(float)
    controller_power_command = Signal(float)
    # brake_applied = Signal(str)


class Train(QRunnable):
    def __init__(self, identifier : int):

        # Initialize QRunnable
        super().__init__()

        # Initialize Train
        self.train_model = Train_Model()
        # self.train_model.set_grade(-0.5)
        self.train_model.set_grade(0)
        self.controller = TrainController()
        self.controller.index = identifier
        self.controller.set_PID_gains(500000,500000)
        ## same here- commanded speed should be 0 to start
        self.identifier = identifier

        self.train_model.toggle_ext_lights()

        # Internal Vars
        self.power_command = 0

        # Setup Clock
        self.time_sec = 0
        self.dt_sec = 0.1
        self.speed_up = 1.0
        self.is_paused = False

        # Setup Signals
        self.signals = Train_Signals()

        self.position_m = 0

        # Update Limit
        # self.update_freq = 10 #hz
        # self.update_time_limit = 1/ self.update_freq

        # Kill Flag
        self.kill = False

        self.connect_modules()

    def connect_modules(self):
        # Temperature 
        self.controller.signals.new_temp.connect(self.train_model.set_temp)

        # Doors
        self.controller.signals.open_all_doors.connect(self.train_model.open_all_doors)
        self.controller.signals.open_left_doors.connect(self.train_model.open_left_door)
        self.controller.signals.open_right_doors.connect(self.train_model.open_right_door)
        self.controller.signals.close_all_doors.connect(self.train_model.close_all_doors)
        self.controller.signals.close_left_doors.connect(self.train_model.close_left_door)
        self.controller.signals.close_right_doors.connect(self.train_model.close_right_door)


        # Lights
        self.controller.signals.toggle_interior_lights.connect(self.train_model.toggle_int_lights)
        self.controller.signals.toggle_exterior_lights.connect(self.train_model.toggle_ext_lights)

        # Ads/Announcements
        self.controller.signals.broadcast_advertisements.connect(self.train_model.set_advertisement)
        self.controller.signals.broadcast_announcements.connect(self.train_model.set_announcements)
        self.controller.signals.new_station.connect(self.train_model.set_station_name)

        # Ebrake
        self.train_model.sig.set_pass_ebrake.connect(self.controller.passenger_ebrake_applied)
        # self.train_model.sig.clear_pass_ebrake.connect(self.controller.clear_passenger_ebrake)
        
        # Commanded Speed

        # Failures
        self.train_model.sig.set_brake_failure.connect(self.controller.receive_brake_failure) # thhis is actually the brake failure
        self.train_model.sig.clear_brake_failure.connect(self.controller.clear_brake_failure)
        self.train_model.sig.set_engine_failure.connect(self.controller.receive_engine_failure)
        self.train_model.sig.set_engine_failure.connect(self.controller.clear_engine_failure)
        self.train_model.sig.set_signal_pickup_failure.connect(self.controller.receive_signal_pickup_failure)
        self.train_model.sig.set_signal_pickup_failure.connect(self.controller.clear_signal_pickup_failure)

        # Physics
        self.train_model.sig.entered_new_block.connect(self.controller.enter_new_block)

        # Track Circuit
        self.train_model.sig.get_speed_track_circuit.connect(self.controller.set_commanded_speed_CTC_m_s)
        self.train_model.sig.get_authority_track_circuit.connect(self.controller.set_authority_blocks)

        # Beacon
        self.train_model.sig.get_beacon_data.connect(self.controller.receive_beacon_info)



    # TODO: idk if this these two functions are safe to call?
    def get_identifier(self):
        return self.identifier
    
    def delete(self):
        self.kill = True

    @Slot()
    def run(self):
        actual_velocity = 0
        self.power_command = 0

        # send_start_time = timer()
        # loop_start_time = timer()
 
        # while self.time_sec < 60*4:
        while True:
            sleep(self.dt_sec/ self.speed_up)

            # something with timers and multithreading it hates. and makes it very slow
            # end = timer() - loop_start_time
            # if(end > (self.dt_sec/self.speed_up)):
            #     loop_start_time = timer()
            #     # print(f"[TRAIN]: {timer()}, 0.1")

            while self.is_paused:
                pass

                

            if self.kill:
                break

            # run the temp contoller
            self.train_model.run_temp_loop()
                
            # run the controller
            # self.power_command = self.controller.run(actual_velocity_mps= actual_velocity, set_velocity_mps= self.controller.get_commanded_speed(), delta_t_sec = self.dt_sec)
            self.power_command = self.controller.output_power(actual_velocity)
            # power_cmd2 = self.controller.output_power(actual_velocity)
            # self.power_command = min(power_cmd1, power_cmd2)

            # feed controller output into plant
            actual_velocity = self.train_model.run(input_power_w= self.power_command, delta_t_sec= self.dt_sec)

            # emit back to main app
            # if (timer() - send_start_time) > self.update_time_limit:
            
            self.signals.actual_velocity.emit(actual_velocity)
            self.controller.set_current_speed_m_s(actual_velocity)
            # self.signals.commanded_velocity.emit(self.controller.commanded_speed)
            # self.signals.acceleration.emit(self.train_model.accel_mps2/9.8)
            # self.signals.grade.emit(self.train_model.grade)
            # self.signals.current_mass.emit(self.train_model.mass_kg)
            self.signals.power.emit(self.train_model.output_power)
            # self.signals.brake_applied.emit(self.train_model.brake_applied)
            # self.signals.position.emit(self.train_model.position_m)
            self.signals.controller_power_command.emit(self.power_command)
            self.signals.updated.emit()
                # send_start_time = timer()

            self.time_sec += self.dt_sec

            monitor_loop()

        print(f"[TRAIN]: Train with identifier {self.identifier} has exited while loop.")

    def __del__(self):
        print(f"[TRAIN]: Train with identifier {self.identifier} has been deleted.")


   
            
