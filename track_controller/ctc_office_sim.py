
from PySide6.QtCore import Signal, QObject
from track_controller.wayside_controller_backend import *
class CTCOffice(QObject):
    train_info_sig = Signal(list)
    def __init__(self):
        self.train_info = [3,45,15]
        self.sw_pos_list = [[5,1]]
        #self.train_info_sig.connect(self.send_train_info)

#ctc = CTCOffice()