import sys, os
import time

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


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("media/epic_logo.png"))

    ctc_mw = CTC_MainWindow()

    # Create the ctc_runner and connect its progress_update signal to the slot in the main ctc_mw
    ctc_runner = CTC_BackEndRunner()
    ctc_runner.office.signals.block_status_list_update.connect(ctc_mw.w.update_data_from_backend)
    ctc_runner.ctc_runner_signals.time_update.connect(ctc_mw.w.update_time_from_backend)

    ctc_mw.w.main_tab.maintenance.update_maintenance_close_button.connect(ctc_runner.office.update_maintenance_close)
    ctc_mw.w.main_tab.maintenance.update_maintenance_open_button.connect(ctc_runner.office.update_maintenance_open)
    ctc_mw.w.main_tab.create_trains.dispatch_train_manual.connect(ctc_runner.office.manual_dispatch)

    ctc_mw.w.update_signal.connect(ctc_runner.office.catch_signal)

    ctc_mw.test_interface.send_green_bsl_to_office.connect(ctc_runner.office.update_block_status)

    ctc_runner.office.signals.output_to_ui.connect(ctc_mw.w.update_stdout)


    # Submit the ctc_runner to the thread pool
    QThreadPool.globalInstance().start(ctc_runner)

    ctc_mw.show()
    app.exec()


if __name__ == "__main__":
    main()
