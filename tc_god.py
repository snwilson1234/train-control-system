import sys, os
import time
import subprocess, atexit

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import sys
import time

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
#from qt_material import apply_stylesheet


def main():
    green_line_system = TrackControllerSystem("GREEN_LINE")
    red_line_system = TrackControllerSystem("RED_LINE")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("media/epic_logo.png"))

    tc_ui = TrackControllerUI(green_line_system, red_line_system)
    tc_test_bench = TrackControllerTestBench(green_line_system, red_line_system)

    tc_ui.show()
    tc_test_bench.show()

    app.exec()

def run_cleanup():
    subprocess.run(["python","cleanup.py"])

if __name__ == "__main__":
    atexit.register(run_cleanup)
    main()