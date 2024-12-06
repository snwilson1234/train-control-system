from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from ctc_office.ctc_office_ui import *
from ctc_office.ctc_office import CTC_Office
from ctc_office.ctc_train import CTC_Train
import sys
import time

from datetime import datetime, date
from testfixtures import Replace, mock_datetime
from testfixtures.tests.sample1 import str_now_1

import time
import traceback, sys
from PySide6.QtWidgets import *
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from train.train_model.inc.run_control import monitor_loop


# ----------------------------------------------------------
class CTC_RunngerSignals(QObject):
    time_update = Signal(str)

# ----------------------------------------------------------
class CTC_BackEndRunner(QRunnable):
    def __init__(self, signal_holder = CTC_RunngerSignals()):
        super().__init__()
        self.ctc_runner_signals = CTC_RunngerSignals()
        self.office = CTC_Office()
        self.speed_up_factor :float = 1.0
        self.is_paused = False
        print("making")

    def set_is_paused(self, state : bool) -> None:
        self.is_paused = state

    def new_speed_up_factor(self, val : float):
        self.speed_up_factor = val

    def run(self):
        threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % threadpool.maxThreadCount())

        block_indices = [x for x in range(1,16)]

        with Replace('testfixtures.tests.sample1.datetime',
            mock_datetime(2023, 6, 29, 8, 0, 0, delta = 1, delta_type='seconds')):

            #################################################################
            # BACKEND LOOP THAT KEEPS TIME AND UPDATES EVERYTHING
            while True:
                current_time = str_now_1()[11:]

                self.ctc_runner_signals.time_update.emit(current_time)

                while self.is_paused:
                    pass
                

                # self.office.update_trains()
                #################################################################
                
                time.sleep(1 / self.speed_up_factor)
                monitor_loop()
