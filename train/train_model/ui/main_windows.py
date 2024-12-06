from train.train_model.ui.ui_help import *

class Main_Windows(QMainWindow):
    def __init__(self, window_name : str) -> None:
        super().__init__()

        self.setWindowTitle(window_name)

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
    