import sys
sys.path.append('../')

from enum import Enum
import random
from time import sleep

from PySide6.QtCore import Signal, QObject

from common.beacon_info_enums import StationSide, StationList
from train.train_model.inc.train_model_enum import Lights

MS_TO_MPH = 2.23694
MPH_TO_MS = 0.44704
DEFAULT_KP = 500000
DEFAULT_KI = 500000

announcements = ["HELLO THIS IS YOUR DRIVER SPEAKING", "HI THE DRIVER IS STILL SPEAKING"]
advertisements = ["BUY COCA-COLA", "PLEASE GET AMAZON PRIME PLEASE"]

class TrainStatus(Enum):
    RUNNING = "Train Operation Normal. All systems operating correctly. "
    DRIVER_EBRAKE = "Driver Ebrake Applied. Stopping."
    PASSENGER_EBRAKE = "Passenger Ebrake Applied. Stopping."
    ENGINE_FAILURE = "Engine failed! No power output, stopping."
    BRAKE_FAILURE = "Brake failure! Unable to slow down. Apply EBRAKE!"
    BRAKE_FAILURE_CLEAR = "Brake failure cleared. Awaiting new speed and authority from CTC."
    SIGNAL_PICKUP_FAILURE = "Signal pickup failure! Unable to receive data from track circuit.  "
    DOOR_STATUS_LEFT = "Doors opening on Left side."
    DOOR_STATUS_RIGHT = "Doors opening on Right side."
    DOOR_CLOSED = "Doors currently closed."
    ENGINE_FAILURE_CLEAR = "Engine failure cleared. Awaiting new speed and authority from CTC."
    SIGNAL_PICKUP_FAILURE_CLEAR = "Signal pickup failure cleared. Awaiting new speed and authority from CTC."


class Modes(Enum):
    AUTO = 1
    MANUAL = 2


class TrainControllerSignals(QObject):
    input_velocity_change = Signal(int)
    set_gains = Signal()
    current_speed_set = Signal(str)
    new_power = Signal(str)
    new_commanded_speed = Signal()
    new_temp = Signal(float)
    new_mode = Signal(Modes)
    new_doors = Signal(StationSide)
    new_status = Signal(str)
    reset_gains = Signal()
    toggle_interior_lights = Signal()
    turn_off_interior_lights = Signal()
    toggle_exterior_lights = Signal()
    open_left_doors = Signal()
    open_right_doors = Signal()
    open_all_doors = Signal()
    close_left_doors = Signal()
    close_right_doors = Signal()
    close_all_doors = Signal()
    brake_failure = Signal()
    broadcast_announcements = Signal(str)
    broadcast_advertisements = Signal(str)
    broadcast_station_name = Signal(str)

    new_station = Signal(str)
    new_CTC_speed = Signal()
    UI_ebrake_applied = Signal()


class TrainController:


    MAX_POWER_W : float = 120000.0  # Max power from datasheet- 120kW

    def __init__(self):
        # Signals
        self.door_opened = False
        self.resume_authority = 0
        self.commanded_speed_mph = 0
        self.signals = TrainControllerSignals()
        # pid_changed = Signal(int)

        self.index = 0
        self.authority = 0
        self.station_ahead = False

        # Mode and commanded speed, either from CTC suggestion (Auto) or driver input (Manual)
        self.mode = Modes.AUTO
        self.commanded_speed_m_s = 0.0
        self.CTC_commanded_speed_m_s = 0.0
        self.current_speed_m_s = 0.0
        self.power_command_w = 0.0
        self.prev_uk = 0.0
        self.uk = 0.0
        self.prev_v_error = 0.0
        self.v_error = 0.0
        self.dt = 0.1

        # PID Gains
        self.PID_lock_flag = False
        self.Kp = float(DEFAULT_KP)
        self.Ki = float(DEFAULT_KI)

        # Failure States
        self.SIGNAL_FAILURE = 0
        self.BRAKE_FAILURE = 0
        self.ENGINE_FAILURE = 0

        # Train Properties
        self.temperature = 72
        self.next_station = ""
        self.door_open_side = StationSide.OPEN_DOORS_LEFT
        self.tunnel_flag = 0

        # Status
        self.current_status = TrainStatus.RUNNING

        # Non-Vital Statuses
        self.doors_open = False
        self.left_door_status = "Closed"
        self.right_door_status = "Closed"
        self.door_status = "Closed"
        self.interior_light_status = Lights.OFF
        self.exterior_light_status = Lights.OFF

        # position
        self.position_m = 0

        # Ebrake applied
        self.EBRAKE_ENABLED = False

        # OP controller powers
        self.went_over_commanded = False
        self.went_under_commanded = False


    def set_PID_gains(self, Kp : float, Ki: float):
        # here, broadcast all signals!
        if not self.PID_lock_flag:
            self.Kp = Kp
            self.Ki = Ki
            self.PID_lock_flag = True
            print("[TRAIN]: Train" + str(self.index) + " PID Gains changed. Kp = " + str(self.Kp) + ", Ki = " + str(self.Ki))
            self.signals.set_gains.emit()

        else:
            print("[TRAIN]: KP Change Failed, lock applied. "
                  "Current Kp = " + str(self.Kp) + ", Ki = " + str(self.Ki))

    def reset_PID_gains(self):
        self.PID_lock_flag = False
        self.Kp = DEFAULT_KP
        self.Ki = DEFAULT_KI
        print("[TRAIN]: PID Values Reset, Kp = " + str(self.Kp) + ", Ki = " + str(self.Ki))
        self.signals.reset_gains.emit()

    def set_mode(self, mode):
        # pre setting
        # in auto going to manual
        if self.mode == Modes.AUTO:
            self.commanded_speed_m_s = self.CTC_commanded_speed_m_s
            self.commanded_speed_mph = self.commanded_speed_m_s * MS_TO_MPH
            self.signals.new_commanded_speed.emit()



        self.mode = mode
        print("[TRAIN]: Train" + str(self.index) + " mode " + str(self.mode))
        self.signals.new_mode.emit(mode)
            

    def set_temperature(self, temperature):
        self.temperature = temperature

    def increase_commanded_speed_mph(self):

        if self.commanded_speed_mph <= (self.CTC_commanded_speed_m_s * MS_TO_MPH):
            self.commanded_speed_mph = round(self.commanded_speed_mph)
            self.commanded_speed_mph += 1
            print("[TRAIN]: Speed increased by 1 mph. Commanded speed = " + str(self.commanded_speed_mph) + " mph.")
        else:
            print("[TRAIN]: Commanded speed = " + str(self.commanded_speed_mph))
        self.commanded_speed_m_s = self.commanded_speed_mph * MPH_TO_MS
        self.signals.new_commanded_speed.emit()

    def decrease_commanded_speed_mph(self):
        if self.commanded_speed_mph != 0:
            self.commanded_speed_mph = round(self.commanded_speed_mph)
            self.commanded_speed_mph -= 1
            print("[TRAIN]: Speed decreased by 1 mph. Commanded speed = " + str(self.commanded_speed_mph) + " mph.")
        else:
            print("[TRAIN]: Commanded speed = " + str(self.commanded_speed_mph))
        self.commanded_speed_m_s = self.commanded_speed_mph * MPH_TO_MS
        self.signals.new_commanded_speed.emit()


    def set_commanded_speed_CTC_m_s(self, speed: float):

        if speed < 0 :
            print("[TRAIN]: Unable to set speed. Commanded speed = " + str(self.commanded_speed_m_s) + " m/s")
            return
        elif self.SIGNAL_FAILURE:
            print("[TRAIN]: Unable to set speed, no track circuit signal pickup. Commanded speed = " + str(self.commanded_speed_m_s) + " m/s")
            return

        elif self.mode == Modes.MANUAL and self.commanded_speed_m_s > speed:
            self.commanded_speed_m_s = speed
            self.commanded_speed_mph = speed * MS_TO_MPH

        if self.EBRAKE_ENABLED:
            print("[TRAIN]: Resume speed set, E-brake engaged.")
            self.resume_speed_m_s = speed
            return
        self.CTC_commanded_speed_m_s = speed
        self.signals.new_CTC_speed.emit()

    def get_ctc_commanded_speed_mph(self):
        return self.CTC_commanded_speed_m_s * MS_TO_MPH


    def set_commanded_speed_m_s(self, speed : float):
        if speed < 0 or speed > self.CTC_commanded_speed_m_s:
            print("[TRAIN]: Unable to set speed. Commanded speed = " + str(self.commanded_speed_m_s) + " m/s")
            return

        if self.EBRAKE_ENABLED:
            print("[TRAIN]: Unable to set commanded speed. E-brake engaged.")
            return

        if speed >= 0:
            self.commanded_speed_m_s = speed
            print("[TRAIN]: Train" + str(self.index) + " commanded speed (m/s) = " + str(speed))
            self.signals.new_commanded_speed.emit()

        # if self.door_closed:
        #     print("[TRAIN]: hey there youre a rock star")
        #     self.toggle_doors()

## TODO: authority 0 should not let the train move


    def get_overall_speed_m_s(self) -> float:
        if self.mode == Modes.AUTO:
            return self.CTC_commanded_speed_m_s
        else:
            return self.commanded_speed_m_s




    def get_commanded_speed_mph(self):
        # TODO: return commanded speed
        if self.mode == Modes.MANUAL:
            return self.commanded_speed_m_s * MS_TO_MPH
        elif self.mode == Modes.AUTO:
            return self.CTC_commanded_speed_m_s * MS_TO_MPH

    def get_commanded_speed_m_s(self):
        if self.mode == Modes.MANUAL:
            return self.commanded_speed_m_s
        elif self.mode == Modes.AUTO:
            return self.CTC_commanded_speed_m_s


    def set_authority_blocks(self, blocks):
        if (blocks == 0):
            self.commanded_speed_m_s = 0
        if self.SIGNAL_FAILURE:
            print("[TRAIN]: Unable to set authority, no track circuit signal pickup. Current authority = " + str(self.authority))
            return
        if self.EBRAKE_ENABLED:
            self.resume_authority = blocks
            print("[TRAIN]: Authority set, E-brake enabled.")
            return
        self.authority = int(blocks)
        print("[TRAIN]: Train" + str(self.index) + " authority = " + str(self.authority))

    def set_current_speed_m_s(self, speed: float):
        self.current_speed_m_s = speed
        self.signals.current_speed_set.emit(str(self.current_speed_m_s))
        # print("[TRAIN]: Train" + str(self.index) + " current speed (m/s) = " + str(self.current_speed_m_s))

    def get_current_speed_m_s(self):
        return self.current_speed_m_s

    def get_current_speed_mph(self):
        return self.current_speed_m_s * MS_TO_MPH



    def receive_brake_failure(self):
        self.BRAKE_FAILURE = 1
        self.set_current_status(TrainStatus.BRAKE_FAILURE)
        print("[TRAIN]: BRAKE FAILING")
        self.signals.brake_failure.emit()
        self.signals.broadcast_announcements.emit("THE BRAKE HAS FAILED. PLEASE PULL THE NEAREST EMERGENCY BRAKE.")


        ## TODO: broadcast brake failure to UIs, urge driver to pull ebrake
        # TODO: enter brake failure here, make sure that signal is sent
        # to output negative power and broadcast to train controller

    def clear_brake_failure(self):
        print("[TRAIN]: Clearing Brake Failure.")
        self.BRAKE_FAILURE = 1
        self.set_current_status(TrainStatus.BRAKE_FAILURE_CLEAR)
        # self.current_status = TrainStatus.BRAKE_FAILURE_CLEAR
        # self.signals.new_status.emit(str(self.current_status.value))


    def receive_engine_failure(self):
        print("[TRAIN]: ENGINE FAILING")
        self.ENGINE_FAILURE = 1
        self.set_current_status(TrainStatus.ENGINE_FAILURE)
        # self.current_status = TrainStatus.ENGINE_FAILURE
        self.driver_ebrake_applied()
        # self.signals.new_status.emit(str(self.current_status.value))

    def clear_engine_failure(self):
        print("[TRAIN]: Clearing Engine Failure.")
        self.ENGINE_FAILURE = 0
        self.set_current_status(TrainStatus.ENGINE_FAILURE_CLEAR)
        # self.current_status = TrainStatus.ENGINE_FAILURE_CLEAR
        # self.signals.new_status.emit(str(self.current_status.value))


    def receive_signal_pickup_failure(self):
        print("[TRAIN]: NO SIGNAL PICKUP")
        self.SIGNAL_FAILURE = 1
        self.set_current_status(TrainStatus.SIGNAL_PICKUP_FAILURE)
        # self.current_status = TrainStatus.SIGNAL_PICKUP_FAILURE
        # self.signals.new_status.emit(str(self.current_status.value))

    def clear_signal_pickup_failure(self):
        print("[TRAIN]: NO SIGNAL PICKUP")
        self.SIGNAL_FAILURE = 0
        self.set_current_status(TrainStatus.SIGNAL_PICKUP_FAILURE_CLEAR)
        # self.current_status = TrainStatus.SIGNAL_PICKUP_FAILURE_CLEAR
        # self.signals.new_status.emit(str(self.current_status.value))



    ## beacon info: 'L/R/LR', "name", "1/0"
    ##              door side, station, tunnel flag
    def receive_beacon_info(self, beacon_info: list):
        print(f"[TRAIN]: Beacon Info Received.{beacon_info} ")
        # if this is the second beacon
        if self.station_ahead:
            self.station_ahead = False
            self.set_door_side(None)
            self.set_next_station(None)
            self.set_tunnel_flag(None)
            return

        self.station_ahead = True
        self.door_opened = False
        print("[TRAIN]: Beacon Info Received. " + str(beacon_info))
        self.set_door_side(beacon_info[0])
        self.set_next_station(beacon_info[1])
        self.set_tunnel_flag(beacon_info[2])


        i = random.randint(0,1)
        j = random.randint(0,1)
        self.signals.broadcast_announcements.emit(announcements[i])
        self.signals.broadcast_advertisements.emit(advertisements[j])
        self.signals.broadcast_station_name.emit(self.next_station)


    def set_next_station(self, next_station: str):
        if next_station is None:
            return
        next_station_enum = StationList.__call__(next_station)
        if not isinstance(next_station_enum, StationList):
            raise TypeError('Next station must be a value in the StationList enum.')
        else:
            self.next_station = next_station_enum
            print("[TRAIN]: Next station: " + next_station_enum.value)
            self.signals.new_station.emit(self.next_station.value)


    def set_door_side(self, door_open: str):
        if door_open is None:
            return
        door_open_enum = StationSide.__call__(door_open)
        if not isinstance(door_open_enum, StationSide):
            raise TypeError('Door side must be a value in the StationSide enum. ')
        else:
            self.door_open_side = door_open_enum
            print("[TRAIN]: Doors will open on: " + door_open_enum.value)



    def get_door_status(self):
        return self.door_status

    # def toggle_left_door(self):
    #     self.signals.toggle_left_doors.emit()
    #
    # def toggle_right_door(self):
    #     self.signals.toggle_right_doors.emit()
    #
    # def toggle_all_doors(self):
    #     self.signals.toggle_all_doors.emit()

    def driver_open_door(self, side: str):
        if self.current_speed_m_s != 0:
            print("[TRAIN]: Unable to open doors. Train current speed = " + str(self.current_speed_m_s))
            return False

        if side == "Left":
            self.left_door_status = "Open"
            self.signals.open_left_doors.emit()
        if side == "Right":
            self.right_door_status = "Open"
            self.signals.open_right_doors.emit()
        print("[TRAIN]: Driver " + side + " doors open.")
        return True


    def driver_close_door(self, side: str):
        if side == "Left":
            self.left_door_status = "Close"
            self.signals.close_left_doors.emit()
        if side == "Right":
            self.right_door_status = "Close"
            self.signals.close_right_doors.emit()
        print("[TRAIN]: Driver " + side + " doors closed.")

    def open_doors(self):
        if self.door_open_side == StationSide.OPEN_DOORS_LEFT:
            self.signals.open_left_doors.emit()
        elif self.door_open_side == StationSide.OPEN_DOORS_RIGHT:
            self.signals.open_right_doors.emit()
        elif self.door_open_side == StationSide.OPEN_ALL_DOORS:
            self.signals.open_all_doors.emit()

        print("[TRAIN]: Opening doors on " + self.door_open_side.value + " side. ")


    def toggle_interior_lights(self):
        if self.interior_light_status == Lights.OFF:
            self.interior_light_status = Lights.ON
            print("[TRAIN]: Turning Interior Lights ON.")
        else:
            self.interior_light_status = Lights.OFF
            print("[TRAIN]: Turning Interior Lights OFF.")
            self.signals.turn_off_interior_lights.emit()

        self.signals.toggle_interior_lights.emit()

    def set_tunnel_flag(self, tunnel_incoming):
        if tunnel_incoming is None:
            return
        self.tunnel_flag = int(tunnel_incoming)
        if self.tunnel_flag:
            self.toggle_exterior_lights()


    def toggle_exterior_lights(self):
        if self.exterior_light_status == Lights.OFF:
            self.exterior_light_status = Lights.ON
            print("[TRAIN]: Turning Exterior Lights ON.")
        else:
            self.exterior_light_status = Lights.OFF
            print("[TRAIN]: Turning Exterior Lights OFF.")

        self.signals.toggle_exterior_lights.emit()

    def get_exterior_light_status(self):
        if self.exterior_light_status == Lights.OFF:
            return "Off"
        else:
            return "On"

    def get_interior_light_status(self):
        if self.interior_light_status == Lights.OFF:
            return "Off"
        else:
            return "On"

    def increase_temp(self):
        self.temperature += 1
        print("[TRAIN]: Temperature increase by 1 degree. Current temp " + str(self.temperature))
        self.signals.new_temp.emit(self.temperature)

    def decrease_temp(self):
        self.temperature -= 1
        print("[TRAIN]: Temperature decrease by 1 degree. Current temp " + str(self.temperature))
        self.signals.new_temp.emit(self.temperature)

    def set_current_status(self, status: TrainStatus):
        self.current_status = status
        self.signals.new_status.emit(str(self.current_status.value))

    def get_current_status(self):
        # self.signals.change_current_status
        return self.current_status.value

    # TODO: broadcast to eric and train model slows down, no regulation needed
    def passenger_ebrake_applied(self):
        print("[TRAIN]: Passenger Ebrake Applied")
        # Train model slows down, controller gets notified that ebrake was pulled.
        self.set_current_status(TrainStatus.PASSENGER_EBRAKE)
        # return self.current_status

    def clear_passenger_ebrake(self):
        print("[TRAIN]: Passenger EBrake removed. ")
        self.set_current_status(TrainStatus.RUNNING)
        # return self.current_status

    def driver_ebrake_applied(self):
        print("[TRAIN]: Driver Ebrake Applied")
        self.set_current_status(TrainStatus.DRIVER_EBRAKE)
        self.resume_authority = self.authority
        # self.resume_speed_m_s = self.commanded_speed_m_s
        self.resume_speed_m_s = self.CTC_commanded_speed_m_s

        self.set_authority_blocks(0)
        self.set_commanded_speed_m_s(0)
        self.set_commanded_speed_CTC_m_s(0)

        self.EBRAKE_ENABLED = True


        # return self.current_status

    def clear_driver_ebrake(self):
        if self.ENGINE_FAILURE or self.BRAKE_FAILURE or self.SIGNAL_FAILURE:
            print("[TRAIN]: Unable to clear ebrake, failures not cleared.")
            return False
        if self.current_speed_m_s != 0:
            print("[TRAIN]: Unable to clear ebrake. Current speed = " + str(self.current_speed_m_s))
            return False
        ## TODO: resume speed/authority not working

        self.EBRAKE_ENABLED = 0
        print("[TRAIN]: Driver ebrake released. Commanded speed = " + str(self.resume_speed_m_s) + " m/s and authority = " + str(self.resume_authority))
        self.set_commanded_speed_CTC_m_s(self.resume_speed_m_s)
        self.set_authority_blocks(self.resume_authority)
        self.resume_speed_m_s = 0
        self.resume_authority = 0
        return True

    def release_ebrake(self, speed):
        self.set_commanded_speed_m_s(speed)
        print("[TRAIN]: EBrake released. Resuming normal operation. Will accelerate to " +
              str(self.get_commanded_speed_mph()) + " mph.")
        self.set_current_status(TrainStatus.RUNNING)
        # self.current_status = TrainStatus.RUNNING


    def output_power(self, actual_speed : float) -> float:
        ## TODO: add vital calculation from train model?

        # TODO: add error checking, check failure states, make sure that gains are set        
        self.current_speed_m_s = actual_speed
        if self.mode == Modes.AUTO:
            self.v_error = self.CTC_commanded_speed_m_s - self.current_speed_m_s
        else:
            self.v_error = self.commanded_speed_m_s - self.current_speed_m_s

        # determine flags
        if self.went_over_commanded is False and self.v_error < -0.2:
            self.went_over_commanded = True
            self.went_under_commanded = False
            print("[TRAIN]: went over set to true")
            self.prev_uk = 0
        elif self.went_under_commanded is False and self.v_error >= 0.2:
            print("[TRAIN]: went under set to true")
            self.went_under_commanded = True
            self.went_over_commanded = False
            self.prev_uk = 0

        if self.power_command_w < TrainController.MAX_POWER_W:
            self.uk = (self.prev_uk) + ((self.dt / 2.0) * (self.v_error+ self.prev_v_error))
        else:
            self.uk = self.prev_uk

        self.power_command_w = (self.Kp*self.v_error) + (self.Ki*self.uk)

        if(self.power_command_w > TrainController.MAX_POWER_W):
           self.power_command_w = TrainController.MAX_POWER_W


        #store previous values
        self.prev_v_error = self.v_error
        self.prev_uk = self.uk

        # if not self.PID_lock_flag:
            # self.power_command_w = 0
            # print("[TRAIN]: PID Gains not set, no power output.")
        if not self.PID_lock_flag:
            if self.power_command_w > 0:
                self.power_command_w = 0
            

        if self.ENGINE_FAILURE or self.SIGNAL_FAILURE or self.BRAKE_FAILURE:
            self.power_command_w = 0
        
        if self.authority == 0:
            self.CTC_commanded_speed_m_s = 0
            self.commanded_speed_m_s = 0
            

        if self.EBRAKE_ENABLED and self.current_speed_m_s <1:
            self.EBRAKE_ENABLED = False

        if self.current_speed_m_s == 0 and self.station_ahead and not self.door_opened:
            self.open_doors()
            self.door_opened = True

        self.position_m += self.current_speed_m_s*0.1
        # print(self.position_m)

        # print(f"[TRAIN]: {self.commanded_speed_m_s}, {self.CTC_commanded_speed_m_s}, {self.Ki}, {self.Kp}")


        self.signals.new_power.emit(str(round(self.power_command_w, 3)))

        return self.power_command_w



    # Track Model Inputs
    def get_train_position(self):
        return self.position_m

    def enter_new_block(self):
        self.position_m = 0

    def __del__(self):
        print("[TRAIN]: Actual Train Controller object deleted.")
