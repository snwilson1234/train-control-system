from track_controller.wayside_controller_backend import *
from track_controller.ctc_office_sim import *
from track_controller.track import *


def main ():
    ctc = CTCOffice()
    #tc1 = track_control_sys.controller_list[0]
    #tc1.set_main_program("./plc_programs/blue_line/tc1b.txt")
    #tc1.set_var_file("./plc_programs/blue_line/var_files/tc1b_vars.txt")
    #print(tc1.run_program())


if __name__ == "__main__":
    main()