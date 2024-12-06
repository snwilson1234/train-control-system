from train.train_model.ui.ui_help import *

class Test_Windows(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Train Model Test Bench")

        self.test_tabs = QTabWidget()
        self.test_tabs.setTabPosition(QTabWidget.West)
        self.test_tabs.setMovable(False)
        self.test_tabs.setTabShape(QTabWidget.TabShape.Rounded)
        self.setCentralWidget(self.test_tabs)
        self.tab_index_offset = 0

    def add_non_train_tab(self, widget : QWidget,  tab_name : str) -> None:
        self.tab_index_offset += 1
        self.test_tabs.addTab(widget, tab_name)

    def add_tab(self,widget : QWidget, tab_name : str) -> None:
        self.test_tabs.addTab(widget, tab_name) 

    def remove_tab(self, idx: int) -> None:
        self.test_tabs.widget(idx + self.tab_index_offset).deleteLater()
        self.test_tabs.removeTab(idx + self.tab_index_offset)

    def set_current_tab(self, idx: int) -> None:
        self.test_tabs.setCurrentIndex(idx + self.tab_index_offset)