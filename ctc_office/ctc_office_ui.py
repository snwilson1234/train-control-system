from typing import Any, Union
import PySide6.QtCore
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import *
from train.train_model.ui.custom_widgets import Color

from ctc_office.ctc_office_resources import *
from ctc_office.ctc_train import *
import csv
import numpy as np


class Simulation_Time_Signals(QObject):
    speed_up_factor_update = Signal(float)
    pause_resume_update = Signal(float)



class Block_Info(Enum):
    GREEN_YARD_CONNECTION = -2
    RED_YARD_CONNECTION = -3
    RED_LINE = 2
    GREEN_LINE = 0
    MAINTENANCE = -1



# ----------------------------------------------------------
class CTC_MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(CTC_MainWindow, self).__init__(*args, **kwargs)

        # TODO: renable test UI
        self.test_interface = CTC_TestInterace_UI()
        self.test_interface.show()
        self.test_interface.setWindowTitle("CTC Test Interface UI")

        self.resize(1920,1080)
        self.setStyleSheet("background-color: lightblue;")

        self.w = CTC_Office_UI()
        self.setCentralWidget(self.w)
        self.show()
        self.setWindowTitle("CTC Office UI")
        self.threadpool = QThreadPool()

        print("[CTC] Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.showMaximized()



# ----------------------------------------------------------
class CTC_TestInterace_UI(QWidget):
    send_green_bsl_to_office = Signal(dict)


    def __init__(self):
        super().__init__()
        self.resize(1500,520)

        self.setStyleSheet("background-color: lightblue;")

        # creating widgets
        ticket_sales_label = QLabel("Ticket Sales: ")
        ticket_sales_input = QLineEdit()
        green_bsl_label = QLabel("Green Block Status List")
        red_bsl_label = QLabel("Red Block Status List")
        self.green_bsl_table = QTableWidget()
        self.red_bsl_table = QTableWidget()
        green_bsl_send_button = QPushButton("Send Green BSL")
        red_bsl_send_button = QPushButton("Send Red BSL")

        # creating green_bsl
        self.green_bsl_table.setColumnCount(2)
        self.green_bsl_table.setRowCount(151)
        self.green_bsl_table.setHorizontalHeaderLabels(["blockindex","status"])


        item = QTableWidgetItem()
        item2 = QTableWidgetItem()

        item.setText("YARD")
        self.green_bsl_table.setItem(0,0,item)

        item2.setText("-1")
        self.green_bsl_table.setItem(0,1,item2)

        for i in range(1,151,1):
            item = QTableWidgetItem()
            item.setText(str(i))
            self.green_bsl_table.setItem(i,0,item)

            item2 = QTableWidgetItem()
            item2.setText("0")
            self.green_bsl_table.setItem(i,1,item2)

        # creating red_bsl
        self.red_bsl_table.setColumnCount(1)
        self.red_bsl_table.setRowCount(76)
        self.red_bsl_table.setHorizontalHeaderLabels(["status"])

        for i in range(76):
            item = QTableWidgetItem()
            item.setText("0")
            self.red_bsl_table.setItem(i,0,item)

        # connecting buttons
        green_bsl_send_button.clicked.connect(self.update_green_bsl)
        red_bsl_send_button.clicked.connect(self.update_red_bsl)

        # adding widgets to layout
        layout = QGridLayout()
        layout.addWidget(ticket_sales_label,0,0)
        layout.addWidget(ticket_sales_input,0,1)
        layout.addWidget(green_bsl_label,1,0)
        layout.addWidget(red_bsl_label,1,1)
        layout.addWidget(self.green_bsl_table,2,0)
        layout.addWidget(self.red_bsl_table,2,1)
        layout.addWidget(green_bsl_send_button,3,0)
        layout.addWidget(red_bsl_send_button,3,1)

        self.setLayout(layout)

    def update_green_bsl(self):
        data = []
        for i in range(151):
            item = self.green_bsl_table.item(i,1).text()
            data.append(int(item))

        print(f"[CTC] data: {data}")

        output_dict =  { Line.GREEN.value : data }

        self.send_green_bsl_to_office.emit(output_dict)


        pass

    def update_red_bsl(self):
        pass


class DepartureTable(QWidget):
    def __init__(self):
        super().__init__()

        self.header_labels = ["Train Index", "Departure Time"]
        # stop_table
        data = self.read_csv("schedule/departure_table.csv")
        self.create_stop_table_from_csv(data)


    def read_csv(self, file_path):
        data = []
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(row)
        return data


    def create_stop_table_from_csv(self, data):
        rows = len(data)
        columns = len(data[0])

        stop_table = QTableWidget(rows, columns)
        for i, row_data in enumerate(data):
            for j, cell_data in enumerate(row_data):
                table_item = QTableWidgetItem(cell_data)
                stop_table.setItem(i, j, table_item)

        # stop_table.setHorizontalHeaderLabels(self.header_labels)
        stop_table.setHorizontalHeaderLabels(self.header_labels)
        stop_table.verticalHeader().setVisible(False)
        layout = QVBoxLayout()
        layout.addWidget(stop_table)
        self.setLayout(layout)




# -----CTC_Map_Style-----------------------------------------------------
class CTC_Map_Style(QtWidgets.QStyledItemDelegate):
    count = 0
    def paint(self, painter, option, index):

        # DEBUG HERE
        # CTC_Map_Style.count +=1
        # print(CTC_Map_Style.count)

        option.displayAlignment = QtCore.Qt.AlignCenter
        # super().paint(painter, option, index)

        # Get the data from the model
        self.data = index.data(QtCore.Qt.DisplayRole)

        # Get the background color based on the data
        self.color_maintenance = QtGui.QColor(QtCore.Qt.black)
        self.color_yellow = QtGui.QColor(QtCore.Qt.yellow)
        self.color_green_line = QtGui.QColor("#00af4d")
        self.yard_color = QtGui.QColor("#bbbbbd")
        self.color_red_line = QtGui.QColor("#ff0000")
        self.color_dark_red = QtGui.QColor("#9B0303")
        self.color_dark_green = QtGui.QColor("#355C00")

        if self.data == None:
            pass
        elif self.data == "YARD":
            painter.fillRect(option.rect, self.yard_color)
        elif isinstance(self.data, str):
            option.displayAlignment = QtCore.Qt.AlignCenter
            painter.drawText(option.rect, self.data)
        elif self.data == 1: # what this?
            painter.fillRect(option.rect, self.color_yellow)
        elif self.data == Block_Info.GREEN_LINE.value:
            painter.fillRect(option.rect, self.color_green_line)
        elif self.data == Block_Info.MAINTENANCE.value:
            painter.fillRect(option.rect, self.color_maintenance)
        elif self.data == Block_Info.RED_LINE.value:
            painter.fillRect(option.rect, self.color_red_line)
        elif self.data == Block_Info.GREEN_YARD_CONNECTION.value:
            painter.fillRect(option.rect, self.color_dark_green)
        elif self.data == Block_Info.RED_YARD_CONNECTION.value:
            painter.fillRect(option.rect, self.color_dark_red)





# ----------------------------------------------------------
class CTC_TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(CTC_TableModel, self).__init__()
        self._data = data


    def data(self, index, role):
        # print("[CTC] hey")
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def setData(self, index, value, role) -> bool:
        # return super().setData(index, value, role)
        # print("[CTC] called?")
        self.dataChanged.emit(index,index,value)
        return True

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def hi(self):
        print("[CTC] data emitted")


# ----------------------------------------------------------
class StopTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(3)
        self.setRowCount(8)
        self.verticalHeader().setVisible(False)
        self.header_labels = ["Stop", "Dwell", "ETA"]
        self.setHorizontalHeaderLabels(self.header_labels)








# ----------------------------------------------------------
class DepartureTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(2)
        self.setRowCount(5)
        self.header_labels = ["Train Index", "Departure Time"]
        self.setHorizontalHeaderLabels(self.header_labels)

        data = self.read_csv("schedule/departure_table.csv")
        self.create_stop_table_from_csv(data)


    def read_csv(self, file_path):
        data = []
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(row)
        return data


    def create_stop_table_from_csv(self, data):
        rows = len(data)
        columns = len(data[0])

        self.clear()
        self.setColumnCount(2)
        self.setRowCount(5)
        self.setHorizontalHeaderLabels(self.header_labels)

        for i, row_data in enumerate(data):
            for j, cell_data in enumerate(row_data):
                table_item = QTableWidgetItem(cell_data)
                self.setItem(i, j, table_item)

# ----------------------------------------------------------
class ActiveTrainsTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(4)
        self.setRowCount(8)
        self.header_labels = ["Train Index", "Current Block", "Suggested Speed", "Authority"]
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(self.header_labels)




# ----------------------------------------------------------
class GeneralInfo(QWidget):
    def __init__(self):
        super().__init__()

        # UI elements
        self.time_le = QLineEdit()
        self.time_le.setReadOnly(True)
        self.time_le.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pause_resume_btn = QPushButton("Pause/Resume")
        self.pause_resume_btn.setCheckable(True)
        self.pause_resume_btn.setFixedWidth(150)

        self.speed_up_factor_le = QLineEdit()
        self.speed_up_factor_le.setFixedWidth(150)
        self.speed_up_factor_le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_up_factor_le.setText("1.0")

        self.throughput_le = QLineEdit()
        self.throughput_le.setReadOnly(True)
        self.throughput_le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.throughput_le.setText("0")

        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(2)

        # Layouts
        # Nested functions
        def create_hboxlayout(widget : QWidget) -> QHBoxLayout:
            hbox = QHBoxLayout()
            hbox.addStretch()
            hbox.addWidget(widget)
            hbox.addStretch()
            return hbox

        main_layout = QGridLayout()
        # main_layout.setContentsMargins(600,300,600,300)
        main_layout.addWidget(frame)

        top_row_v_layout = QVBoxLayout()
        top_row_v_layout.addLayout(create_hboxlayout(QLabel("SIMULATION TIME")))
        top_row_v_layout.addLayout(create_hboxlayout(self.time_le))
        top_row_v_layout.addStretch()

        pause_layout = QVBoxLayout()
        pause_layout.addLayout(create_hboxlayout(QLabel("PAUSE OR RESUME SIMULATION")))
        pause_layout.addLayout(create_hboxlayout(self.pause_resume_btn))

        speedup_layout = QVBoxLayout()
        speedup_layout.addLayout(create_hboxlayout(QLabel("SIMULATION SPEED UP MULTIPLIER")))
        speedup_layout.addLayout(create_hboxlayout(self.speed_up_factor_le))

        middle_row_h_layout = QHBoxLayout()
        # middle_row_h_layout.addStretch()
        middle_row_h_layout.addLayout(pause_layout)
        middle_row_h_layout.addLayout(speedup_layout)
        # middle_row_h_layout.addStretch()

        middle_row_v_layout = QVBoxLayout()
        # middle_row_v_layout.addLayout(create_hboxlayout(QLabel("SIMULATION TIME SETTINGS")))
        middle_row_v_layout.addLayout(middle_row_h_layout)
        middle_row_v_layout.addStretch()

        bottom_row_v_layout = QVBoxLayout()
        bottom_row_v_layout.addLayout(create_hboxlayout(QLabel("SYSTEM THROUGHPUT")))
        bottom_row_v_layout.addLayout(create_hboxlayout(self.throughput_le))
        bottom_row_v_layout.addStretch()

        inner_frame_layout = QVBoxLayout()
        # inner_frame_layout.setContentsMargins(20,20,20,20)
        inner_frame_layout.addStretch()
        inner_frame_layout.addLayout(top_row_v_layout)
        inner_frame_layout.addLayout(middle_row_v_layout)
        inner_frame_layout.addLayout(bottom_row_v_layout)
        inner_frame_layout.addStretch()


        main_layout.addLayout(inner_frame_layout,0,0,1,1)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)


        # signals
        self.sigs = Simulation_Time_Signals()
        self.speed_up_factor_val : float = 1.0
        self.is_paused = False
        self.speed_up_factor_le.textChanged.connect(self.update_sim_speedup)
        self.pause_resume_btn.clicked.connect(self.update_pause_resume)

    @Slot(int)
    def update_ticket_sales_from_track(self, ticket_sales: int):
        update_text = f"Throughput = {ticket_sales} passengers per hour per line!"
        print(update_text)
        self.throughput_label.setText(update_text)
        self.throughput_label.repaint()


    def update_sim_speedup(self, text : str) -> None:
        try:
            self.speed_up_factor_val = float(text)
        except ValueError:
            print("[CTC] [CTC OFFICE]: Cannot convert speed up factor to float.")
            return

        if self.speed_up_factor_val < 0.1:
            self.speed_up_factor_val = 1

        if self.speed_up_factor_val > 50.0:
            self.speed_up_factor_val = 50.0

        print(f"[CTC OFFICE]: New value for speed up factor: {text}.")

        self.sigs.speed_up_factor_update.emit(self.speed_up_factor_val)

    def update_pause_resume(self, state : bool):
        self.is_paused = state
        self.sigs.pause_resume_update.emit(self.is_paused)
        if self.is_paused:
            print(f"[CTC OFFICE]: Simulation is now paused!")
        else:
            print(f"[CTC OFFICE]: Simulation is now resuming!")



# ----------------------------------------------------------
class CreateTrains(QWidget):
    dispatch_train_manual = Signal(int, int, list, int)
    send_train_queue = Signal(list)
    send_trains_schedule_dict = Signal(dict)

    def __init__(self):
        super().__init__()


        # manual_left_side
        # making widgets
        index_label = QLabel("Train Number")
        index_value = QLabel("0")
        line_label = QLabel("Line")
        line_selector = QComboBox()
        depart_label = QLabel("Departure Time: ")
        depart_input = QLineEdit()
        depart_input_confirm_button = QPushButton("Confirm")

        line_selector.addItems(LINE_NAMES)

        # making layout
        manual_left_side = QGridLayout()
        manual_left_side.addWidget(index_label,0,0)
        manual_left_side.addWidget(line_label,0,1)
        manual_left_side.addWidget(index_value,1,0)
        manual_left_side.addWidget(line_selector,1,1)
        manual_left_side.addWidget(depart_label,2,0)
        manual_left_side.addWidget(depart_input,3,0)
        manual_left_side.addWidget(depart_input_confirm_button,2,1,2,1)





        # ------------------------------------------
        # add_stops


        stop_label = QLabel("Stop")
        self.stop_selector = QComboBox()

        self.stop_selector.addItems(GREEN_BLOCK_NAME_LIST)

        add_stop_button = QPushButton("Add Stop")
        launch_now_button = QPushButton("DISPATCH NOW TO BLOCK")


        launch_now_button.clicked.connect(self.launch_to_destination)

        stop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stop_table = StopTable()
        stop_table.setMinimumWidth(300)

        add_stops = QGridLayout()
        add_stops.addWidget(stop_label,0,0)
        add_stops.addWidget(self.stop_selector,1,0)
        add_stops.addWidget(add_stop_button,0,1)
        add_stops.addWidget(launch_now_button,0,2)
        add_stops.addWidget(stop_table,2,0,1,2)



        # ------------------------------------------
        # manual_tab

        add_schedule_button = QPushButton("Add Train to Queue")

        manual_tab = QGridLayout()
        manual_tab.addLayout(manual_left_side,0,0)
        manual_tab.addLayout(add_stops,0,1)
        manual_tab.addWidget(add_schedule_button,1,0,1,2)

        # ------------------------------------------
        # automatic tab
        import_schedule_button = QPushButton("Import Schedule")
        import_schedule_button.clicked.connect(self.open_file_explorer)

        automatic_tab = QGridLayout()
        automatic_tab.addWidget(import_schedule_button,0,0)


        # ------------------------------------------
        # putting the tabs together -> mode_tab_wiget
        mode_tab_widget = QTabWidget()

        automatic_tab_content = QWidget()
        automatic_tab_content.setLayout(automatic_tab)

        manual_tab_content = QWidget()
        manual_tab_content.setLayout(manual_tab)

        mode_tab_widget.addTab(manual_tab_content, "Manual")
        mode_tab_widget.addTab(automatic_tab_content, "Automatic")

        # title bar
        train_creation_label = QLabel("Train Creation")

        whole_section = QVBoxLayout()
        whole_section.addWidget(train_creation_label)
        whole_section.addWidget(mode_tab_widget)


        self.setLayout(whole_section)

    def open_file_explorer(self):
        print("[CTC] OPENING FILE EXPLORER")

        fileName, filter = QFileDialog.getOpenFileName(self, "Import Schedule", "./schedule", "CSV (*.csv)")

        if not fileName == '':
            print(f"[CTC] file_name = {fileName}")

            # CSVData = open(fileName)
            # Array2d_result = np.loadtxt(CSVData, delimiter=",")

            import csv
            data = list(csv.reader(open(fileName)))
            row_len = print(len(data))
            col_len = print(len(data[0]))



            train_queue_done = False

            num_rows = 1
            for row in range(len(data)):
                if row == -1:
                    num_rows = row

            # col,row
            queue_matrix = []


            schedules_dict = {}

            key = -1
            value = []
            for row in range(len(data)):
                if data[row][0] == '-1':
                    print("made it here")
                    train_queue_done = True
                    continue

                if not(train_queue_done):
                    row_list = []
                    for col in range(2):
                        row_list.append(data[row][col])
                    # print(f"row_list: {row_list}")
                    queue_matrix.append(row_list)
                else:
                    row_list = []
                    for col in range(4):
                        if key == -1:
                            key = data[row][0]
                        print(f"data[row][0]: {data[row][0]} | key: {key}")

                        if data[row][0] != key:
                            print(f"in here, key {key}, value {value}")
                            schedules_dict.update({key: value})
                            value = []
                            key = data[row][0]

                        if col > 0:
                            row_list.append(data[row][col])

                    value.append(row_list)

            schedules_dict.update({key: value})
            print(f"queue matrix: {queue_matrix}")
            print(f"schedule queue: {schedules_dict}")

            self.send_train_queue.emit(queue_matrix)
            self.send_trains_schedule_dict.emit(schedules_dict)



            print("[CTC] ")



    def launch_to_destination(self):
        print(f"[CTC]  YEET: {self.stop_selector.currentText()}")

        auth = self.stop_selector.currentText()
        auth = auth[1:]
        print(f"[CTC]  YEET2: {auth}")
        first_space = auth.find(" ")
        if first_space != -1:
            auth = auth[:first_space+1]
        print(f"[CTC]  YEET2: {auth}")
        auth_num = int(auth)

        auth_num_list = []
        auth_num_list.append(auth_num)



        block = 63
        speed = 10
        switch = 1
        print(f"[CTC] Sending: block: {block}, speed: {speed}, auth: {auth_num}, switch:, {switch}")
        self.dispatch_train_manual.emit(block, speed, auth_num_list, switch)

# ----------------------------------------------------------
class TrainQueue(QWidget):
    send_departure_times = Signal(dict)

    def __init__(self):
        super().__init__()

        # creating widgets
        train_queue_label = QLabel("Train Queue")
        self.departure_table = DepartureTable()
        self.departure_table.clear()
        self.departure_table.setColumnCount(2)
        self.departure_table.setRowCount(4)
        self.departure_table.verticalHeader().setVisible(False)
        header_labels = ["Index", "Departure Time"]
        self.departure_table.setHorizontalHeaderLabels(header_labels)
        selected_train_label = QLabel("Train Schedule")
        self.stop_table = StopTable()
        depart_time_label = QLabel("Departure Time: ")
        depart_time_input = QLineEdit()
        delete_selected_button = QPushButton("Delete")
        dispatch_now_button = QPushButton("Dispatch Now")


        self.departure_table.cellClicked.connect(self.set_bottom_table_data)

        self.stop_table.setMinimumHeight(200)
        self.stop_table.setMinimumWidth(300)

        # adding widgets to layout
        layout = QGridLayout()
        layout.addWidget(train_queue_label,0,0,1,3)
        layout.addWidget(self.departure_table,1,0,1,3)
        layout.addWidget(selected_train_label,2,0,1,3)
        layout.addWidget(self.stop_table,3,0,2,1)
        layout.addWidget(depart_time_label,3,1)
        layout.addWidget(depart_time_input,3,2)
        layout.addWidget(delete_selected_button,4,1)
        layout.addWidget(dispatch_now_button,4,2)

        self.schedules_dict = {}

        self.setLayout(layout)

    @Slot(list)
    def set_top_table_data(self, data):
        print(f"top table: {data}")

        self.departure_table.clear()
        self.departure_table.setColumnCount(2)
        self.departure_table.setRowCount(len(data))
        self.departure_table.verticalHeader().setVisible(False)
        header_labels = ["Index", "Departure Time"]
        self.departure_table.setHorizontalHeaderLabels(header_labels)

        for i, row_data in enumerate(data):
            for j, cell_data in enumerate(row_data):
                table_item = QTableWidgetItem(cell_data)
                self.departure_table.setItem(i, j, table_item)

        departure_dict = {}
        for row in range(len(data)):
                departure_dict.update({data[row][0]:data[row][1]})

        print(f"DEPARTURE DICT: {departure_dict}")
        self.send_departure_times.emit(departure_dict)



    def set_bottom_table_data(self,row,col):

        index = str(row)
        matrix = self.schedules_dict[index]

        print(f"index: {index}")
        print(f"matrix: {matrix}")

        self.stop_table.clear()

        self.stop_table.setColumnCount(3)
        self.stop_table.setRowCount(len(matrix))
        self.stop_table.verticalHeader().setVisible(False)
        header_labels = ["Stop", "Dwell", "ETA"]
        self.stop_table.setHorizontalHeaderLabels(header_labels)

        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                table_item = QTableWidgetItem()
                table_item.setText(matrix[i][j])
                self.stop_table.setItem(i, j, table_item)


        # item = QTableWidgetItem()
        # item.setText(str(row))
        # self.stop_table.setItem(0,0,item)

    @Slot()
    def set_dict_stuff(self, data):
        print(f"bottom: {data}")
        self.schedules_dict = data




# ----------------------------------------------------------
class ActiveTrains(QWidget):
    def __init__(self):
        super().__init__()

        # creating widgets
        active_trains_label = QLabel("Active Trains")
        active_trains_table = ActiveTrainsTable()
        selected_train_label = QLabel("Train Schedule")
        stop_table = StopTable()
        manual_speed_label = QLabel("Manual: Suggested Speed")
        manual_speed_input = QLineEdit()
        manual_speed_confirm_button = QPushButton("Confirm")

        active_trains_table.setMinimumWidth(400)



        # adding widgets to layout
        layout = QGridLayout()
        layout.addWidget(active_trains_label,0,0,1,3)
        layout.addWidget(active_trains_table,1,0,1,3)
        layout.addWidget(selected_train_label,2,0,1,3)
        layout.addWidget(stop_table,3,0,2,1)
        layout.addWidget(manual_speed_label,3,1,1,2)
        layout.addWidget(manual_speed_input,4,1)
        layout.addWidget(manual_speed_confirm_button,4,2)


        self.setLayout(layout)


# ----------------------------------------------------------
class MaintenanceTab(QWidget):
    update_maintenance_close_button = Signal(Line, str)
    update_maintenance_open_button = Signal(Line, str)

    def __init__(self):
        super().__init__()

        maintenance_font = QFont()
        maintenance_font.setPointSize(60)

        # ------------------------------------------
        # row 1 - select line
        line = QLabel("Line: ")
        self.select_line = QComboBox()
        self.line_button = QPushButton("Select Line")

        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.select_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.line_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # line.setFont(maintenance_font)
        # self.select_line.setFont(maintenance_font)
        # self.line_button.setFont(maintenance_font)

        self.select_line.addItem("Green")
        self.select_line.addItem("Red")

        row1 = QHBoxLayout()
        row1.addWidget(line)
        row1.addWidget(self.select_line)
        row1.addWidget(self.line_button)

        self.line_button.clicked.connect(self.change_line)

        # ------------------------------------------
        # row 2 - closing blocks
        close_block = QLabel("Close Section: ")
        self.select_close_block = QComboBox()
        self.close_block_button = QPushButton("RUN")

        close_block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.select_close_block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.close_block_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # close_block.setFont(maintenance_font)
        # self.select_close_block.setFont(maintenance_font)
        # self.close_block_button.setFont(maintenance_font)

        row2 = QHBoxLayout()
        row2.addWidget(close_block)
        row2.addWidget(self.select_close_block)
        row2.addWidget(self.close_block_button)

        # ------------------------------------------
        # row 3 - opening blocks
        open_block = QLabel("Open Section: ")
        self.select_open_block = QComboBox(self)
        self.open_block_button = QPushButton("RUN")

        open_block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.select_open_block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.open_block_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # open_block.setFont(maintenance_font)
        # self.select_open_block.setFont(maintenance_font)
        # self.open_block_button.setFont(maintenance_font)

        row3 = QHBoxLayout()
        row3.addWidget(open_block)
        row3.addWidget(self.select_open_block)
        row3.addWidget(self.open_block_button)

        # ------------------------------------------
        # putting it all together

        v_layout = QVBoxLayout()
        v_layout.addLayout(row1)
        v_layout.addLayout(row2)
        v_layout.addLayout(row3)

        self.setLayout(v_layout)

        self.close_block_button.clicked.connect(self.close_block)
        self.open_block_button.clicked.connect(self.open_block)

        # initializing maintenance list
        for _, ele in enumerate(GREEN_LINE_SECTION_DICT.keys()):
            self.select_close_block.addItem(ele)
            self.select_open_block.addItem(ele)

        self.setStyleSheet("background-color: #f0f0f0;")

        # ------------------------------------------

    def close_block(self):
        index = self.select_close_block.currentText()
        print("[CTC] [CTC_OFFICE]: CLOSING SECTION: {index}!")
        line = self.select_line.currentText()

        self.update_maintenance_close_button.emit(line, index)

    def open_block(self):
        index = self.select_open_block.currentText()
        print("[CTC] [CTC_OFFICE]: OPENING BLOCK {index}!")

        line = self.select_line.currentText()
        self.update_maintenance_open_button.emit(line,index)

    def change_line(self):
        #print("[CTC] file: ctc_office_ui, function: change_line")
        line = self.select_line.currentText()

        # print("[CTC] [CTC_OFFICE]: line: {line}")

        self.select_close_block.clear()
        self.select_open_block.clear()

        if line == "Blue":
            for _, ele in enumerate(BLUE_LINE_SECTION_DICT.keys()):
                self.select_close_block.addItem(ele)
                self.select_open_block.addItem(ele)
        elif line == "Green":
            for _, ele in enumerate(GREEN_LINE_SECTION_DICT.keys()):
                self.select_close_block.addItem(ele)
                self.select_open_block.addItem(ele)
        elif line == "Red":
            for _, ele in enumerate(RED_LINE_SECTION_DICT.keys()):
                self.select_close_block.addItem(ele)
                self.select_open_block.addItem(ele)

    def current_value2(self):
        print("[CTC] Current item : ", self.select_open_block.currentText(),
                " - current index : ", self.select_open_block.currentIndex())
        return self.select_open_block.currentText()


# ----------------------------------------------------------
class CTC_MainTab(QWidget):
    def __init__(self):
        super().__init__()

        self.schedule_dict = {}

        self.general_info = GeneralInfo()
        self.create_trains = CreateTrains()
        self.train_queue = TrainQueue()
        self.active_trains = ActiveTrains()
        self.maintenance = MaintenanceTab()

        layout = QGridLayout()
        layout.addWidget(self.general_info,0,0,1,3)
        layout.addWidget(self.create_trains,1,0)
        layout.addWidget(self.train_queue,1,1)
        layout.addWidget(self.active_trains,1,2)
        layout.addWidget(self.maintenance,2,0,1,3)

        layout.setColumnStretch(0,1)
        layout.setColumnStretch(1,1)
        layout.setColumnStretch(2,1)

        # connecting signals

        self.create_trains.send_train_queue.connect(self.train_queue.set_top_table_data)
        self.create_trains.send_trains_schedule_dict.connect(self.train_queue.set_dict_stuff)

        self.setLayout(layout)

# ----------------------------------------------------------
class CTC_Office_UI(QWidget):
    update_signal = Signal()

    def __init__(self):
        super().__init__()
        tab_widget = QTabWidget(self)

        # ------------------------------------------
        # dynamic map

        self.data = [ [None] * 37 for _ in range(47)]

        # Green Yard Connection
        self.data[20][32] = Block_Info.GREEN_YARD_CONNECTION
        self.data[21][32] = Block_Info.GREEN_YARD_CONNECTION
        for i in range(20, 31):
            self.data[i][36] = Block_Info.GREEN_YARD_CONNECTION
        self.data[29][35] = Block_Info.GREEN_YARD_CONNECTION
        self.data[30][35] = Block_Info.GREEN_YARD_CONNECTION


        # Red Yard Connection
        self.data[14][32] = Block_Info.RED_YARD_CONNECTION
        self.data[13][32] = Block_Info.RED_YARD_CONNECTION
        self.data[12][32] = Block_Info.RED_YARD_CONNECTION

        # Text Information
        self.data[1][0] = "time:"
        self.data[2][0] = "ticket"
        self.data[2][1] = " sales:"

        # Yard Blocks
        for i in range(15,20,1):
            for j in range(32,37,1):
                self.data[i][j] = "YARD"


        # Defs
        green_block_status: list[int] = [0] * (GREEN_LINE_NUMBER_OF_BLOCKS+1)
        red_block_status: list[int] = [0] * (RED_LINE_NUMBER_OF_BLOCKS+1)

        green_maintenance_status: list[int] = [0] * (GREEN_LINE_NUMBER_OF_BLOCKS+1)
        red_maintenance_status: list[int] = [0] * (RED_LINE_NUMBER_OF_BLOCKS+1)


        # ------------------------------------------
        # TAB 1: View System
        view_map = QWidget()

        # interactive map
        self.model = CTC_TableModel(self.data)
        self.map = QTableView()
        self.map.setModel(self.model)
        self.map.setShowGrid(True)
        self.map.horizontalHeader().setVisible(False)
        self.map.verticalHeader().setVisible(False)
        self.map.verticalHeader().setMaximumSectionSize(17)
        self.map.horizontalHeader().setMaximumSectionSize(30)

        self.map.resizeRowsToContents()
        self.map.resizeColumnsToContents()


        self.delegate = CTC_Map_Style()
        self.map.setItemDelegate(self.delegate)
        # self.model.dataChanged.connect(self.model.hi)
        for i in range(0,8*2,2):
            self.map.setSpan(25+i,34,2,1)
        for i in range(0,8*2,2):
            self.map.setSpan(25+i,31,2,1)


        # time
        self.time = QLabel("time: 08:00")
        font = self.time.font()
        font.setPointSize(24)
        self.time.setFont(font)
        self.time.setAlignment(QtCore.Qt.AlignCenter)

        # throughput
        self.throughput_label = QLabel("Throughput = 0 passengers per hour per line!")
        font = self.time.font()
        font.setPointSize(24)
        self.throughput_label.setFont(font)
        self.throughput_label.setAlignment(QtCore.Qt.AlignCenter)

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.throughput_label)

        form_layout.addWidget(self.map)
        view_map.setLayout(form_layout)


        # ------------------------------------------
        # TAB 2: Maintenance

        # ------------------------------------------
        # TAB 3: Manual: Dispatch
        dispatch_font = QFont()
        dispatch_font.setPointSize(60)

        dispatch = QWidget()
        dispatch_layout = QVBoxLayout()

        dispatch_up = QPushButton("DISPATCH TO STATION; DORMONT")
        dispatch_down = QPushButton("TBD")

        dispatch_up.setFont(dispatch_font)
        dispatch_down.setFont(dispatch_font)

        dispatch_up.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        dispatch_down.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        dispatch_layout.addWidget(dispatch_up)
        dispatch_layout.addWidget(dispatch_down)
        dispatch.setLayout(dispatch_layout)

        dispatch_up.clicked.connect(self.send_train)

        # ------------------------------------------
        # TAB 4:


        self.main_tab = CTC_MainTab()

        self.output_tab = QWidget()

        output_label = QLabel("Speed, Authority, and Outputs:")
        self.stdout = QTextEdit()
        self.stdout.setReadOnly(True)

        out_layout = QGridLayout()
        out_layout.addWidget(output_label,0,0)
        out_layout.addWidget(self.stdout,1,0)
        self.output_tab.setLayout(out_layout)


        # ------------------------------------------
        tab_widget.addTab(self.main_tab, "Main")
        tab_widget.addTab(view_map, "Map")
        tab_widget.addTab(self.output_tab, "Output")


        layout = QVBoxLayout()
        layout.addWidget(tab_widget)

        self.setLayout(layout)

        self.update_data_from_backend(Line.GREEN, green_block_status, green_maintenance_status)
        self.update_data_from_backend(Line.RED, red_block_status, red_maintenance_status)

        self.departure_dict = {}

        self.main_tab.train_queue.send_departure_times.connect(self.update_departure_dict)

        # ------------------------------------------

    def send_train(self):
        print("[CTC] dispatching new train from button!")
        self.update_signal.emit()

    @Slot(Line, list, list)
    def update_data_from_backend(self, line: Line, block_status_list: list, maintenance_status_list: list):
        # print("[CTC] file: ctc_office_ui, function: update_data_from_backend")
        # print("[CTC] [CTC_OFFICE]: line: {line}")

        index_to_map_dict = {}

        if line == Line.BLUE:
            index_to_map_dict = BLUE_LINE_INDEX_TO_MAP_DICT
        elif line == Line.GREEN:
            index_to_map_dict = GREEN_LINE_INDEX_TO_MAP_DICT
        elif line == Line.RED:
            index_to_map_dict = RED_LINE_INDEX_TO_MAP_DICT

        for i in range(1,len(block_status_list),1):
            pos = index_to_map_dict[i]

            if isinstance(pos, list):
                for _,ele in enumerate(pos):
                    if maintenance_status_list[i] == 1:
                        self.data[ele.row][ele.col] = -1
                        self.model.setData(self.model.createIndex(ele.row, ele.col), -1, Qt.DisplayRole)
                    elif block_status_list[i] == 1:
                        self.data[ele.row][ele.col] = 1
                        self.model.setData(self.model.createIndex(ele.row, ele.col), 1, Qt.DisplayRole)
                    elif line == Line.GREEN:
                        self.data[ele.row][ele.col] = 0
                        self.model.setData(self.model.createIndex(ele.row, ele.col), 0, Qt.DisplayRole)
                    elif line == Line.RED:
                        self.data[ele.row][ele.col] = 2
                        self.model.setData(self.model.createIndex(ele.row, ele.col), 2, Qt.DisplayRole)
                    # TODO: document what each of the numbers mean better

            else:
                # maintenance overrides block status, if maintenance, display closed on map
                if maintenance_status_list[i] == 1:
                    self.data[pos.row][pos.col] = -1
                    self.model.setData(self.model.createIndex(pos.row, pos.col), -1, Qt.DisplayRole)
                elif block_status_list[i] == 1:
                    self.data[pos.row][pos.col] = 1
                    self.model.setData(self.model.createIndex(pos.row, pos.col), 1, Qt.DisplayRole)
                elif line == Line.GREEN:
                    self.data[pos.row][pos.col] = 0
                    self.model.setData(self.model.createIndex(pos.row, pos.col), 0, Qt.DisplayRole)
                elif line == Line.RED:
                    self.data[pos.row][pos.col] = 2
                    self.model.setData(self.model.createIndex(pos.row, pos.col), 2, Qt.DisplayRole)
                # TODO: document what each of the numbers mean better

    @Slot(str)
    def update_time_from_backend(self, time):
        self.data[1][1] = time
        self.model.setData(self.model.createIndex(1,1), time, Qt.DisplayRole)

        departure_list = self.departure_dict.values()

        for i,ele in enumerate(departure_list):
            if time == ele:
                key = self.get_key(ele)
                print(f"key = {key}")
                text = f"DISPATCHING TRAIN: {key} from schedule"
                self.update_stdout(text)

                block = 63
                speed = 10
                switch = 1

                mat = self.main_tab.train_queue.schedules_dict[key]


                stops = []
                for row in range(len(mat)):
                    stops.append(int(mat[row][0]))

                text = f"stops: {stops}_"
                self.update_stdout(text)
                self.main_tab.create_trains.dispatch_train_manual.emit(block, speed, stops, switch)



                # print(f"[CTC] Sending: block: {block}, speed: {speed}, auth: {auth_num}, switch:, {switch}")
                # self.dispatch_train_manual.emit(block, speed, auth_num, switch)


        # print(f"departure_list = {departure_list}")

    def get_key(self,val):
        for key, value in self.departure_dict.items():
            if val == value:
                return key

    @Slot(dict)
    def update_departure_dict(self, data):
        self.departure_dict = data
        print(f"self.departure: {self.departure_dict}")


    @Slot(str)
    def update_stdout(self, text):
        # todo add back
        # print("[CTC] outputing authority command to ui")
        self.stdout.append(text)

# ----------------------------------------------------------
