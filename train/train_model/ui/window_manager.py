from train_model.ui.ui_help import *
from core.qthreads_stripped import QThreadPool_Manager, QThreadPool_Data
from train_model.ui.train_model_ui import MainWindow

class Test_Windows(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Test Bench")

        self.test_tabs = QTabWidget()
        self.test_tabs.setTabPosition(QTabWidget.West)
        self.test_tabs.setMovable(False)
        self.test_tabs.setTabShape(QTabWidget.TabShape.Rounded)
        self.setCentralWidget(self.test_tabs)
        self.tab_index_offset = 0

        # Train Manager
        self.add_train_dsp = QDoubleSpinBox()
        self.add_train_dsp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_train_dsp.setDecimals(0)
        self.add_train_dsp.setValue(1)
        self.add_train_btn = QPushButton(text="Add Train(s)")
        self.remove_train_le = QLineEdit()
        self.remove_train_le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remove_train_btn = QPushButton(text="Remove Train(s)")
        self.running_train_count = QLineEdit()
        self.running_train_count.setReadOnly(True)
        self.running_train_count.setText("0")
        self.running_train_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.new_train_count = QLineEdit()
        self.new_train_count.setReadOnly(True)
        self.new_train_count.setText("0")
        self.new_train_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.print_trains_btn = QPushButton(text="Print All Trains")
        self.print_threadpool_data = QPushButton(text="Print Threadpool Data")

        self.create_train_manager_page()
       

    def create_train_manager_page(self) -> None:

        # Train Manager (TM) Layout
        TM_layout = QGridLayout()
        TM_layout.addWidget(UI_Help.create_frame())

        TM_frame_layout = QVBoxLayout()
        TM_frame_layout.setContentsMargins(130,15,130,15)
        TM_frame_layout.addWidget(UI_Help.create_label("Train Manager", Fonts.tui_block_header))
        TM_frame_layout.addSpacerItem(QSpacerItem(10,20))
        
        TM_stats_layout = QHBoxLayout()
        TM_stats_layout.addWidget(QLabel(text="Number of trains running:"))
        TM_stats_layout.addWidget(self.running_train_count)

        TM_frame_layout.addLayout(TM_stats_layout)
        TM_frame_layout.addSpacerItem(QSpacerItem(10,20))

        add_train_layout = QHBoxLayout()
        add_train_layout.addWidget(QLabel(text="Add train(s) :"))
        add_train_layout.addWidget(self.add_train_dsp)

        TM_frame_layout.addLayout(add_train_layout )
        TM_frame_layout.addWidget(self.add_train_btn)
        TM_frame_layout.addSpacerItem(QSpacerItem(10,20))

        remove_train_layout = QHBoxLayout()
        remove_train_layout.addWidget(QLabel(text="Remove train(s): "))
        remove_train_layout.addWidget(self.remove_train_le)

        TM_frame_layout.addLayout(remove_train_layout)
        TM_frame_layout.addWidget(self.remove_train_btn)
        remove_instr = QLabel()
        remove_instr.setWordWrap(True)
        remove_instr.setText("* Remove train by specifying the train number. Several trains can be removed at once by providing a comma separated list.")

        TM_frame_layout.addWidget(remove_instr)
        TM_frame_layout.addSpacerItem(QSpacerItem(10,20))
        TM_frame_layout.addWidget(UI_Help.create_label("Debugging", Fonts.tui_block_header))
        TM_frame_layout.addWidget(self.print_trains_btn)
        TM_frame_layout.addWidget(self.print_threadpool_data)

        TM_frame_layout.addStretch()

        # Add to main layout, set color and central
        TM_layout.addLayout(TM_frame_layout,0,0,1,1)

        widget = Color('light blue')
        widget.setLayout(TM_layout)
        self.add_non_train_tab(widget, "Train Manager")

    def get_trains_to_add(self) -> int:
        try: return int(self.add_train_dsp.value())
        except ValueError: return 0

    def get_trains_to_remove(self) -> list:
        text = self.remove_train_le.text()
        try:
            remove_list = text.split(',')
        except:
            print("[TRAIN]: Failed to parse remove list.")
            return None
        
        for i in range(0, len(remove_list)):
            try:
                remove_list[i] = int(remove_list[i])
            except:
                print("[TRAIN]: Failed to prase remove list.")
                return None
            
        return remove_list
            
    def set_active_trains(self, count: int) -> None:
        self.running_train_count.setText(str(count))

    def add_non_train_tab(self, widget : QWidget,  tab_name : str) -> None:
        self.tab_index_offset += 1
        self.test_tabs.addTab(widget, tab_name)

    def add_tab(self,widget : QWidget, tab_name : str) -> None:
        self.test_tabs.addTab(widget, tab_name) 

    def remove_tab(self, idx: int) -> None:
        actual_idx = self.tab_index_offset + idx
        self.test_tabs.widget(actual_idx).deleteLater()
        self.test_tabs.removeTab(actual_idx)

    def set_current_tab(self, idx: int) -> None:
        self.test_tabs.setCurrentIndex(idx + self.tab_index_offset)
        

class Main_Windows(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Train Model")

        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.West)
        self.main_tabs.setMovable(False)
        self.main_tabs.setTabShape(QTabWidget.TabShape.Rounded)

        self.setCentralWidget(self.main_tabs)

    def add_tab(self,widget : QWidget, tab_name : str) -> None:
        self.main_tabs.addTab(widget, tab_name) 

    def remove_tab(self, idx: int) -> None:
        self.main_tabs.widget(idx).deleteLater()
        self.main_tabs.removeTab(idx)

    def get_index_of(self, widget : QWidget) -> None:
        return self.main_tabs.indexOf(widget)
    
    def set_current_tab(self, idx: int) -> None:
        self.main_tabs.setCurrentIndex(idx)
    

class Main_App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # Create tabbed windows
        self.main_windows = Main_Windows()
        self.test_windows = Test_Windows()

        # Create thread manager
        self.qthread_manager = QThreadPool_Manager()

        # Flag for whether the first train has been added.
        self.firstTabAdded = False

        # Connect Train Manager Signals Up
        self.test_windows.add_train_btn.clicked.connect(self.add_trains_btn_clicked)
        self.test_windows.remove_train_btn.clicked.connect(self.remove_trains_btn_clicked)
        self.test_windows.print_trains_btn.clicked.connect(self.qthread_manager.print_obj_list)
        self.test_windows.print_threadpool_data.clicked.connect(self.qthread_manager.print_active_threads_all)
        self.test_windows.test_tabs.currentChanged.connect(self.handle_test_tab_change)

        # Show the test window which has the train manager page
        self.test_windows.show()


    def show_all_windows(self) -> None:
        self.test_windows.show()
        self.main_windows.show()
        self.show()

    def show_tabbed_windows(self) -> None:
        self.test_windows.show()
        self.main_windows.show()

    def add_trains_btn_clicked(self) -> None:
        num = self.test_windows.get_trains_to_add()
        
        if num > 0:
            for _ in range(0, num):
                self.add_tab()


    def remove_trains_btn_clicked(self) -> None:
        remove_idxs = self.test_windows.get_trains_to_remove()
        
        if remove_idxs == None: 
            return
        
        for idx in remove_idxs:
            self.remove_tab(idx)

    def handle_test_tab_change(self, new_tab_idx : int) -> None:
        # print(new_tab_idx)
        if new_tab_idx == -1:
            return
        self.main_windows.set_current_tab(new_tab_idx - self.test_windows.tab_index_offset)


    def add_tab(self) -> None:

        new_train = MainWindow(self.qthread_manager.get_total_obj_count())

        self.qthread_manager.add_thread(new_train.train)

        idx = new_train.train.get_identifier()

        self.main_windows.add_tab(new_train.window(), f"  {idx}  ")
        self.test_windows.add_tab(new_train.tb.window(), f"  {idx}  " )

        if(self.firstTabAdded == False):
            self.firstTabAdded = True
            self.layout_windows()

        self.test_windows.set_active_trains(self.qthread_manager.get_running_obj_count())

        # new_train.graph.show()
            
            
    def layout_windows(self) -> None:
        # Show the windows now
        self.show_tabbed_windows()

        # Get the geometry of the screen and test bench
        screen_geo = self.screen().availableGeometry()
        tb_geo = self.test_windows.geometry()
        self.test_windows.setGeometry(0,0,tb_geo.width() - 100, screen_geo.height())
        tb_geo = self.test_windows.geometry()

        # Move the top left corner of the test window to top right of the screen
        self.test_windows.move(screen_geo.topRight() - QPoint(tb_geo.width(),0))

        # Move the main window to fill the rest of the space
        self.main_windows.setGeometry(0,0, screen_geo.width() - tb_geo.width(), screen_geo.height() - 20)
        self.main_windows.move(screen_geo.topLeft())


    def remove_tab(self, idx : int) -> None:

        obj = self.qthread_manager.peek_idx(idx)
        if obj is None:
            print("[TRAIN]: bad idx")
            return 
        

        # find tab_index
        # TODO: clean this up
        tab_idx = 0
        for i in range(0, self.main_windows.main_tabs.count()):
            if obj == self.main_windows.main_tabs.widget(i).train:
                tab_idx = i
                break
        

        # tab_idx = self.main_windows.get_index_of(self.qthread_manager.peek_idx(idx))

        self.main_windows.remove_tab(tab_idx)
        self.test_windows.remove_tab(tab_idx)

        self.qthread_manager.remove_thread(idx)

        self.test_windows.set_active_trains(self.qthread_manager.get_running_obj_count())