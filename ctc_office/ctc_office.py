from typing import List

from ctc_office.ctc_office_resources import BLUE_LINE_NUMBER_OF_BLOCKS, Line
from ctc_office.ctc_train import CTC_Train
from ctc_office.ctc_office_resources import *

from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import *

from ctc_office.ctc_office_resources import *

class CTC_Signals(QObject):
    # pars = block number, speed, authority
    send_speed_authority1 = Signal(int, int, int)
    send_speed_authority2 = Signal(int, int, int)
    send_speed_authority3 = Signal(int, int, int)
    send_speed_authority4 = Signal(int, int, int)
    send_speed_authority5 = Signal(int, int, int)
    send_speed_authority6 = Signal(int, int, int)


    ## Broadcast suggested switches to Track Controllers.
    set_green_switch1 = Signal(int)
    set_green_switch2 = Signal(int)
    set_green_switch3 = Signal(int)
    set_green_switch4 = Signal(int)
    set_green_switch5 = Signal(int)
    set_green_switch6 = Signal(int)

    set_red_switch1 = Signal(int)
    set_red_switch2 = Signal(int)
    set_red_switch3 = Signal(int)
    set_red_switch4 = Signal(int)
    set_red_switch5 = Signal(int)

    spawn_train = Signal(str, int, int, int)


    block_status_list_update = Signal(Line, list, list)
    create_train = Signal()

    output_to_ui = Signal(str)



class CTC_Office():
    def __init__(self):
        self.green_train_list: list[CTC_Train] = []
        self.red_train_list: list[CTC_Train] = []

        # initializing the block status list with size number of blocks+1. Index 0
        # won't be used and each index corresponds to its real block number
        self.blue_block_status: list[int] = [0] * (BLUE_LINE_NUMBER_OF_BLOCKS+1)
        self.green_block_status: list[int] = [0] * (GREEN_LINE_NUMBER_OF_BLOCKS+1)
        self.red_block_status: list[int] = [0] * (RED_LINE_NUMBER_OF_BLOCKS+1)

        self.blue_maintenance_status: list[int] = [0] * (BLUE_LINE_NUMBER_OF_BLOCKS+1)
        self.green_maintenance_status: list[int] = [0] * (GREEN_LINE_NUMBER_OF_BLOCKS+1)
        self.red_maintenance_status: list[int] = [0] * (RED_LINE_NUMBER_OF_BLOCKS+1)

        self.green_line_switches: list[int] = [0] * (7)

        self.signals = CTC_Signals()

        self.temp_speed = -1
        self.temp_authority = -1
        self.train_index = 0


    def dispatch_train(self, train: CTC_Train) -> bool:
        dispatch_block_occupied = self.green_block_status[60]

        if dispatch_block_occupied:
            return False

        self.train_list.append(train)
        print("[CTC] [CTC_OFFICE]: DISPATCHING TRAIN {len(self.train_list)}")

        self.signals.set_green_switch4.emit(1)
        self.signals.create_train.emit()
        self.signals.send_speed_authority4.emit(63,11,73)


        return True


    ## If a switch needs to be updated, set the current switch state.
    ## This will broadcast a signal as the switch position is changed.
    def set_switch_position(self, line: Line, id: int, status: bool):
        if line == Line.GREEN:
            if id == 1:
                self.signals.set_green_switch1.emit(status)
            if id == 2:
                self.signals.set_green_switch2.emit(status)
            if id == 3:
                self.signals.set_green_switch3.emit(status)
            if id == 4:
                self.signals.set_green_switch4.emit(status)
            if id == 5:
                self.signals.set_green_switch5.emit(status)
            if id == 6:
                self.signals.set_green_switch6.emit(status)

        if line == Line.RED:
            if id == 7:
                self.signals.set_red_switch1.emit(status)
            if id == 8:
                self.signals.set_red_switch2.emit(status)
            if id == 9:
                self.signals.set_red_switch3.emit(status)
            if id == 10:
                self.signals.set_red_switch4.emit(status)
            if id == 11:
                self.signals.set_red_switch5.emit(status)


    def update_trains(self, block_status_list, line: Line):

        occupied_blocks = []
        for i,ele in enumerate(self.green_block_status):
            if ele == 1:
                occupied_blocks.append(i)



        train_indices = []
        current_train_positions = []
        next_train_positions = []


        for i,ele in enumerate(self.green_train_list):
            train_indices.append(ele.id)
            current_train_positions.append(ele.route_list[0])
            next_train_positions.append(ele.route_list[1])


        print("[CTC] *************************")
        print(f"[CTC] Number of trains: {len(self.green_train_list)}")
        print(f"[CTC] occupied_blocks: {occupied_blocks}")
        print(f"[CTC] train indices: {train_indices}")
        print(f"[CTC] current train positions: {current_train_positions}")
        print(f"[CTC] next train positions: {next_train_positions}")

        text = "*************************"
        self.signals.output_to_ui.emit(text)
        text = f"[CTC] Number of trains: {len(self.green_train_list)} "
        self.signals.output_to_ui.emit(text)
        text = f"[CTC] occupied_blocks: {occupied_blocks} "
        self.signals.output_to_ui.emit(text)
        text = f"[CTC] train indices: {train_indices} "
        self.signals.output_to_ui.emit(text)
        text = f"[CTC] current train positions: {current_train_positions }"
        self.signals.output_to_ui.emit(text)
        text = f"[CTC] next train positions: {next_train_positions} "
        self.signals.output_to_ui.emit(text)



        # trains that haven't moved
        for i,train in enumerate(self.green_train_list):
            for j,block in enumerate(occupied_blocks):


                if train.route_list[0] == block:
                    output_string = f"[CTC] Train {train.id} stayed on {train.route_list[0]}"
                    print(output_string)

                    # no longer need to look for the found block
                    occupied_blocks.pop(j)

                    # print(f"[CTC] route list: {train.route_list}")
                    # print(f"[CTC] speed list: {train.speed_list}")
                    # print(f"[CTC] blocks to check: {occupied_blocks}")

                    if train.authority_list[0] == block:
                        if train.wait_time <= 10:
                            self.send_speed_auth(block, 0, train.authority_list[0])
                            text = f"train {train.id} dwelling on block {block} for {train.wait_time}"
                            self.signals.output_to_ui.emit(text)
                            train.wait_time += 1
                        else:

                            text = f"train {train.authority_list} auth list before= {train.authority_list}"
                            self.signals.output_to_ui.emit(text)

                            train.wait_time += 1
                            train.authority_list.pop(0)

                            text = f"train {train.authority_list} auth list after = {train.authority_list}"
                            self.signals.output_to_ui.emit(text)

                            self.send_speed_auth(block, train.speed_list[0], train.authority_list[0])
                            text = f"train {train.id} moving again to {train.authority_list[0]}"
                            self.signals.output_to_ui.emit(text)
                            train.wait_time = 0
                    else:
                        self.send_speed_auth(block, train.speed_list[0], train.authority_list[0])



         # trains that moved one position
        for i,train in enumerate(self.green_train_list):
            for j,block in enumerate(occupied_blocks):
                # print(f"[CTC] !!!{train.route_list[1]} | {block}!!!")
                if train.route_list[1] == block:
                    output_string = f"[CTC] Train {train.id} moved from {train.route_list[0]} to {train.route_list[1]}"
                    print(output_string)
                    self.signals.output_to_ui.emit(output_string)
                    train.route_list.pop(0)
                    train.speed_list.pop(0)

                    # no longer need to look for the found block
                    occupied_blocks.pop(j)

                    # print(f"[CTC] route list: {train.route_list}")
                    # print(f"[CTC] speed list: {train.speed_list}")
                    print(f"[CTC] blocks to check: {occupied_blocks}")

                    self.send_speed_auth(block, train.speed_list[0], train.authority_list[0])



        # the rest are failures
        for i,block in enumerate(occupied_blocks):
            self.green_maintenance_status[block] = 1
            output_string = f"[CTC] FAILURE ON: {block}"
            print(output_string)
            self.signals.output_to_ui.emit(output_string)


        self.signals.block_status_list_update.emit(Line.GREEN, self.green_block_status, self.green_maintenance_status)

        # TODO: uncomment once red line is implemented, commented rn to improve performance
        self.signals.block_status_list_update.emit(Line.RED, self.red_block_status, self.red_maintenance_status)




    def set_failure_block(self, idx: int, line: Line):
        if line == Line.GREEN:
            self.green_maintenance_status[idx] = 1 ## 1 == failure
        if line == Line.RED:
            self.red_maintenance_status[idx] = 1 ## 1 == failure


    @Slot(Line, str)
    def update_maintenance_close(self, line: Line, section: str):
        print("[CTC] file: ctc_office, function: update_maintenance_close")
        print(f"[CTC] [CTC_OFFICE]: ############ line: {line}, index: {section}")

        if line == "Green":
            vals = GREEN_LINE_SECTION_DICT[section]
            for i in range(vals.start_block,vals.end_block+1,1):
                self.green_maintenance_status[i] = 1
            self.signals.block_status_list_update.emit(Line.GREEN, self.green_block_status, self.green_maintenance_status)
        elif line == "Red":
            print("[CTC] [][][][][][][]")
            vals = RED_LINE_SECTION_DICT[section]
            for i in range(vals.start_block,vals.end_block+1,1):
                self.red_maintenance_status[i] = 1
            self.signals.block_status_list_update.emit(Line.RED, self.red_block_status, self.red_maintenance_status)


    @Slot(Line, str)
    def update_maintenance_open(self, line: Line, section: str):
        print("[CTC] file: ctc_office, function: update_maintenance_open")
        print("[CTC] [CTC_OFFICE]: ############ line: {line}, index: {section}")

        if line == "Green":
            vals = GREEN_LINE_SECTION_DICT[section]
            for i in range(vals.start_block,vals.end_block+1,1):
                self.signals.block_status_list_update.emit(Line.GREEN, self.green_block_status, self.green_maintenance_status)
                self.green_maintenance_status[i] = 0
        elif line == "Red":
            print("[CTC] [][][][][][][]")
            vals = RED_LINE_SECTION_DICT[section]
            for i in range(vals.start_block,vals.end_block+1,1):
                self.red_maintenance_status[i] = 0
            self.signals.block_status_list_update.emit(Line.RED, self.red_block_status, self.red_maintenance_status)


    @Slot()
    def catch_signal(self):
        print("[CTC] signal recieved to send train!")
        self.dispatch_train(CTC_Train(GREEN_LINE_ROUTE_DORMONT,GREEN_LINE_SPEED_DORMONT,GREEN_LINE_AUTHORITY_DORMONT))

    @Slot(dict)
    def update_block_status(self, value):
        assert isinstance(value, dict)

        try:
            self.blue_block_status = value[Line.BLUE.value]
            self.update_trains(value, Line.BLUE)

        except:
            self.blue_block_status = []

        try:
            self.green_block_status = value[Line.GREEN.value]
            self.update_trains(value, Line.GREEN)
            # print(f"[CTC] green bsl: {self.green_block_status}")

        except:
            self.green_block_status = []

        try:
            self.red_block_status = value[Line.RED.value]
            self.update_trains(value, Line.RED)

        except:
            self.red_block_status = []


        # print("[CTC] Blue: " + str(self.blue_block_status))
        # print("[CTC] Green: " + str(self.green_block_status))
        # print("[CTC] Red: " + str(self.red_block_status))

        return

    def send_speed_auth(self, block, speed, auth):
        tc_var = GREEN_LINE_TC_DICT[block]
        tc_num = tc_var.track_controller_number
        # print("[CTC] ########## DELETE THIS")

        if tc_num >= 1 and tc_num <= 6:
            output_string = f"[CTC] emitting to TC: {tc_num}, block: {block}, speed: {speed}, auth: {auth}"
            print(output_string)
            self.signals.output_to_ui.emit(output_string)

        if tc_num == 1:
            self.signals.send_speed_authority1.emit(block, speed, auth)
        if tc_num == 2:
            self.signals.send_speed_authority2.emit(block, speed, auth)
        if tc_num == 3:
            self.signals.send_speed_authority3.emit(block, speed, auth)
        if tc_num == 4:
            self.signals.send_speed_authority4.emit(block, speed, auth)
        if tc_num == 5:
            self.signals.send_speed_authority5.emit(block, speed, auth)
        if tc_num == 6:
            self.signals.send_speed_authority6.emit(block, speed, auth)




    @Slot()
    def update_switches(self, line, loc, config, id):
        self.green_line_switches[int(id)] = config

    @Slot(int, int, int, int)
    def manual_dispatch(self, block, speed, auth, switch):

        print("[CTC] LAUNCHING")
        print(f"[CTC] block: {block}, speed: {speed}, auth: {auth}")

        self.green_train_list.append(CTC_Train(self.train_index,Line.GREEN,auth))

        self.train_index += 1


        self.signals.send_speed_authority4.emit(block, speed, auth)
        self.set_switch_position(Line.GREEN, 4, switch)
        self.signals.spawn_train.emit("Green", block, speed, auth)

