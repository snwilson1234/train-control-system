from train.train_model.ui.ui_help import *

class Train_Specs_Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Train Specs")

        def create_label(text: str, font: QFont='None', color: str='black') -> QLabel:
            label = QLabel(text)
            if font is not None:
                label.setFont(font)
            # label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            style = "color: " + color
            label.setStyleSheet(style)
            return label
        
        self.unit_toggle = AnimatedToggle()
        self.unit_toggle.setFixedWidth(80)
        self.unit_toggle.setCheckState(Qt.CheckState.Checked)
        imperial_label = QLabel("IMPERIAL")
        imperial_label.setFont(Fonts.subsection_font)
        metric_label = QLabel("METRIC")
        metric_label.setFont(Fonts.subsection_font)

        units_layout = QHBoxLayout()
        units_layout.addWidget(imperial_label)
        units_layout.addWidget(self.unit_toggle)
        units_layout.addWidget(metric_label)
        units_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)


        layout = QVBoxLayout()
        font = Fonts.subsection_font

        self.height_label = create_label("Height: 3.42 m", font)
        self.length_label = create_label("Length: 32.2 m", font)
        self.width_label = create_label("Width: 2.65 m", font)
        self.mass_unloaded_label = create_label("Mass (unloaded): 40900 kg", font)
        self.mass_loaded_label = create_label("Mass (max load): 56700 kg", font)


        # layout.addWidget(create_label("", font))
        layout.addWidget(self.height_label)
        layout.addWidget(self.length_label)
        layout.addWidget(self.width_label)
        layout.addWidget(create_label("Number of Train Cars: 5", font))
        layout.addWidget(create_label("", font))
        layout.addWidget(self.mass_unloaded_label)
        layout.addWidget(self.mass_loaded_label)
        layout.addWidget(create_label("", font))
        layout.addWidget(create_label("Max Acceleration: 0.5 m/s", font))
        layout.addWidget(create_label("Braking Deceleration: 1.2 m/s", font))
        layout.addWidget(create_label("Emergency Brake Deceleration: 2.73 m/s", font))
        layout.addWidget(create_label("", font))
        layout.addLayout(units_layout)

        # layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        widget = Color('white')
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.unit_toggle.stateChanged.connect(self.update_units)


        

    def update_units(self, state) -> None:
        if state == Qt.CheckState.Checked.value:
            # Metric
            self.height_label.setText("Height: 3.42 m")
            self.length_label.setText("Length: 32.2 m")
            self.width_label.setText("Width: 2.65 m")
            self.mass_unloaded_label.setText("Mass (unloaded): 40900 kg")
            self.mass_loaded_label.setText("Mass (max load): 56700 kg")
        else:
            # Imperial
            self.height_label.setText("Height: 11.22 ft")
            self.length_label.setText("Length: 105.643 ft")
            self.width_label.setText("Width: 8.694 ft")
            self.mass_unloaded_label.setText("Mass (unloaded): 90169 lbs")
            self.mass_loaded_label.setText("Mass (max load): 125002 lbs")


