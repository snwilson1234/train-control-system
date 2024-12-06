# QThread Manager
from train.core.qthreads_stripped import QThreadPool_Manager

# Tabbed UIs
from train.train_model.ui.ui_help import *
from train.train_model.ui.main_windows import Main_Windows

# Train Model UI
from train.train_model.ui.train_model_ui import Train_Model_Main_Window

# Train Controller UIs
from train.train_controller.driver_window import DriverWindow
from train.train_controller.train_engineer_ui import TrainEngineerWindow
from train.train_controller.test_window import TestBenchWindow

# Train Manager
from train.train_model.ui.train_manger_ui import Train_Manager_Window


class Main_App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # Stores all the test windows in a tab layout
        self.tabbed_test_wins = QTabWidget()
        self.tabbed_test_wins.setWindowTitle("Train Test Windows")
        self.tabbed_test_wins.setTabPosition(QTabWidget.North)

        # store all the main windows in a tab layout
        self.tabbed_main_wins = QTabWidget()
        self.tabbed_main_wins.setWindowTitle("Train Main Windows")
        self.tabbed_main_wins.setTabPosition(QTabWidget.North)

        # Create tabbed windows
        self.model_main_windows = Main_Windows("Train Model")
        self.model_test_windows = Main_Windows("Train Model Test Bench")
        self.driver_windows = Main_Windows("Train Driver")
        self.train_engineer_windows = Main_Windows("Train Engineer")
        self.controller_test_windows = Main_Windows("Train Controller Test Bench")

        # Create Train Manager
        self.train_manager = Train_Manager_Window()

        # Create thread manager
        self.qthread_manager = QThreadPool_Manager()

        # Flag for whether the first train has been added.
        self.firstTabAdded = False

        # Connect Train Manager Signals Up
        self.train_manager.add_train_btn.clicked.connect(self.add_trains_btn_clicked)
        self.train_manager.remove_train_btn.clicked.connect(self.remove_trains_btn_clicked)
        self.train_manager.print_trains_btn.clicked.connect(self.qthread_manager.print_obj_list)
        self.train_manager.print_threadpool_data.clicked.connect(self.qthread_manager.print_active_threads_all)
        
        # Have tab click change all of the tabs
        self.model_test_windows.main_tabs.tabBarClicked.connect(self.handle_any_tabbar_clicked)
        self.train_engineer_windows.main_tabs.tabBarClicked.connect(self.handle_any_tabbar_clicked)
        self.model_main_windows.main_tabs.tabBarClicked.connect(self.handle_any_tabbar_clicked)
        self.controller_test_windows.main_tabs.tabBarClicked.connect(self.handle_any_tabbar_clicked)
        self.driver_windows.main_tabs.tabBarClicked.connect(self.handle_any_tabbar_clicked)

        # Show the train manager
        # self.train_manager.show()

    def handle_any_tabbar_clicked(self, idx : int):
        if idx == -1:
            return

        self.model_test_windows.set_current_tab(idx) 
        self.train_engineer_windows.set_current_tab(idx)
        self.model_main_windows.set_current_tab(idx)
        self.controller_test_windows.set_current_tab(idx)
        self.driver_windows.set_current_tab(idx)

        


    def show_tabbed_windows(self) -> None:
        self.model_test_windows.show()
        self.model_main_windows.show()
        self.driver_windows.show()
        self.train_engineer_windows.show()
        self.controller_test_windows.show()

    def add_trains_btn_clicked(self) -> None:
        num = self.train_manager.get_trains_to_add()
        
        if num > 0:
            for _ in range(0, num):
                self.add_tab()


    def remove_trains_btn_clicked(self) -> None:
        remove_idxs = self.train_manager.get_trains_to_remove()
        
        if remove_idxs == None: 
            return
        
        for idx in remove_idxs:
            self.remove_tab(idx)


    def add_tab(self) -> None:

        new_train = Train_Model_Main_Window(self.qthread_manager.get_total_obj_count())
        driver_window = DriverWindow(new_train.train.controller)
        train_engineer_window = TrainEngineerWindow(new_train.train.controller)
        controller_test_window = TestBenchWindow(new_train.train.controller)

        self.qthread_manager.add_thread(new_train.train)

        idx = new_train.train.get_identifier()

        self.model_main_windows.add_tab(new_train.window(), f"  {idx}  ")
        self.model_test_windows.add_tab(new_train.tb.window(), f"  {idx}  " )
        self.driver_windows.add_tab(driver_window.window(), f"  {idx}  ")
        self.train_engineer_windows.add_tab(train_engineer_window.window(), f"  {idx}  ")
        self.controller_test_windows.add_tab(controller_test_window.window(), f"  {idx}  ")

        if(self.firstTabAdded == False):
            self.firstTabAdded = True
            self.layout_windows()

        self.train_manager.set_active_trains(self.qthread_manager.get_running_obj_count())            
            
    def layout_windows(self) -> None:
        # Show the windows now

        self.tabbed_test_wins.addTab(self.model_test_windows.window(), "Train Model Test Bench")
        self.tabbed_test_wins.addTab(self.controller_test_windows.window(), "Train Controller Test Bench")
        self.tabbed_test_wins.show()

        self.tabbed_main_wins.addTab(self.train_manager.window(), "Train Manager")
        self.tabbed_main_wins.addTab(self.model_main_windows.window(), "Train Model Home")
        self.tabbed_main_wins.addTab(self.train_engineer_windows.window(), "Train Engineer")
        self.tabbed_main_wins.addTab(self.driver_windows.window(), "Train Controller Home")
        self.tabbed_main_wins.show()

        self.tabbed_main_wins.setCurrentIndex(3)

        self.show_tabbed_windows()

        # Get the geometry of the screen and test bench
        screen_geo = self.screen().availableGeometry()
        tb_geo = self.model_test_windows.geometry()
        self.tabbed_test_wins.setGeometry(0,0,tb_geo.width() - 100, screen_geo.height())
        tb_geo = self.model_test_windows.geometry()

        # Move the top left corner of the test window to top right of the screen
        self.tabbed_test_wins.move(screen_geo.topRight() - QPoint(tb_geo.width(),0))

        # Move the main window to fill the rest of the space
        self.tabbed_main_wins.setGeometry(0,0, screen_geo.width() - tb_geo.width(), screen_geo.height() - 20)
        self.tabbed_main_wins.move(screen_geo.topLeft())


    def remove_tab(self, idx : int) -> None:

        # Get the train object
        obj = self.qthread_manager.peek_idx(idx)
        if obj is None:
            print(f"[TRAIN]: Bad index provided. Returning from remove_tab({idx})")
            return 
        
        # Find the tab index by searching widgets and comparing the train object references
        # Not a great way to do this but couldn't come up with anything else for the moment.
        tab_idx = 0
        for i in range(0, self.model_main_windows.main_tabs.count()):
            if obj == self.model_main_windows.main_tabs.widget(i).train:
                tab_idx = i
                break

        # Remove the thread
        self.qthread_manager.remove_thread(idx)
    
        # Remove all the tabs
        self.model_main_windows.remove_tab(tab_idx)
        self.model_test_windows.remove_tab(tab_idx)
        self.train_engineer_windows.remove_tab(tab_idx)
        self.driver_windows.remove_tab(tab_idx)
        self.controller_test_windows.remove_tab(tab_idx)

        # Update active train count
        self.train_manager.set_active_trains(self.qthread_manager.get_running_obj_count())
