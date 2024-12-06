from train.train_model.inc.run_control import kill

#TODO: research if there is any actual way to prevent reassignment of fields after init

class Beacon:

    DELIM = "."
    MAX_LENGTH = 128

    def __init__(self, station_side : str, station_name : str, tunnel_light_toggle : bool):
        self.station_side= station_side
        self.station_name = station_name
        self.tunnel_light_toggle  = tunnel_light_toggle
        self.beacon_data = ""
        
        self.char_length = 0

        self.set_stream()
        self.determine_length()

    def set_stream(self):
        self.beacon_data = self.station_side + \
                            Beacon.DELIM + \
                            self.station_name + \
                            Beacon.DELIM
        
        if self.tunnel_light_toggle:
            self.beacon_data += "True"
        else:
            self.beacon_data += "False"
        
        print(f"[TRAIN]: Beacon Data String: {self.beacon_data}")
            
    def determine_length(self):
        self.char_length = len(self.beacon_data)
        if(self.char_length > Beacon.MAX_LENGTH):
            print("[TRAIN]: [ERROR]: BEACON OVER CHAR LIMIT")
            kill()

    def get_data_string(self) -> str:
        return self.beacon_data

                                   