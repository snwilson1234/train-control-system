import sys
import os
import time
import keyboard
import pyqtgraph
import sqlite3
import csv
import timeit

sys.path.append(".")

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from datetime import datetime, date
from testfixtures import Replace, mock_datetime
from testfixtures.tests.sample1 import str_now_1
from track_controller.wayside_controller_ui import *
from track_controller.wayside_controller_backend import *

from ctc_office.ctc_office_ui import *
from ctc_office.ctc_office_ui import CTC_Office_UI
from ctc_office.ctc_office import CTC_Office
from ctc_office.ctc_train import CTC_Train
from ctc_office.ctc_worker import *

from track_model.train import *
from track_model.track_model import *
from track_model.track_model_ui import *
from track_model.testbench_ui import *


imported_tracks = []

def main():
    global red_line_system
    red_line_system = TrackControllerSystem("RED_LINE")
    global green_line_system
    green_line_system = TrackControllerSystem("GREEN_LINE")
    #green_line_system.run_waysides()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("media/epic_logo.png"))

    ctc_mw = CTC_MainWindow()
    track_controller_ui = TrackControllerUI(green_line_system, red_line_system)
    track_controller_test_bench = TrackControllerTestBench(green_line_system,red_line_system)
    #track_controller_ui.green_line_system = green_line_system
    track_controller_ui.controller_view.run_selected_system()

    ctc_mw.w.main_tab.general_info.sigs.pause_resume_update.connect(track_controller_ui.controller_view.handle_system_pause)


    ma = Main_App()
    global tmw
    tmw = TrackModelMainWindow(ma)
    #tmw.tm.import_track("./track_model/track_green.csv", ColorEnum.GREEN)
    #tmw.import_cmbx0_line = 'Green'
    #tmw.on_import_clicked()
    ctc_mw.w.main_tab.general_info.sigs.speed_up_factor_update.connect(tmw.tm.update_speed_up_factor)
    ctc_mw.w.main_tab.general_info.sigs.pause_resume_update.connect(tmw.tm.update_pause_resume)

    # Create the ctc_runner and connect its progress_update signal to the slot in the main ctc_mw
    ctc_runner = CTC_BackEndRunner()
    ctc_runner.office.signals.block_status_list_update.connect(ctc_mw.w.update_data_from_backend)
    ctc_runner.ctc_runner_signals.time_update.connect(ctc_mw.w.update_time_from_backend)
    ctc_runner.ctc_runner_signals.time_update.connect(ctc_mw.w.main_tab.general_info.time_le.setText)
    ctc_mw.w.main_tab.general_info.sigs.speed_up_factor_update.connect(ctc_runner.new_speed_up_factor)
    ctc_mw.w.main_tab.general_info.sigs.pause_resume_update.connect(ctc_runner.set_is_paused)


    ctc_mw.w.main_tab.maintenance.update_maintenance_close_button.connect(ctc_runner.office.update_maintenance_close)
    ctc_mw.w.main_tab.maintenance.update_maintenance_open_button.connect(ctc_runner.office.update_maintenance_open)

    ctc_mw.w.update_signal.connect(ctc_runner.office.catch_signal)
    ctc_mw.w.main_tab.create_trains.dispatch_train_manual.connect(ctc_runner.office.manual_dispatch)


    ## Connect speed and authority to Track Controllers.
    ctc_runner.office.signals.send_speed_authority1.connect(green_line_system.controller_list[0].set_block_speed_auth)
    ctc_runner.office.signals.send_speed_authority2.connect(green_line_system.controller_list[1].set_block_speed_auth)
    ctc_runner.office.signals.send_speed_authority3.connect(green_line_system.controller_list[2].set_block_speed_auth)
    ctc_runner.office.signals.send_speed_authority4.connect(green_line_system.controller_list[3].set_block_speed_auth)
    ctc_runner.office.signals.send_speed_authority5.connect(green_line_system.controller_list[4].set_block_speed_auth)
    ctc_runner.office.signals.send_speed_authority6.connect(green_line_system.controller_list[5].set_block_speed_auth)


    ## Send switch positions to track controllers.
    ## Green
    ctc_runner.office.signals.set_green_switch1.connect(green_line_system.controller_list[0].request_switch)
    ctc_runner.office.signals.set_green_switch2.connect(green_line_system.controller_list[1].request_switch)
    ctc_runner.office.signals.set_green_switch3.connect(green_line_system.controller_list[2].request_switch)
    ctc_runner.office.signals.set_green_switch4.connect(green_line_system.controller_list[3].request_switch)
    ctc_runner.office.signals.set_green_switch5.connect(green_line_system.controller_list[4].request_switch)
    ctc_runner.office.signals.set_green_switch6.connect(green_line_system.controller_list[5].request_switch)
    ## Red
    ctc_runner.office.signals.set_red_switch1.connect(red_line_system.controller_list[0].request_switch)
    ctc_runner.office.signals.set_red_switch2.connect(red_line_system.controller_list[1].request_switch)
    ctc_runner.office.signals.set_red_switch3.connect(red_line_system.controller_list[2].request_switch)
    ctc_runner.office.signals.set_red_switch4.connect(red_line_system.controller_list[3].request_switch)
    ctc_runner.office.signals.set_red_switch5.connect(red_line_system.controller_list[4].request_switch)


    ctc_runner.office.signals.create_train.connect(tmw.tb.on_new_train_clicked)
    ctc_mw.test_interface.send_green_bsl_to_office.connect(ctc_runner.office.update_block_status)


    ctc_runner.office.signals.spawn_train.connect(tmw.tm.new_train_ctc)

    ## Receive block status from track controller, send to CTC office.
    tmw.tm.signals.update_bool_block_status.connect(ctc_runner.office.update_block_status)
    tmw.tm.signals.update_bool_block_status.connect(track_controller_updates)
    tmw.tm.signals.import_track.connect(import_track)
    ctc_runner.office.signals.output_to_ui.connect(ctc_mw.w.update_stdout)


    ## Tickets
    # tmw.tm.signals.update_tickets.connect(ctc_mw.w.update_ticket_sales_from_track)
    #tmw.tm.signals.update_bool_block_status.connect(ctc_runner.office.update_block_status)


    #ctc_runner.ctc_runner_signals.time_update.connect(tm_to_tc_update)

    #ctc_runner.ctc_runner_signals.time_update.connect(tm_to_tc_update(tmw))


    ctc_mw.w.main_tab.maintenance.update_maintenance_close_button.connect(ctc_runner.office.update_maintenance_close)
    ctc_mw.w.update_signal.connect(ctc_runner.office.catch_signal)
    # tmw.tm.signals.update_tickets.connect(ctc_mw.w.update_ticket_sales_from_track)

    # Submit the ctc_runner to the thread pool
    QThreadPool.globalInstance().start(ctc_runner)

    # green_line_system.controller_list[0].program.signals.sw_sig.connect(ctc_runner.office.update_switches)#INPUT CTC SLOT
    # green_line_system.controller_list[1].program.signals.sw_sig.connect(ctc_runner.office.update_switches)#INPUT CTC SLOT
    # green_line_system.controller_list[2].program.signals.sw_sig.connect(ctc_runner.office.update_switches)#INPUT CTC SLOT
    green_line_system.controller_list[3].program.signals.sw_sig.connect(ctc_runner.office.update_switches)#INPUT CTC SLOT
    # green_line_system.controller_list[4].program.signals.sw_sig.connect(ctc_runner.office.update_switches)#INPUT CTC SLOT
    # green_line_system.controller_list[5].program.signals.sw_sig.connect(ctc_runner.office.update_switches)#INPUT CTC SLOT

    # #green_line_system.controller_list[0].program.speed_auth_loc_sig

    if True:
        green_line_system.controller_list[0].program.signals.speed_auth_loc_sig.connect(tmw.tm.set_speed_authority)
        green_line_system.controller_list[0].program.signals.sw_sig.connect(tmw.tm.set_switch)
        green_line_system.controller_list[0].program.signals.lights_sig.connect(tmw.tm.set_light)
        green_line_system.controller_list[0].program.signals.crossing_sig.connect(tmw.tm.set_railway)

        green_line_system.controller_list[1].program.signals.speed_auth_loc_sig.connect(tmw.tm.set_speed_authority)
        green_line_system.controller_list[1].program.signals.sw_sig.connect(tmw.tm.set_switch)
        green_line_system.controller_list[1].program.signals.lights_sig.connect(tmw.tm.set_light)
        green_line_system.controller_list[1].program.signals.crossing_sig.connect(tmw.tm.set_railway)

        green_line_system.controller_list[2].program.signals.speed_auth_loc_sig.connect(tmw.tm.set_speed_authority)
        green_line_system.controller_list[2].program.signals.sw_sig.connect(tmw.tm.set_switch)
        green_line_system.controller_list[2].program.signals.lights_sig.connect(tmw.tm.set_light)
        green_line_system.controller_list[2].program.signals.crossing_sig.connect(tmw.tm.set_railway)

        green_line_system.controller_list[3].program.signals.speed_auth_loc_sig.connect(tmw.tm.set_speed_authority)
        green_line_system.controller_list[3].program.signals.sw_sig.connect(tmw.tm.set_switch)
        green_line_system.controller_list[3].program.signals.lights_sig.connect(tmw.tm.set_light)
        green_line_system.controller_list[3].program.signals.crossing_sig.connect(tmw.tm.set_railway)

        green_line_system.controller_list[4].program.signals.speed_auth_loc_sig.connect(tmw.tm.set_speed_authority)
        green_line_system.controller_list[4].program.signals.sw_sig.connect(tmw.tm.set_switch)
        green_line_system.controller_list[4].program.signals.lights_sig.connect(tmw.tm.set_light)
        green_line_system.controller_list[4].program.signals.crossing_sig.connect(tmw.tm.set_railway)

        green_line_system.controller_list[5].program.signals.speed_auth_loc_sig.connect(tmw.tm.set_speed_authority)
        green_line_system.controller_list[5].program.signals.sw_sig.connect(tmw.tm.set_switch)
        green_line_system.controller_list[5].program.signals.lights_sig.connect(tmw.tm.set_light)
        green_line_system.controller_list[5].program.signals.crossing_sig.connect(tmw.tm.set_railway)


    ctc_mw.show()
    track_controller_ui.show()
    track_controller_test_bench.show()
    tmw.show()

    app.exec()


def track_controller_updates():
    for line in imported_tracks:
        #print(tmw.tm.controller_ids(line))
        for id in tmw.tm.controller_ids(line):
            if(line == ColorEnum.GREEN):
                green_line_system.controller_list[id-1].set_block(tmw.tm.controller_blocks(line, id))
                green_line_system.controller_list[id-1].set_switch(tmw.tm.controller_switches(line, id))
                green_line_system.controller_list[id-1].set_lights(tmw.tm.controller_lights(line, id))
                green_line_system.controller_list[id-1].set_crossing(tmw.tm.controller_railway(line, id))
            if(line == ColorEnum.RED):
                pass
                # red_line_system.controller_list[id-1].set_block(tmw.tm.controller_blocks(line, id))
                # red_line_system.controller_list[id-1].set_switch(tmw.tm.controller_switches(line, id))
                # red_line_system.controller_list[id-1].set_lights(tmw.tm.controller_lights(line, id))
                # red_line_system.controller_list[id-1].set_crossing(tmw.tm.controller_railway(line, id))


@Slot(ColorEnum)
def import_track(value):
    assert isinstance(value, ColorEnum)
    imported_tracks.append(value)




if __name__ == "__main__":
    main()
