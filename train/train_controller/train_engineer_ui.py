import sys

from train.train_model.ui.ui_help import *

from train.train_controller.train_controller_class import TrainController


class TrainEngineerWindow(QMainWindow):
    def __init__(self, train: TrainController):
        super().__init__()
        self.train = train
        self.create_engineer_window()

    def create_engineer_window(self):
        page = QWidget()

        self.setWindowTitle("Train Engineer Inputs")

        kp_text = QLabel("Kp = ")
        ki_text = QLabel("Ki = ")

        self.KP_val = QLineEdit()
        self.KI_val = QLineEdit()
        self.KP_val.setText(str(self.train.Kp))
        self.KI_val.setText(str(self.train.Ki))

        val_layout = QHBoxLayout()
        val_layout.addStretch()
        val_layout.addWidget(kp_text)
        val_layout.addWidget(self.KP_val)
        val_layout.addWidget(ki_text)
        val_layout.addWidget(self.KI_val)
        val_layout.addStretch()



        self.apply_vals = QPushButton("Apply")
        if self.train.PID_lock_flag:
            self.apply_vals.setDisabled(True)
        self.apply_vals.clicked.connect(lambda: self.set_vals(self.train, float(self.KP_val.text()), float(self.KI_val.text())))
        self.train.signals.reset_gains.connect(self.reset_vals)
        self.train.signals.set_gains.connect(self.receive_set_vals)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.apply_vals.setFixedWidth(200)
        bottom_layout.addWidget(self.apply_vals)
        bottom_layout.addStretch()

        window_layout = QVBoxLayout()
        window_layout.addLayout(val_layout)
        window_layout.addLayout(bottom_layout)
        window_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        widget = Color('light blue')
        widget.setLayout(window_layout)
        self.setCentralWidget(widget)

    def set_vals(self, train: TrainController, Kp: float, Ki: float):
        train.set_PID_gains(Kp=Kp, Ki=Ki)
        self.apply_vals.setDisabled(True)
        self.KP_val.setStyleSheet("background-color: rgb(217,217,217)")
        self.KI_val.setStyleSheet("background-color: rgb(217,217,217)")
        self.KI_val.setReadOnly(True)
        self.KP_val.setReadOnly(True)

    def receive_set_vals(self):
        self.apply_vals.setDisabled(True)
        self.KI_val.setText(str(self.train.Ki))
        self.KP_val.setText(str(self.train.Kp))
        self.KP_val.setStyleSheet("background-color: rgb(217,217,217)")
        self.KI_val.setStyleSheet("background-color: rgb(217,217,217)")
        self.KI_val.setReadOnly(True)
        self.KP_val.setReadOnly(True)


    def __del__(self):
        print(f"[TRAIN]: Train Controller Engineer Window deleted.")

    def reset_vals(self):
        self.apply_vals.setEnabled(True)
        self.KI_val.setReadOnly(False)
        self.KP_val.setReadOnly(False)
        self.KP_val.setStyleSheet("background-color: white")
        self.KI_val.setStyleSheet("background-color: white")


