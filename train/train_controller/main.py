import sys

from PySide6.QtWidgets import QApplication
sys.path.append('.')

from train.train_controller import *
from train.train_controller.driver_window import DriverWindow
from train.train_controller.test_window import TestBenchWindow
from train.train_controller.train_controller_class import TrainController
from train.train_controller.train_engineer_ui import TrainEngineerWindow


def main():
    app = QApplication(sys.argv)
    train = TrainController()
    window = DriverWindow(train)
    test_window = TestBenchWindow(train)
    # TODO: fix why this won't work? no need to call specific windows??
    window.show()

    engineer_window = TrainEngineerWindow(train)
    test_window.show()
    engineer_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
