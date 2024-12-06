from train.train_model.ui.ui_help import *

class Train_Manager_Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Train Manager")

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
        TM_frame_layout = QVBoxLayout()
        # TM_frame_layout.addStretch()
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

        TM_layout = QGridLayout()
        TM_layout.addWidget(UI_Help.create_frame())
        TM_layout.addLayout(TM_frame_layout,0,0,1,1)

        final_layout = QHBoxLayout()
        # final_layout.addStretch()
        final_layout.addLayout(TM_layout)
        final_layout.addStretch()

        widget = Color('light blue')
        widget.setLayout(final_layout)
        self.setCentralWidget(widget)

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
