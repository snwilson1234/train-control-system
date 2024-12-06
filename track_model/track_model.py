import sys, sqlite3, csv
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from train.train_model.ui.main_app import Main_App
from track_model.train import TrainTM
from enum import Enum
from time import sleep
from timeit import default_timer as timer
from PySide6.QtCore import QRunnable, Slot, QObject, Slot, Signal

from train.train_model.inc.run_control import monitor_loop

class ColorEnum(Enum):
    BLUE = 'Blue'
    RED = 'Red'
    GREEN = 'Green'
    NONE = ''

class BreakEnum(Enum):
    RAIL = -2
    POWER = -4
    CIRCUIT = -8

class TrackModelSignals(QObject):
    update_block_status = Signal(dict)
    update_bool_block_status = Signal(dict)
    update_trains = Signal(list)
    import_track = Signal(ColorEnum)
    update_tickets = Signal(dict)
    update_passengers = Signal(list)
    update_switches = Signal()
    update_lights = Signal()
    update_crossings = Signal()
    update_beacon = Signal(list)
    new_train = Signal()
    update_tc = Signal()

class TrackModel(QRunnable):

    track_imported = False
    track_heater = False
    block_status = {}
    bool_block_status = {}
    trains = {}
    light_status = {}
    root_switch_status = {}
    root_switch_list = {}
    all_switch_status = {}
    all_switch_list = {}
    station_blocks = {}
    beacon_blocks = {}
    yard_blocks = {}
    crossing_blocks = {}
    lines = []
    train_count = 0
    tickets = {}
    controllers = {}
    train_factory = None
    tc_switches = {}
    tc_blocks = {}
    block_lengths = {}
    switch_directions = {}

    DB_NAME = "./track_model/track.db"
    db_len = 0
    con = sqlite3.connect(DB_NAME, check_same_thread=False)
    cur = con.cursor()


    def __init__(self, app):
        super(TrackModel, self).__init__()
        self.signals = TrackModelSignals()
        self.train_factory = app
        self.speed_up_factor = 1.0
        self.is_paused = False
        self.train_list = list()
        assert isinstance(self.train_factory, Main_App)

        self.onboard_once = True

    def __del__(self):
        #pass
        self.delete_track()


    # delete all imported track and empty db
    def delete_track(self) -> None:
        self.cur.execute("DROP TABLE IF EXISTS track")
        self.con.commit()


    # import track line
    def import_track(self, file : str, line : ColorEnum) -> bool:

        self.cur.execute("""CREATE TABLE IF NOT EXISTS track(Id INTEGER PRIMARY KEY, Line STRING,
                     Section CHAR, Number INTEGER, Length FLOAT, Grade FLOAT, Speed INTEGER,
                     Infrastructure STRING, Switch BOOL, Positions STRING, Station BOOL, Side CHAR,
                         Name STRING, Tunnel BOOL, Crossing BOOL, Yard INTEGER, Direction INTEGER,
                         Controllers INTEGER, Relative INTEGER, Pass INTEGER);""")

        self.lines = self.get_line_list()

        if(not line.value in self.lines):
            try:
                with open(file,'r') as fin:
                    dr = csv.DictReader(fin)
                    to_db = [(i['Line'], i['Section'], i['Number'], i['Length'], i['Grade'], i['Speed'], i['Infrastructure'], i['Switch'], i['Positions'], i['Station'], i['Side'], i['Name'], i['Tunnel'], i['Crossing'], i['Yard'], i['Direction'], i['Controllers'], i['Relative'], i['Pass']) for i in dr]

                self.cur.executemany("""INSERT INTO track (Line, Section, Number, Length, Grade,
                                        Speed, Infrastructure, Switch, Positions, Station, Side,
                                    Name, Tunnel, Crossing, Yard, Direction, Controllers, Relative,
                                    Pass) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", to_db)
            except:
                    return False

        self.track_imported = True
        self.signals.import_track.emit(line)

        self.init_block_status(line)
        self.init_root_switch_status(line)
        self.init_all_switch_status(line)
        self.init_light_status(line)
        self.init_station_blocks(line)
        self.init_beacon_blocks(line)
        #self.init_yard_blocks(line)
        self.init_crossing_blocks(line)
        self.init_controllers(line)
        self.init_block_lengths(line)
        self.init_switch_directions(line)
        self.trains[line.value] = []
        self.tickets[line.value] = 0

        self.con.commit()
        self.lines = self.get_line_list()
        #self.sw_dir = {1: -1, 2: 1, 13: -1, 28: 1, 29: -1, 57: 1, 58: -1, 62: 1, 63: -1, 76: 1, 77: -1, 85: 1, 86: -1, 100: 1, 101: -1, 150: 1}

        sw = {}
        for switch in self.root_switch_list[line.value]:
            sw[switch] = self.get_switch_positions(line, switch)
        self.tc_switches[line.value] = sw

        blk = {}
        for i, stat in enumerate(self.block_status[line.value]):
            if i > 0:
                blk[i] = self.get_relative_block(line, i)
        self.tc_blocks[line.value] = blk

        self.yard_blocks[line.value] = [0]

        #print(self.root_switch_status[line.value])
        #print(self.all_switch_status[line.value])

        return True


    # get all lines
    # example : ['Blue']
    def get_line_list(self) -> list:
        result = self.cur.execute("SELECT DISTINCT Line FROM track;").fetchall()
        return [tup[0] for tup in result]


    # get all block section letters for a given line
    # example : ['A', 'B', 'C']
    def get_section_list(self, line: ColorEnum) -> list:
        result = self.cur.execute("SELECT DISTINCT Section FROM track WHERE Line = '" + line.value + "';").fetchall()
        return [tup[0] for tup in result]


    # get all block numbers for a given line and section
    def get_number_list(self, line: ColorEnum, section: str) -> list:
        result = self.cur.execute("SELECT DISTINCT Number FROM track WHERE Line = '" + line.value + "' AND Section = '" + section + "';").fetchall()
        return [str(tup[0]) for tup in result]


    # get all switch blocks for a given line
    # example : blue line switch list [(5, '6, 11'), (6, '5, -1'), (11, '-1, 5')], returns [5, 6, 11]
    def get_all_switch_list(self, line: ColorEnum) -> list:
        result = self.cur.execute("SELECT Number, Positions FROM track WHERE Line = '" + line.value + "' AND Switch = 1;").fetchall()
        return [int(tup[0]) for tup in result]


    # get all root switch blocks for a given line
    # example : blue line switch list [(5, '6, 11'), (6, '5, -1'), (11, '-1, 5')], returns [5]
    def get_root_switch_list(self, line: ColorEnum) -> list:
        result = self.cur.execute("SELECT Number, Positions FROM track WHERE Line = '" + line.value + "' AND Switch = 1;").fetchall()
        return [int(tup[0]) for tup in result if '-1' not in tup[1]]


    # get L/R block numbers for a given line and switch
    # example : [5] returns [6, 11]
    def get_switch_positions(self, line: ColorEnum, switch : int) -> list:
        result = self.cur.execute("SELECT Positions FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(switch) + "';").fetchall()
        try:
            return [int(i) for i in result[0][0].split(',')]
        except:
            return


    # get position of switch
    def get_switch(self, line: ColorEnum, switch : int) -> int:
        for list in self.all_switch_status[line.value]:
            if list[0] == switch:
                return list[1]


    # get color of light
    def get_light(self, line: ColorEnum, light : int) -> int:
        for list in self.light_status[line.value]:
            if list[0] == light:
                return list[1]


    # toggle position of switch
    def toggle_switch(self, line: ColorEnum, switch : int) -> int:
        pos = self.get_switch_positions(line, switch)
        for list in self.all_switch_status[line.value]:
            if list[0] == switch:
                pos.remove(list[1])
                list[1] = pos[0]
        for list in self.root_switch_status[line.value]:
            if list[0] == switch:
                list[1] = pos[0]


    # break thing at given line and block
    def break_thing(self, line : ColorEnum, block : int, failure : BreakEnum) -> None:
        self.block_status[line.value][block] = failure.value
        self.bool_block_status[line.value][block] = 1


    # fix thing at given line and block
    def fix_thing(self, line : ColorEnum, block : int, failure : BreakEnum) -> None:
        if self.block_status[line.value][block] == failure.value:
            self.block_status[line.value][block] = 0
            self.bool_block_status[line.value][block] = 0


    # set track heater on if off or off if on
    def toggle_track_heater(self) -> None:
        self.track_heater = not self.track_heater

    # set track heater
    def set_track_heater(self, state : bool) -> None:
        self.track_heater = state


    # initialize block occupancy: set all blocks 0, first block name of line
    # example : {'Blue': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    def init_block_status(self, line : ColorEnum):
        result = self.cur.execute("SELECT Id FROM track WHERE ROWID IN ( SELECT max( Id ) FROM track);").fetchone()[0]
        self.block_status[line.value] = [''] + [0] * (result - self.db_len)
        self.bool_block_status[line.value] = [''] + [0] * (result - self.db_len)
        self.db_len = result


    # initialize block lengths
    # example : {'Blue': [50, 50, 50, 60, 50, 60, 60, 60, 50, 50, 50, 50, 50, 50, 50]}
    def init_block_lengths(self, line : ColorEnum):
        result = self.cur.execute("SELECT Length FROM track WHERE Line = '" + line.value + "';").fetchall()
        self.block_lengths[line.value] = [''] + [tup[0] for tup in result]


    # initialize root switch status: all switches set L
    # example : {'Blue': [[5, 6]]}
    def init_root_switch_status(self, line : ColorEnum):
        switches = self.get_root_switch_list(line)
        self.root_switch_list[line.value] = switches
        self.root_switch_status[line.value] = [[switch, self.get_switch_positions(line, switch)[0]] for switch in switches]


    # initialize all switch status: all switches set L
    # example : {'Blue': [[5, 6], [6, 5], [11, -1]]}
    def init_all_switch_status(self, line : ColorEnum):
        switches = self.get_all_switch_list(line)
        self.all_switch_list[line.value] = switches
        self.all_switch_status[line.value] = [[switch, self.get_switch_positions(line, switch)[0]] for switch in switches]


    # initialize light status, R or G
    # example : {'Blue': [[5, 'G'], [6, 'G'], [11, 'R']]}
    def init_light_status(self, line : ColorEnum):
        lights = self.get_all_switch_list(line)
        status = []
        for light in lights:
            color = 'G'
            if self.get_switch_positions(line, light)[0] == -1:
                color = 'R'
            status.append([light, color])
        self.light_status[line.value] = status


    # initialize track controller list
    # example : {'Red': [7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 7, 7, ..] }
    def init_controllers(self, line : ColorEnum):
        result = self.cur.execute("SELECT Controllers FROM track WHERE Line = '" + line.value + "';").fetchall()
        self.controllers[line.value] = [tup[0] for tup in result]


    # intialize switch passing directions
    # example : [[1, -1], [12, 1], [13, -1], [28, 1]... ]}
    def init_switch_directions(self, line: ColorEnum) -> list:
        result = self.cur.execute("SELECT Number, Pass FROM track WHERE Line = '" + line.value + "' AND Switch = 1;").fetchall()
        self.switch_directions[line.value] = [[tup[0], tup[1]] for tup in result]
        print(self.switch_directions)


    # get switch passing value
    # example : [63: -1]
    def get_switch_passing_direction(self, line: ColorEnum, switch: int) -> int:
        for list in self.switch_directions[line.value]:
            if list[0] == switch:
                return list[1]


    # get length of block for a given line and block number
    def get_block_length(self, line: ColorEnum, block : int) -> float:
        result = self.cur.execute("SELECT Length FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(block) + "';").fetchone()[0]
        return result


    # get grade of block for a given line and block number
    def get_block_grade(self, line: ColorEnum, block : int) -> float:
        result = self.cur.execute("SELECT Grade FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(block) + "';").fetchone()[0]
        return result


    # get speed limit of block for a given line and block number
    def get_block_speed(self, line: ColorEnum, block : int) -> int:
        result = self.cur.execute("SELECT Speed FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(block) + "';").fetchone()[0]
        return result


    # get relative block number for a given line and block number
    def get_relative_block(self, line: ColorEnum, block : int) -> int:
        result = self.cur.execute("SELECT Relative FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(block) + "';").fetchone()[0]
        return result


    # get list of stations for a given line
    # example : ['Station B', 'Station C']
    def get_stations(self, line: ColorEnum) -> list:
        result = self.cur.execute("SELECT Name FROM track WHERE Line = '" + line.value + "' AND Station = 1;").fetchall()
        return [('Station ' + str(tup[0])) for tup in result]


    # get direction of track
    # 1 : ascending in block number, 2: descending in block number, 3 : bidirectional
    def get_direction(self, line: ColorEnum, block : int) -> int:
        result = self.cur.execute("SELECT Direction FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(block) + "';").fetchone()[0]
        return result


    # initialize list of blocks containing stations for a given line
    # example : {'Blue': [10, 15]}
    def init_station_blocks(self, line: ColorEnum) -> None:
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Station = 1;").fetchall()
        self.station_blocks[line.value] = [int(tup[0]) for tup in result]


    # get list of blocks containing beacons for a given line (before and after stations)
    # example : {'Blue': [9, 11, 14, 16]}
    def init_beacon_blocks(self, line: ColorEnum) -> None:
        beacons = []
        for block in self.station_blocks[line.value]:
            beacons.append(block - 1)
            beacons.append(block + 1)
        self.beacon_blocks[line.value] = beacons


    # get beacon data for station on a given line and station block
    # if after param is true, station side will flip- assumes train movement is descending in block number
    # examples : ['LR', 'B', 0] or ['LR', 'C', 0] or ['', '', '']
    def get_beacon_data(self, line: ColorEnum, block : int, after : bool) -> list:
        if block + 1 in self.station_blocks[line.value]:
            beacon = block + 1
        elif block - 1 in self.station_blocks[line.value]:
            beacon = block - 1
        else:
            return ['', '', '']

        side = self.cur.execute("SELECT Side FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(beacon) + "';").fetchone()[0]
        name = self.cur.execute("SELECT Name FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(beacon) + "';").fetchone()[0]
        tunnel = self.cur.execute("SELECT Tunnel FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(beacon) + "';").fetchone()[0]
        if side == 'R' and after:
            side == 'L'
        if side == 'L' and after:
            side == 'R'
        return [side, name, tunnel]


    # get list of blocks of the yard of a given line
    # example: {'Blue': [0, 11, 16]}
    def init_yard_blocks(self, line: ColorEnum) -> None:
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Yard != 0;").fetchall()
        nums = []
        for res in result:
            nums.append(int(self.cur.execute("SELECT Yard FROM track WHERE Line = '" + line.value + "' AND Number = '" + str(res[0]) + "';").fetchone()[0]) + int(res[0]))
        self.yard_blocks[line.value] = nums


    # get list of blocks containing stations for a given line
    # example: {'Blue': []}
    def init_crossing_blocks(self, line: ColorEnum) -> None:
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Crossing = 1;").fetchall()
        cross = [int(tup[0]) for tup in result]
        status = []
        for num in cross:
            status.append([num, 0])
        self.crossing_blocks[line.value] = status


    # create new train on specified line and block, with given speed and authority
    # actual train object (train) and track model train (traintm)
    @Slot()
    def new_train_ctc(self, line : str, block : int, speed : int, auth_dest : int) -> None:
        line_enum = ColorEnum.__call__(line)
        if(not self.block_status[line_enum.value][block]):
            assert isinstance(self.train_factory, Main_App)
            id = self.train_count
            self.train_factory.add_tab()
            train = self.train_factory.qthread_manager.peek_model(id)

            tm = TrainTM(auth_dest, auth_dest, id, block)
            if auth_dest < block:
                tm.direction = -1

            auth_diff = self.convert_authority(tm, line_enum, auth_dest, id, block)
            print(f"[TRACK MODEL]: New Train: {speed}, {auth_diff}, {auth_dest}")
            train.set_track_circuit_data(speed, auth_diff)
            tm.authority_diff = auth_diff
            self.train_count += 1

            self.train_list.append(tm)
            # print(f"UPDATING TRAIN LIST, NEW LIST: {self.train_list}")

            self.trains[line_enum.value] = self.train_list
            self.block_status[line_enum.value][block] = 1
            self.bool_block_status[line_enum.value][block] = 1
            #print(self.root_switch_status[line.value])
            #print(self.all_switch_status[line.value])

            self.signals.new_train.emit()
            self.update_speed_up_factor_new_train(self.speed_up_factor, id)


    # calculate difference authority from destination authority
    # if switch, issue authority only until switch
    def convert_authority(self, tm : TrainTM, line : ColorEnum, auth_dest : int, id : int, block : int) -> int:
        assert isinstance(self.train_factory, Main_App)
        train = self.train_factory.qthread_manager.peek_model(id)

        if tm.block_i == -1:
            return 0

        return abs(auth_dest - block)


    # convert relative block number and track controller id to absolute block
    # track controller all functions
    def rel_block_to_abs(self, line: str, block :int, id : int) -> int:
        if id == 0:
            return
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line + "' AND Controllers = '" + str(id) + "' AND Relative = '" + str(block) + "';").fetchone()[0]
        return result


    # convert relative block number and track controller id to absolute block
    # track controller all functions
    def rel_block_to_abs_tc(self, line: str, block :int, id : int) -> int:
        id = int(id)
        for i,blk in enumerate(self.block_status[line]):
            if i > 0:
                if self.tc_blocks[line][i] == block and self.controllers[line][i-1] == id:
                    return i


    # random number of tickets
    def set_tickets(self, line: ColorEnum, tix : int) -> None:
        self.tickets[line.value] += tix


    # set speed authority
    # set to block, check for train on block and convert authority
    # list [rel_block, speed, authority]
    def set_speed_authority(self, line_int : int, info: list, tc_id : str) -> None:
        print("[TRACK MODEL]: Speed & Authority " + str(info) + " Controller: " + tc_id)

        if line_int == 0:
            line = ColorEnum.RED.value
        elif line_int == 1:
            line = ColorEnum.GREEN.value
        else:
            line = ColorEnum.BLUE.value

        if not (line in self.lines):
            return

        abs_block = info[0].value
        speed = info[1].value
        auth_dest = info[2].value

        assert isinstance(self.train_factory, Main_App)

        # print(f"IN SET SPEED AUTH IN TRACK MODEL: PRINT {self.trains[line]}")
        for tm in self.trains[line]:
            assert isinstance(tm, TrainTM)
            train = self.train_factory.qthread_manager.peek_model(tm.id)
            # print(f"[TRACK MODEL]: TRAIN IS {train}")
            if tm.block_i == abs_block:
                # print("HEY THERE YOU ARE ROCK STAR")
                tm.authority_dest = auth_dest
                print("[TRACK MODEL]: Block " + str(tm.block_i) + " Controller: " + tc_id)
                auth_diff = self.convert_authority(tm, line, auth_dest, tm.id, abs_block)
                train.set_track_circuit_data(speed, auth_diff)

    # set switch
    # from track controller, block is absolute and switch is 0 for L or 1 for R
    def set_switch(self, line_int : int, rel_block : int, switch : bool, tc_id : str) -> None:
        #if(tc_id == '5'):
        #    print('[TRACK CONTROLLER]: Set Switch: ' + str(line_int) + " " +  str(rel_block) + " " + str(switch) + " " + tc_id)

        if line_int == 0:
            line = ColorEnum.RED
        elif line_int == 1:
            line = ColorEnum.GREEN
        else:
            line = ColorEnum.BLUE

        if not (line.value in self.lines):
            return

        abs_block = self.rel_block_to_abs_tc(line.value, rel_block, tc_id)
        if abs_block is None:
            return
        pos = self.tc_switches[line.value][abs_block]
        self.set_switch_tm(line, abs_block, pos[switch])



    # set light
    # from track controller, block is absolute and light is 0 for R or 1 for G   [R, L, R]
    def set_light(self, line_int : int, rel_block : int, states : list, tc_id : str) -> None:
        #print('[TRACK CONTROLLER]: Set Light: ' + str(line_int) + " " +  str(rel_block) + " " + str(states) + " " + tc_id)

        if line_int == 0:
            line = ColorEnum.RED
        elif line_int == 1:
            line = ColorEnum.GREEN
        else:
            line = ColorEnum.BLUE

        if not (line.value in self.lines):
            return

        abs_block = self.rel_block_to_abs_tc(line.value, rel_block, tc_id)
        if abs_block is None:
            return
        pos = self.tc_switches[line.value][abs_block]

        blks = [abs_block, pos[0], pos[1]]

        for i, update_light in enumerate(blks):
            if states[i].value == 1:
                color = 'G'
            else:
                color = 'R'

            for light in self.light_status[line.value]:
                if light[0] == blks[i]:
                    light[1] = color


    # set railway
    # from track controller, block is absolute and railway is 0 for inactive or 1 for active
    def set_railway(self, line_int : int, rail : bool, tc_id : str) -> None:

        if line_int == 0:
            line = ColorEnum.RED
        elif line_int == 1:
            line = ColorEnum.GREEN
        else:
            line = ColorEnum.BLUE

        if not (line.value in self.lines):
            return
        self.crossing_blocks[line.value][0][1] = rail


    # get all distinct controller ids
    # example : [1, 2, 3, 4, 5, 6]
    def controller_ids(self, line : ColorEnum):
        result = self.cur.execute("SELECT DISTINCT Controllers FROM track WHERE Line = '" + line.value + "';").fetchall()
        return [int(tup[0]) for tup in result]


    # get block list for a controller
    # example : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    def controller_blocks(self, line : ColorEnum, id : int) -> list:
        status = []
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Controllers = '" + str(id) + "';").fetchall()
        blocks = [int(tup[0]) for tup in result]

        for num in blocks:
            status.append(self.bool_block_status[line.value][num])
        return status


    # get switch list for a controller
    # example : [1] or [0] or [0 , 0] or [0, 1] or [1 , 0] or [1, 1]
    def controller_switches(self, line : ColorEnum, id : int) -> int:
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Controllers = '" + str(id) + "' AND Switch = 1;").fetchall()
        blocks = [int(tup[0]) for tup in result]

        for num in blocks:
            pos = self.get_switch_positions(line, num)
            if num in self.get_root_switch_list(line):
                if self.get_switch(line, num) == pos[1]:
                    return 1
                else:
                    return 0


    # get light list for a controller
    # example : [1, 1, 0]
    def controller_lights(self, line : ColorEnum, id : int) -> list:
        lights = []
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Controllers = '" + str(id) + "' AND Switch = 1;").fetchall()
        blocks = [int(tup[0]) for tup in result]

        for num in blocks:
            if self.get_light(line, num) == 'G':
                lights.append(1)
            else:
                lights.append(0)
        return lights


    # get railway list for a controller
    # [] [0] or [1]
    def controller_railway(self, line : ColorEnum, id : int) -> list:
        result = self.cur.execute("SELECT Number FROM track WHERE Line = '" + line.value + "' AND Controllers = '" + str(id) + "' AND Crossing = 1;").fetchall()
        blocks = [int(tup[0]) for tup in result]

        for num in blocks:
            for list in self.crossing_blocks[line.value]:
                if list[0] == num:
                    return list[1]


    # set switch
    def set_switch_tm(self, line : ColorEnum, block : int, switch : int) -> None:
        pos = self.tc_switches[line.value][block]
        #print("[TRACK MODEL]: switch: " + str(switch))
        #print("[TRACK MODEL]: pos: " + str(pos))

        for list in self.root_switch_status[line.value]:
            if list[0] == block:
                list[1] = switch
            if list[0] == switch:
                if list[1] == -1:
                    if pos[0] != 0 :
                        self.toggle_switch(line, pos[0])
                    if pos[1] != 0 :
                        self.toggle_switch(line, pos[1])
        for list in self.all_switch_status[line.value]:
            if list[0] == block:
                list[1] = switch
            if list[0] == switch:
                if list[1] == -1:
                    if pos[0] != 0 :
                        self.toggle_switch(line, pos[0])
                    if pos[1] != 0 :
                        self.toggle_switch(line, pos[1])


    # set light
    def set_light_tm(self, line : ColorEnum, block : int, color : str) -> None:
        for list in self.light_status[line.value]:
            if list[0] == block:
                list[1] = color





    # update position of all trains from delta time
    def update(self, line : str, dt_s : float):
        assert isinstance(self.train_factory, Main_App)

        for tm in self.trains[line]:
            line_enum = ColorEnum.__call__(line)
            assert isinstance(tm, TrainTM)
            train_mod = self.train_factory.qthread_manager.peek_model(tm.id)
            train_contr = self.train_factory.qthread_manager.peek_controller(tm.id)

            # get train info
            pos = tm.block_i
            dist = tm.distance_m # this is train model, how far you are into the block
            dm = train_contr.get_train_position() - dist
            new_pos = pos
            stop = False
            passengers = None
            print()
            print("[TRACK MODEL]: Current distance: " + str(dist))
            print("[TRACK MODEL]: Meters traveled: " + str(dm))
            print("[TRACK MODEL]: Block: " + str(pos))

            # if train is not on track
            if(pos == -1 or pos == 0):
                tm.block_i = -1
                continue

            #update grade and block length
            blklen = self.block_lengths[line_enum.value][pos]
            blkdir = self.get_direction(line_enum, pos)
            train_mod.set_block_length(blklen)
            train_mod.set_grade(self.get_block_grade(line_enum, pos))

            # update authority, send failures
            if(self.block_status[line][pos] == BreakEnum.POWER):
                train_mod.handle_track_power_failure(True)
            else:
                train_mod.handle_track_power_failure(False)
                #print("[TRACK MODEL]: Train Authority: " + str(tm.authority_dest))
                #print("[TRACK MODEL]: Convert Authority: " + line_enum.value + " " + str(tm.authority_dest) + " " + str(tm.id) + " " + str(tm.block_i))
                new_auth = self.convert_authority(tm, line_enum, tm.authority_dest, tm.id, tm.block_i)
                speed = train_contr.CTC_commanded_speed_m_s
                train_mod.set_track_circuit_data(speed, new_auth)
                if (new_auth == 0 and not train_mod.get_brake_failure() and not train_mod.get_signal_pickup_failure()):
                    stop = True


            # update position
            # if authority is zero
            if(stop):
                tm.distance_m = blklen/2
                dist = blklen/2
                dm = 0
                tm.block_i = tm.authority_dest


            # if train enters station
            if(pos in self.station_blocks[line] and train_contr.current_speed_m_s == 0 and self.onboard_once):
                tix = random.randint(0, 30)
                self.set_tickets(line_enum, tix)
                self.signals.update_tickets.emit(self.tickets)
                passengers = random.randint(0, tix)
                train_mod.onboard_passengers(passengers)
                self.signals.update_passengers.emit([passengers, train_mod.removed_passengers, train_mod.passenger_count])
                self.onboard_once = False

            # if train has entered new block
            if(dm + dist >= blklen):
                self.block_status[line][pos] = 0
                self.bool_block_status[line][pos] = 0
                tm.distance_m = dm + dist - blklen
                train_mod.entered_new_block()

                if(blkdir == 3):
                    new_pos = pos + 1*tm.direction
                elif(blkdir == 2):
                    tm.direction = -1
                    new_pos = pos - 1
                elif(blkdir == 1):
                    tm.direction = 1
                    new_pos = pos + 1


                # if train enters beacon block
                if(new_pos in self.beacon_blocks[line]):
                    after = (tm.direction == -1)
                    beacon = self.get_beacon_data(line_enum, new_pos, after)
                    print(beacon)
                    print(str(beacon[0]) + "." + str(beacon[1]) + "." + str(beacon[2]))
                    train_mod.set_beacon_data(str(beacon[0]) + "." + str(beacon[1]) + "." + str(beacon[2]))
                    self.onboard_once = True
                    self.signals.update_beacon.emit(beacon)


                # if train enters switch
                if(pos in self.all_switch_list[line]):
                    if(tm.direction == self.get_switch_passing_direction(line_enum, pos)):
                        print("[TRACK MODEL]: Before Switch: " + str(pos))
                        new_pos = self.get_switch(ColorEnum.__call__(line), pos)
                        print("[TRACK MODEL]: After Switch: " + str(new_pos))
                        tm.direction = -1*self.get_switch_passing_direction(line_enum, new_pos)
                        print("[TRACK MODEL]: Train Direction: " + str(tm.direction))

                # if train is in yard
                if(new_pos in self.yard_blocks[line] or new_pos == 0):
                    print("[TRACK MODEL]: Train has entered Yard")
                    tm.block_i = -1
                    pos = -1
                    continue

                # if next block is occupied
                if(new_pos == -1 or self.block_status[line][new_pos] == 1):
                    print("[TRACK MODEL]: NEXT BLOCK IS OCCUPIED OR DOES NOT EXIST")
                    return

                tm.block_i = new_pos
                self.block_status[line][new_pos] = 1
                self.bool_block_status[line][new_pos] = 1

            # if train has not entered new block
            else:
                tm.distance_m = dm + dist


    def update_speed_up_factor(self, val : float) -> None:

        if "Green" in self.lines:
            for train in self.trains["Green"]:
                train_ref = self.train_factory.qthread_manager.peek_idx(train.id)
                train_ref.speed_up = val

        if "Red" in self.lines:
            for train in self.trains["Red"]:
                train_ref = self.train_factory.qthread_manager.peek_idx(train.id)
                train_ref.speed_up = val

        self.speed_up_factor = val


    def update_speed_up_factor_new_train(self, val : float, id) -> None:

        print(f"[TRACK MODEL]: UPDATING NEW TRAIN WITH THE SPEED {val}")
        train_ref = self.train_factory.qthread_manager.peek_idx(id)
        train_ref.speed_up = val

        self.speed_up_factor = val

    def update_pause_resume(self, state : bool):
        print(f"[TRACK MODEL]: Received pause/resume, val: {state}")
        self.is_paused = state

        if "Green" in self.lines:
            for train in self.trains["Green"]:
                train_ref = self.train_factory.qthread_manager.peek_idx(train.id)
                train_ref.is_paused = state

        if "Red" in self.lines:
            for train in self.trains["Red"]:
                train_ref = self.train_factory.qthread_manager.peek_idx(train.id)
                train_ref.is_paused = state

    # run track model
    @Slot()
    def run(self):
        self.update_freq = 10
        self.update_time_limit = 1/ self.update_freq

        while True:
            sleep(1)
            while self.is_paused:
                pass

            for line in self.lines:
                line_enum = ColorEnum.__call__(line)
                assert isinstance(line_enum, ColorEnum)
                self.update(line, 1)

                self.signals.update_tc.emit()
                self.signals.update_block_status.emit(self.block_status)
                self.signals.update_bool_block_status.emit(self.bool_block_status)
                self.signals.update_trains.emit(self.trains)
                self.signals.update_lights.emit()
                self.signals.update_switches.emit()
                self.signals.update_crossings.emit()

            monitor_loop()


