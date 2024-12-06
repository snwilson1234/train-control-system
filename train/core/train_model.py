import math
import random
from timeit import default_timer as timer
from train.train_model.inc.train_model_enum import *
from train.core.mock_beacon import Beacon

from PySide6.QtCore import QObject, Signal

class Train_Model_Internal_Signals(QObject):
    set_engine_failure = Signal()
    set_brake_failure = Signal()
    set_signal_pickup_failure = Signal()
    clear_engine_failure = Signal()
    clear_brake_failure = Signal()
    clear_signal_pickup_failure = Signal()
    set_pass_ebrake = Signal()
    clear_pass_ebrake = Signal()
    entered_new_block = Signal()
    get_speed_track_circuit = Signal(float)
    get_authority_track_circuit = Signal(float)
    get_beacon_data = Signal(list)
    disembark_passengers = Signal()
    air_conditioning_status = Signal(bool)
    passengers_changed = Signal(int)
    grade_updated = Signal(float)
class Train_Model:

    # Global Physics 
    # TODO: convert to scream snake case
    fully_loaded_mass_kg = 56700 # 56.7 metric tons
    no_load_mass_kg =  40900 # 40.9 metric tons
    mass_range_kg = (fully_loaded_mass_kg - no_load_mass_kg)
    nominal_mass_kg = no_load_mass_kg + (mass_range_kg*2/3) #nominal mass is 2/3 loaded
    max_acceleration_mps2 = 0.5
    max_engine_force_N = nominal_mass_kg * max_acceleration_mps2
    brake_deceleration_mps2 = -1.2
    max_braking_force_N = nominal_mass_kg * brake_deceleration_mps2
    max_power_w = 120000 
    g_mps2 = -9.8
    ebrake_deceleration_mps2 = -2.73
    max_seated_passengers = 74
    max_standing_passengers = 148
    max_passengers = max_seated_passengers + max_standing_passengers
    PASSENGER_WEIGHT_KG = (fully_loaded_mass_kg - no_load_mass_kg) / max_passengers

    # Temp Loop Control Settings
    PERCENT_OLD_VAL = 0.95
    PERCENT_NEW_VAL = 1 - PERCENT_OLD_VAL
    MAX_TEMP_F = 85
    MIN_TEMP_F = 50

    # Physics Settings
    use_static_braking = False

    def __init__(self) -> None:
        
        # Mass
        self.mass_kg = Train_Model.no_load_mass_kg

        # Engine and Power
        self.max_engine_force_N = Train_Model.max_engine_force_N
        self.output_power = 0.0

        # Acceleration
        self.accel_mps2 = 0.0
        self.prev_accel_mps2 = 0.0
        self.accel_no_grade_mps2 = 0.0

        # Velocity 
        self.velocity_mps = 0.0
        self.prev_velocity_mps = 0.0
        self.velocity_max = 0.0
        self.velocity_min = 0.0

        # Grade Calculation
        self.grade = 0.5
        self.grade_dec = self.grade / 100
        self.cur_block_length_m = 75
        
        # Entered new block
        self.entered_new_block_pending_update = False

        # Service Brake
        self.brake_applied = "NO"

        # Failures and ebrakes
        self.engine_fail = False
        self.brake_fail = False
        self.signal_pickup_fail = False
        self.driver_ebrake = False 
        self.passenger_ebrake = False 
        self.track_power_failure = False

        # Physical Interfaces
        self.left_door = Door.CLOSE
        self.right_door = Door.CLOSE
        self.ext_lights = Lights.OFF
        self.int_lights = Lights.OFF

        # Temp Control
        self.AC_state = True
        self.set_temp_F = 72.0
        self.actual_temp_F = 85.0
        self.prev_temp_F = self.actual_temp_F

        # Track Circuit
        self.commanded_speed_mps = 0.0
        self.authority_blocks = 0

        # Beacon Data
        self.station_name = ""
        self.station_side = ""
        self.tunnel_light_toggle = False

        # Passengers
        self.crew_count = 5 # one driver, 2 people for tickets, 1 person per multipurpose room (2 total)
        self.passenger_count = 0
        random.seed(int(timer()))
        self.update_mass()

        # Info Center
        self.announcements_str = ""
        self.advertisements_str = ""

        # Signals
        self.sig = Train_Model_Internal_Signals()

    ##########################################
    #### BEACON
    ##########################################

    # this is data coming from the beacon
    def set_beacon_data(self,data: str) -> None:
        print(f"[TRAIN]: data in beacon {data}")
        self.station_side, self.station_name, self.tunnel_light_toggle = data.split(f'{Beacon.DELIM}')
        self.sig.get_beacon_data.emit(self.get_beacon_data())
        
    # this is the data stored internally. returns beacon data that was read 
    # in the last time set_beacon_data() was called.
    def get_beacon_data(self) -> list:
        if self.tunnel_light_toggle == "1":
            return [self.station_side, self.station_name, "1"]
        elif self.tunnel_light_toggle == "0":
            return [self.station_side, self.station_name, "0"]
        else:
            print("[TRAIN]: something went wrong")

    
    def get_station_name(self) -> str:
        return self.station_name
    

    ##########################################
    #### PASSENGERS
    ##########################################

    def disembark_passengers(self) -> None:
        self.removed_passengers = random.randint(0,self.passenger_count)
        self.passenger_count -= self.removed_passengers
        self.update_mass()
        print("[TRAIN]: disembarking passengers")
        
    def disembark_all_passengers(self) -> None:
        self.passenger_count = 0
        self.update_mass()

    # this function takes a parameter and boards on exactly that number of people
    # from the video (9:15)
    # the ticket sales are the number of people that buy a ticket and go stand on the station, they don't necessarily all board
    # the track model is supposed to randomly choose how many people board from the station on the train.
    def onboard_passengers(self, num : int) -> None:
        if(self.left_door != Door.OPEN and self.right_door != Door.OPEN):
            print("[TRAIN]: CANNOT ONBOARD PASSENGERS, DOORS NOT OPEN")
            return

        if( (self.passenger_count + self.crew_count + num) <= Train_Model.max_passengers):
            self.passenger_count += num
        else:
            self.passenger_count = Train_Model.max_passengers - self.crew_count

        self.update_mass()
        self.sig.disembark_passengers.emit() # this is actually a signa that passengers are onboard to tell her to close doors

        self.sig.passengers_changed.emit(self.passenger_count)
        print("[TRAIN]: onboarding passengers")



    def get_passenger_count(self) -> int:
        return self.passenger_count

    def get_crew_count(self) -> int:
        return self.crew_count
    
    def update_mass(self) -> None:
        self.mass_kg = Train_Model.no_load_mass_kg + (self.crew_count + self.passenger_count)* Train_Model.PASSENGER_WEIGHT_KG
        
        
    ##########################################
    #### INFO CENTER
    ##########################################

    def set_advertisement(self, data : str) -> None:
        self.advertisements_str = data

    def set_announcements(self, data : str) -> None:
        self.announcements_str = data

    def set_station_name(self, data : str) -> None:
        self.station_name = data

    def get_advertisement(self) -> str:
        return self.advertisements_str

    def get_announcements(self) -> str:
        return self.announcements_str

    ##########################################
    #### DOORS
    ##########################################

    def set_right_door(self, state : Door) -> None:
        self.right_door = state
        if self.right_door == Door.OPEN:
            # assume door is open cause its at a station 
            # and people need to get off
            self.disembark_passengers()

    def set_left_door(self, state : Door) -> None:
        self.left_door = state
        if self.left_door == Door.OPEN:
            # assume door is open cause its at a station 
            # and people need to get off
            self.disembark_passengers()

    def get_right_door(self) -> bool:
        return bool(self.right_door.value)
    
    def get_left_door(self) -> bool:
        return bool(self.left_door.value)

    def set_doors(self, l_state : Door, r_state : Door) -> None:
        self.right_door = r_state
        self.left_door = l_state

    def toggle_both_doors(self):
        print(f"[TRAIN]: before toggle both doors, state is R: {self.right_door}, L {self.left_door}")
        door_opened = False

        if(self.right_door is Door.CLOSE):
            self.right_door = Door.OPEN
            door_opened = True
        else:
            self.right_door = Door.CLOSE

        if(self.left_door is Door.CLOSE):
            self.left_door = Door.OPEN
            door_opened = True
        else:
            self.left_door = Door.CLOSE

        if door_opened:
            self.disembark_passengers()

        print(f"[TRAIN]: after toggle both doors, state is R: {self.right_door}, L {self.left_door}")

    def open_all_doors(self):
        print(f"[TRAIN]: before open both doors, state is R: {self.right_door}, L {self.left_door}")
        self.right_door = Door.OPEN
        self.left_door = Door.OPEN
        self.disembark_passengers()

    def close_all_doors(self):
        print(f"[TRAIN]: before close both doors, state is R: {self.right_door}, L {self.left_door}")
        self.right_door = Door.CLOSE
        self.left_door = Door.CLOSE

    def toggle_right_door(self):
        print(f"[TRAIN]: before toggle right door, state is R: {self.right_door}, L {self.left_door}")
        if(self.right_door is Door.CLOSE):
            self.right_door = Door.OPEN

            # assume door is open cause its at a station 
            # and people need to get off
            self.disembark_passengers()

        else:
            self.right_door = Door.CLOSE

        print(f"[TRAIN]: after toggle right door, state is R: {self.right_door}, L {self.left_door}")

    def open_right_door(self):
        print(f"[TRAIN]: before open right door, state is R: {self.right_door}, L {self.left_door}")
        self.right_door = Door.OPEN
        self.disembark_passengers()

    def close_right_door(self):
        print(f"[TRAIN]: before open right door, state is R: {self.right_door}, L {self.left_door}")
        self.right_door = Door.CLOSE


    def close_left_door(self):
        print(f"[TRAIN]: before close left door, state is R: {self.right_door}, L {self.left_door}")
        self.left_door = Door.CLOSE

    def open_left_door(self):
        print(f"[TRAIN]: before open left door, state is R: {self.right_door}, L {self.left_door}")
        self.left_door = Door.OPEN
        self.disembark_passengers()

    def toggle_left_door(self):
        print(f"[TRAIN]: before toggle left door, state is R: {self.right_door}, L {self.left_door}")
        if(self.left_door is Door.CLOSE):
            self.left_door = Door.OPEN

            # assume door is open cause its at a station and people
            # need to get off
            self.disembark_passengers()
        else:
            self.left_door = Door.CLOSE

        print(f"[TRAIN]: after toggle left door, state is L: {self.right_door}, R {self.left_door}")

    ##########################################
    #### LIGHTS
    ##########################################

    def set_ext_lights(self, state : Lights) -> None:
        self.ext_lights = state

    def set_int_lights(self, state : Lights) -> None:
        self.int_lights = state

    def toggle_ext_lights(self) -> None:
        if self.ext_lights == Lights.ON:
            self.ext_lights = Lights.OFF
        else:
            self.ext_lights = Lights.ON

    def toggle_int_lights(self) -> None:
        if self.int_lights == Lights.ON:
            self.int_lights = Lights.OFF
        else:
            self.int_lights = Lights.ON

    def get_ext_lights(self) -> bool:
        return bool(self.ext_lights.value)
    
    def get_int_lights(self) -> bool:
        return bool(self.int_lights.value)
            

    ##########################################
    #### FAILURES AND EBRAKES
    ##########################################
    def handle_track_power_failure(self, state : bool) -> None:
        self.track_power_failure = state
        if self.track_power_failure:
            self.engine_fail = True
            self.sig.set_engine_failure.emit()

    def toggle_engine_failure(self) -> None:
        self.engine_fail = not self.engine_fail

        if self.track_power_failure:
            self.engine_fail = True

        if self.engine_fail: self.sig.set_engine_failure.emit()
        else: self.sig.clear_engine_failure.emit()
            
    def toggle_brake_failure(self) -> None:
        self.brake_fail = not self.brake_fail
        if self.brake_fail: self.sig.set_brake_failure.emit()
        else: self.sig.clear_brake_failure.emit()

    def toggle_signal_pickup_failure(self) -> None:
        self.signal_pickup_fail = not self.signal_pickup_fail
        if self.signal_pickup_fail: self.sig.set_signal_pickup_failure.emit()
        else: self.sig.clear_signal_pickup_failure.emit()

    def toggle_pass_ebrake(self) -> None:
        self.passenger_ebrake = not self.passenger_ebrake
        if self.passenger_ebrake: self.sig.set_pass_ebrake.emit()
        else: self.sig.clear_pass_ebrake.emit()

    def toggle_driver_ebrake(self) -> None:
        self.driver_ebrake = not self.driver_ebrake

    def get_engine_failure(self) -> bool:
        return self.engine_fail
    
    def get_brake_failure(self) -> bool:
        return self.brake_fail
    
    def get_signal_pickup_failure(self) -> bool:
        return self.signal_pickup_fail
    
    def get_pass_ebrake(self) -> bool:
        return self.passenger_ebrake
    
    def get_driver_ebrake(self) -> bool:
        return self.driver_ebrake

    ##########################################
    #### PHYSICS / DIRECT INFO
    ##########################################

    def set_grade(self, new_grade : float) -> None:
        # print(f"[TRAIN MODEL]: NEW GRADE {new_grade}")
        self.grade = new_grade
        self.grade_dec = new_grade/100
        self.sig.grade_updated.emit(self.grade)

    def set_block_length(self, new_bl : int) -> None:
        # print(f"[TRAIN MODEL]: NEW BLOCK LENGTH {new_bl}")
        self.cur_block_length_m = new_bl

    def entered_new_block(self) -> None:
        self.entered_new_block_pending_update = True
        self.sig.entered_new_block.emit()
        print("[TRAIN]: Entered new block flag set.")

    def get_entered_new_block(self) -> bool:
        if self.entered_new_block_pending_update:
            self.entered_new_block_pending_update = False
            return True
        return False

    ##########################################
    #### TRACK CIRCUIT
    ##########################################

    # just sets the track circuit data so that it can be forwarded to train controller
    def set_track_circuit_data(self, new_speed_mps : float, new_authority_blocks : int):
        if(self.signal_pickup_fail):
            return
    
        # print(new_speed_mps)
        
        self.commanded_speed_mps = new_speed_mps
        self.authority_blocks = new_authority_blocks

        print(f"[TRAIN]: Set Track Circuit Data: {self.commanded_speed_mps} and {self.authority_blocks}")

        self.sig.get_speed_track_circuit.emit(self.commanded_speed_mps)
        self.sig.get_authority_track_circuit.emit(self.authority_blocks)


    def get_track_circuit_data(self) -> tuple:
        return (self.commanded_speed_mps, self.authority_blocks)

    ##########################################
    #### TEMP CONTROL
    ##########################################
    
    def run_temp_loop(self) -> None:
        
        self.actual_temp_F = self.set_temp_F * Train_Model.PERCENT_NEW_VAL + \
                             self.prev_temp_F * Train_Model.PERCENT_OLD_VAL
        
        self.prev_temp_F = self.actual_temp_F  

        if (abs(self.set_temp_F - self.actual_temp_F) < 1e-3):
            self.actual_temp_F = self.set_temp_F
            self.AC_state = Air_Conditioning.OFF
        else:
            self.AC_state = Air_Conditioning.ON

        self.sig.air_conditioning_status.emit(bool(self.AC_state.value))

    def set_temp(self, val_F: float):
        self.set_temp_F = val_F
        if self.set_temp_F > Train_Model.MAX_TEMP_F:
            self.set_temp_F = Train_Model.MAX_TEMP_F
        elif self.set_temp_F < Train_Model.MIN_TEMP_F:
            self.set_temp_F = Train_Model.MIN_TEMP_F


    ##########################################
    #### TRAIN MODEL PHYSICS & CONTROL LOOP
    ##########################################

    def calculate_grade_force(self) -> float:
        theta = math.atan(self.grade_dec) # returns in radians
        force_x = math.sin(theta) * Train_Model.g_mps2 * self.mass_kg
        return force_x
    
    def get_actual_vel(self) -> float:
        return self.velocity_mps

    def run(self, input_power_w: float, delta_t_sec : float) -> float:

        grade_force_N = self.calculate_grade_force()
        engine_force_N = 0 # should always be positive
        braking_force_N = 0 
        ebrake_acc_mps2 = 0

        # power input is positive
        if(input_power_w > 0 and not self.engine_fail):
            
            self.brake_applied="NO"
            
            # if power command above engine max power, set to engine max power
            if(input_power_w > Train_Model.max_power_w):
                input_power_w = Train_Model.max_power_w

            self.output_power = input_power_w / 10e3

            
            try:
                # engine force should always be positive
                engine_force_N = input_power_w / abs(self.velocity_mps)

                if(engine_force_N > self.max_engine_force_N):
                    engine_force_N = self.max_engine_force_N

            except ZeroDivisionError:
                engine_force_N = self.max_engine_force_N
            
        # train is braking
        elif(input_power_w < 0 and not self.brake_fail):
            self.brake_applied="YES"
            self.output_power = 0
            
            # constant braking
            if Train_Model.use_static_braking:
                braking_force_N = Train_Model.max_braking_force_N
            
            # dynamic braking
            else:
                try:
                    # braking force should always be negative, input power is negative here
                    # correction: braking force is always in the opposite direction of travel. 
                    # but it doesnt really matter when vel is negative cause ebrake will pulled.
                    braking_force_N = input_power_w / self.velocity_mps

                    if(braking_force_N < self.max_braking_force_N):
                        braking_force_N = self.max_braking_force_N

                except ZeroDivisionError:
                    braking_force_N = self.max_braking_force_N
    
        # input power is zero
        else:
            self.brake_applied="NO"            
            self.output_power = 0
            # engine and braking power are zero (already true)

        # handle the case where the brake should still be applied if input is negative but there is 
        # a brake failure. Altho the applied brake will not do anything
        if (input_power_w < 0 and self.brake_fail):
                self.brake_applied="YES"

        # calculate acceleration due to braking force
        braking_acc_mps2 = braking_force_N / self.mass_kg #braking force should be negative
        if(braking_acc_mps2 < Train_Model.brake_deceleration_mps2): #check if braking_acc is more negative
            braking_acc_mps2 = Train_Model.brake_deceleration_mps2

        # calculate acceleration due to engine
        engine_acc_mps2 = engine_force_N / self.mass_kg
        if(engine_acc_mps2 > Train_Model.max_acceleration_mps2): #check if engine acc is above max acc
            engine_acc_mps2 = Train_Model.max_acceleration_mps2

        # Set acceleration due to ebrake
        if(self.passenger_ebrake or self.driver_ebrake):
            
            # Determine whether ebrake acceleration should be positive or negative depending on when it was applied
            # Set velocity limits to print the ebrake acceleration from driving the train:
                # less than zero when ebrake applied when vel was positive
                # above zero when ebrake applied when vel was negative. 
            # this only happens due to integration errors and would not happen in the real world
            if self.velocity_mps < 0:
                ebrake_acc_mps2 = -1*Train_Model.ebrake_deceleration_mps2
                self.velocity_max = 0
                self.velocity_min = -10e3
            else:
                ebrake_acc_mps2 = Train_Model.ebrake_deceleration_mps2
                self.velocity_max = 10e3
                self.velocity_min = 0

        # calculate final acceleration of the train
        # print(f"[TRAIN]: {grade_force_N/self.mass_kg}, {braking_acc_mps2}")
        self.accel_mps2 = engine_acc_mps2 + braking_acc_mps2 + grade_force_N/self.mass_kg + ebrake_acc_mps2

        # calculate the final acceleration without considering the grade for the UI G's calc
        self.accel_no_grade_mps2 = self.accel_mps2 - grade_force_N / self.mass_kg
        
        # do this because there will still be an acceleration when the velocity is zero because either 
        # ebrake or normal brake will be applied. but the acceleration is constant so set to zero.
        if self.velocity_mps == 0:
            self.accel_no_grade_mps2 = 0


        # calculate velocity
        # print(f"[TRAIN]: {self.prev_velocity_mps} + ({delta_t_sec}/2)*({self.accel_mps2} + {self.prev_accel_mps2})")
        self.velocity_mps = self.prev_velocity_mps + (delta_t_sec/2)*(self.accel_mps2 + self.prev_accel_mps2)

        # train cannot move backwards so prevent negative velocities the calculation above. 
        # in a real model, friction would bring the velocity to zero (and not below it)
        if(self.velocity_mps < 0):
            # only apply the rule of setting negative vel to zero if the engine is running normally.
            # if the train is on a positive grade, the train will roll downhill, allow this to happen
            if(not self.engine_fail):
                self.velocity_mps = 0

        # velocity overrides for when ebrake is applied for reason detailed above when setting ebrake accel
        # only apply these vel overrides when ebrake is active.
        if self.passenger_ebrake or self.driver_ebrake:
            if self.velocity_mps > self.velocity_max:
                self.velocity_mps = self.velocity_max
            elif self.velocity_mps < self.velocity_min:
                self.velocity_mps = self.velocity_min        
    
        # store values for the next calculation
        self.prev_accel_mps2 = self.accel_mps2
        self.prev_velocity_mps = self.velocity_mps
    
        # returns actual velocity
        return self.velocity_mps
    
    def __del__(self):
        print("[TRAIN]: Actual Train Model object deleted.")