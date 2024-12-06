from track_controller.interpreter import *
from track_controller.track import TrackModel
#from ctc_office_sim import *
from PySide6.QtCore import Signal, QThread, QObject, QRunnable, Slot
import time
import re
from train.train_model.inc.run_control import monitor_loop

class ProgramSignals(QObject):

    #All starting at index
    #main return value signal
    return_val_sig = Signal(list)

    #specific return values


    speed_auth_loc_sig = Signal(int,list,str)
    sw_sig = Signal(int,int,int,str)
    sw_sig2 = Signal(int,int,int,str)
    lights_sig = Signal(int,int,list,str)
    crossing_sig = Signal(int,int,str)
    pending_run_call = Signal()

class Program(QRunnable):
    def __init__(self, wayside_controller):
        super().__init__()
        self.wayside_controller = wayside_controller
        self.signals = ProgramSignals()
        self.running = True

    @Slot()
    def run(self):
            
        if self.running:
            self.running = False
            # print(f"[TRACK CONTROLLER]: starting program:{self.wayside_controller}")
            # while not self.wayside_controller.stop_flag:

            result = self.wayside_controller.run_program()
            self.signals.return_val_sig.emit(result)
            #print(result[9])

            #emit new speed auth loc
            self.signals.speed_auth_loc_sig.emit(self.wayside_controller.line, result[10].elements, self.wayside_controller.id)

            #emit new switch
            self.signals.sw_sig.emit(self.wayside_controller.line, result[14].value, result[11].value, self.wayside_controller.id)

            #emit new switch (track controllers w 2 switches)
            if self.wayside_controller.id in ["9","10"]:
                self.signals.sw_sig2.emit(self.wayside_controller.line, result[4].value, result[5].value, self.wayside_controller.id)

            #emit new lights
            self.signals.lights_sig.emit(self.wayside_controller.line, result[14].value, result[12].elements, self.wayside_controller.id)

            #emit railway crossing status
            self.signals.crossing_sig.emit(self.wayside_controller.line, result[13].value, self.wayside_controller.id)
            if self.wayside_controller.id == "5": print(f"TRACK CONTROLLER {self.wayside_controller.id} BSL: {result[15]}")
            #print(f"WAYSIDE {self.wayside_controller.id} OUTPUT: {result}")
            self.running = True

            #print(f"TRACK CONTROLLER {self.wayside_controller.id} OUTPUT: {result}")


class TrackController():

    def __init__(self, id):
        self.id = id
        self.interpreter = Interpreter()

        self.line = None

        #main program, function defs
        self.main_file = None
        self.main_body = None

        #var file
        self.var_file = None
        self.var_body = None
        self.var_list = None

        self.stop_flag = False
        self.fun_out = None
        self.program = None

    def handle_return_val(self, result):
        if result:
            #print(result)
            self.fun_out = result
            return result
        else:
            self.fun_out = "no result"
            return "no result"

    def create_program(self):
        self.stop_flag = False
        if not self.program:
            self.program = Program(self)
            self.program.signals.return_val_sig.connect(self.handle_return_val)
            self.program.signals.pending_run_call.connect(self.program.run)

    def delete_program(self):
        if self.program:
            self.stop_flag = True
            self.program = None

    def set_main_program(self, fn):
        self.main_file = fn
        try:
            with open(fn, "r") as f:
                self.main_body = ''.join(f.readlines())
            f.close()
        except:
            print(f"unable to write main program for wayside {self.id}:")

    def set_var_file(self, fn):
        self.var_file = fn
        try:
            with open(fn, "r") as f:
                self.var_body = ''.join(f.readlines())
            f.close()
            self.var_list = [x for x in self.var_body.split("\n")]
        except:
            print(f"unable to write var file for wayside {self.id}:")

    def run_program(self):
        result, error = compile_run(self.main_file, self.main_body)
        if error:
            print(error.as_string())
            return error.as_string()
        else:
            output = result.elements if result else "null"
            return output


    ##########################################
    #### INPUTS FROM CTC
    ##########################################

    @Slot(int, int, int)#option for setting tc sigs
    def set_block_speed_auth(self, loc, speed, auth):
        #print("[TRACK CONTROLLER]: ##################################################")
        #print(f"[TRACK CONTROLLER]: wayside controller #: {self.id}")
        #print(f"[TRACK CONTROLLER]: received from ctc, loc: {loc}, speed, {speed}, auth: {auth}")
        #print("[TRACK CONTROLLER]: ##################################################")

        if self.var_body:
            self.var_list = [x for x in self.var_body.split("\n")]
        else:
            return "no var file found"
        #find variable to update
        for i in range(len(self.var_list)):
            if f"VAR ctc_request_loc_{self.id}" in self.var_list[i]:
                self.var_list[i] = f"VAR ctc_request_loc_{self.id} = {loc}" #update it
            elif f"VAR ctc_speed_{self.id}" in self.var_list[i]:
                self.var_list[i] = f"VAR ctc_speed_{self.id} = {speed}"
            elif f"VAR ctc_auth_{self.id}" in self.var_list[i]:
                self.var_list[i] = f"VAR ctc_auth_{self.id} = {auth}"

        #rewrite the file
        try:
            new_var_body = "\n".join(self.var_list)
            with open(self.var_file, "w") as f:
                f.writelines(new_var_body)

            self.var_body = new_var_body
            self.program.signals.pending_run_call.emit()
            
        except:
            print(f"unable to write new speed, auth for wayside {self.id}")

        

## left 0, right 1
## click this for every switch - only green line
    def request_switch(self, sw: bool):
        if self.var_body:
            self.var_list = [x for x in self.var_body.split("\n")]
        else:
            return "no var file found"

        #find variable to update
        for i in range(len(self.var_list)):
            if f"VAR ctc_swpos_{self.id}" in self.var_list[i]:
                self.var_list[i] = f"VAR ctc_swpos_{self.id} = {sw}" #update it


        #rewrite the file
        try:
            new_var_body = "\n".join(self.var_list)
            with open(self.var_file, "w") as f:
                f.writelines(new_var_body)

            self.var_body = new_var_body
        except:
            print(f"unable to write ctc switch for wayside {self.id}")

    ##########################################
    #### INPUTS FROM TRACK MODEL
    ##########################################

    #TM sends controller-specific BSL
    def set_block(self, mini_bsl):#tm sends tc-specific bsl
        if self.var_body:
            self.var_list = [x for x in self.var_body.split("\n")]
        else:
            return "no var file found"

        #find variable to update
        for i in range(len(self.var_list)):
            if f"VAR block_status_list_{self.id}" in self.var_list[i]:
                self.var_list[i] = f"VAR block_status_list_{self.id} = {mini_bsl}" #update it

        #rewrite the file
        try:
            new_var_body = "\n".join(self.var_list)
            with open(self.var_file, "w") as f:
                f.writelines(new_var_body)

            self.var_body = new_var_body
        except:
            print(f"unable to write new bsl for wayside {self.id}")

    #TM sends controller-specific lights
    def set_lights(self, light_arr):
        if self.var_body:
            self.var_list = [x for x in self.var_body.split("\n")]
        else:
            return "no var file found"

        pattern = r'VAR sw_\d+_lights'
        #find variable to update
        for i in range(len(self.var_list)):
            if re.search(pattern, self.var_list[i]):
                curr = self.var_list[i]
                curr = curr[:19]
                self.var_list[i] = curr + f"{light_arr}"

        #rewrite the file
        try:
            new_var_body = "\n".join(self.var_list)
            with open(self.var_file, "w") as f:
                f.writelines(new_var_body)
            self.var_body = new_var_body
        except:
            print(f"unable to write new lights for wayside {self.id}")

    #TM sends switch for single switch waysides
    def set_switch(self, val: bool):
        if self.var_body:
            self.var_list = [x for x in self.var_body.split("\n")]
        else:
            return "no var file found"

        pattern = r'VAR sw_\d+ '
        #find variable to update
        for i in range(len(self.var_list)):
            if re.search(pattern, self.var_list[i]):
                curr = self.var_list[i]
                curr = curr[:12]
                self.var_list[i] = curr + f"{val}"

        #rewrite the file
        try:
            new_var_body = "\n".join(self.var_list)
            with open(self.var_file, "w") as f:
                f.writelines(new_var_body)
            self.var_body = new_var_body
        except:
            print(f"unable to write new switch for wayside {self.id}")

    #TM sends switch for double switch waysides
    #def set_switch(self, vals: List[bool]):
    #    pass

    #TM sends crossing status
    def set_crossing(self, state):
        if self.var_body:
            self.var_list = [x for x in self.var_body.split("\n")]
        else:
            return "no var file found"

        if self.id == "1":
            #find variable to update
            for i in range(len(self.var_list)):
                if f"VAR crossing_1" in self.var_list[i]:
                    self.var_list[i] = f"VAR crossing_1 = {state}" #update it
        elif self.id == "10":
            for i in range(len(self.var_list)):
                if f"VAR crossing_10" in self.var_list[i]:
                    self.var_list[i] = f"VAR crossing_10 = {state}" #update it

        #rewrite the file
        try:
            new_var_body = "\n".join(self.var_list)
            with open(self.var_file, "w") as f:
                f.writelines(new_var_body)

            self.var_body = new_var_body
        except:
            print(f"unable to write new crossing for wayside {self.id}")



class TrackControllerSystem():
    def __init__(self, line):
        self.line = line
        self.controller_list = self.make_controllers(line)
        self.program_list = []
        # self.thread_pool = QThreadPool()
        # self.thread_pool.setMaxThreadCount(6)

    def make_controllers(self, line) -> list:
        controller_list = []

        if line == "GREEN_LINE":
            self.num_controllers = 6
            for i in range(self.num_controllers):
                controller = TrackController(f"{i+1}")
                controller.set_var_file(f"./plc_programs/green_line/var_files/tc{i+1}_vars.txt")
                controller.set_main_program(f"./plc_programs/green_line/tc{i+1}.txt")
                controller_list.append(controller)
                controller.line = 1

        elif line == "RED_LINE":
            self.num_controllers = 5
            for i in range(self.num_controllers):
                controller = TrackController(f"{i+7}")
                controller.set_var_file(f"./plc_programs/red_line/var_files/tc{i+7}_vars.txt")
                controller.set_main_program(f"./plc_programs/red_line/tc{i+7}.txt")
                controller_list.append(controller)
                controller.line = 0

        return controller_list

    def create_waysides(self):
        # for i in reversed(range(len(self.controller_list)-1)):
        #    self.controller_list[i].create_program()
        if self.line == "GREEN_LINE": self.controller_list[5].create_program()
        self.controller_list[4].create_program()
        self.controller_list[3].create_program()
        self.controller_list[2].create_program()
        self.controller_list[1].create_program()
        self.controller_list[0].create_program()

    def run_waysides_one_step(self):
        # for i in reversed(range(len(self.controller_list)-1)):
        #    self.controller_list[i].program.run()
        if self.line == "GREEN_LINE": self.controller_list[5].program.run()
        self.controller_list[4].program.run()
        self.controller_list[3].program.run()
        self.controller_list[2].program.run()
        self.controller_list[1].program.run()
        self.controller_list[0].program.run()

    def stop_waysides(self):
        # for i in reversed(range(len(self.controller_list)-1)):
        #    self.controller_list[i].delete_program()
        if self.line == "GREEN_LINE": self.controller_list[5].delete_program()
        self.controller_list[4].delete_program()
        self.controller_list[3].delete_program()
        self.controller_list[2].delete_program()
        self.controller_list[1].delete_program()
        self.controller_list[0].delete_program()