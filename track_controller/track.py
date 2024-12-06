from track_controller.error import *
from PySide6.QtCore import Signal

##OBJECTS ON THE TRACK

class Block:
    def __init__(self, idx, occupancy):
        self.idx = idx
        self.occupancy = occupancy #boolean -> 1: occupied, 0: not occupied
    
    def __repr__(self):
        return f"b{self.idx}: '{self.occupancy}'"

class Switch:
    def __init__(self, block_idx, position):
        self.block_idx = block_idx
        self.position = position

    def toggle(self):
        if self.position == True:
            self.position = False
        else:
            self.position = True
    
    def __repr__(self):
        return f"sw{self.block_idx}: '{self.position}'"

class RailwayCrossing:
    def __init__(self, block_idx, on_off):
        self.block_idx = block_idx
        self.on_off = on_off #1 = closed, train can go; 0 = open, train cannot go

    def toggle(self):
        if self.position == True:
            self.position = False
        else:
            self.position = True

    def __repr__(self):
        return f"Railway Crossing {self.block_idx}: '{self.on_off}'"

class TrafficLight:
    def __init__(self, block_idx, color):
        self.block_idx = block_idx
        self.color = color
    
    def toggle(self):
        if self.color == True:
            self.color = False
        else:
            self.color = True

    def __repr__(self):
        return f"Traffic Light {self.block_idx}: '{self.color}'"


##TRACK CIRCUIT ITSELF

class TrackModel:
    
    sent_occupancies = Signal(list)

    def __init__(self, line):
        self.block_status_list = self.make_track(line)
        #self.sw_list = self.make_switches()

    def make_track(self, line):
        new_track = []
        if line == "Blue":
            new_track = [False] * 16
            new_track[0] = "Blue"
        elif line == "Red":
            new_track = [False] * 76
            new_track[0] = "Red"
        elif line == "Green":
            new_track = [False] * 150
            new_track[0] = "Green"
    
    def send_occupancies(self):
        self.sent_occupancies.emit([0,0,0])


'''
class TrackModel:
    def __init__(self, num_blocks):
        self.num_blocks = num_blocks
        self.block_status_list = self.make_track(num_blocks+1)
        self.sw_list = self.make_switches()

    def make_track(self, num_blocks) -> list:
        new_track = []
        switch_list = []
        new_track.append("BLUE_LINE")
        for i in range(1,num_blocks):
            new_track.append(Block(i,False))
        
        switch_list.append(Switch(5,False))

        return new_track
    
    def make_switches(self):
        return [Switch(5,0)]

    def reset_track(self):
        for i in range(1,len(self.track)):
            self.track[i].set_occupancy(False)
        
    def send_single_occupancy(self, idx):
        if idx > len(self.track) or idx < 0:
            return Error("Invalid block number","out of bounds").as_string()
        return f"{self.track[idx]}"
    
    def send_multiple_occupancies(self, idx_arr):
        res_arr = []
        for idx in idx_arr:
            #if idx > self.num_blocks or idx < 0:
            #    return Error("Invalid block number","out of bounds").as_string()
            block = self.track[idx]
            print(block)
            res_arr.append(block)

        return f"{res_arr}"
    
    def send_switch_position(self):
        pass

    def send_railway_crossing_status(self):
        pass

    def send_light_color(self):
        pass
'''