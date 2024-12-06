import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint
from train.train_model.ui.main_app import Main_App
from track_model.track_model_ui import TrackModelMainWindow

def main():
    app = QApplication()
    ma = Main_App()
    # tmw = TrackModelMainWindow(ma)
    # tmw.show()
    app.exec()

if __name__ == "__main__":
    main()