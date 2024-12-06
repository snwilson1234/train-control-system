from PySide6.QtWidgets import QApplication
from track_model.track_model_ui import TrackModelMainWindow
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)

    tm = TrackModelMainWindow()
    tm.show()
    
    sys.exit(app.exec())