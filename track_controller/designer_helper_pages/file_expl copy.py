
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(130, 20, 561, 491))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtin_import_file = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget)
        self.txtin_import_file.setObjectName("txtin_import_file")
        self.horizontalLayout.addWidget(self.txtin_import_file)
        self.btn_import_file = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.btn_import_file.setObjectName("btn_import_file")
        self.btn_import_file.clicked.connect(self.open_file_explorer)
        self.horizontalLayout.addWidget(self.btn_import_file)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_import_file.setText(_translate("MainWindow", "Import"))
        self.pushButton.setText(_translate("MainWindow", "back"))
        

    #opens file explorer of directory entered in file_path
    def open_file_explorer(self):
        #MainWindow.setWindowTitle("test")
        file_path = '<directory>'
        url = QUrl.fromLocalFile(file_path)
       
        if QDesktopServices.openUrl(url):
            print("[TRACK CONTROLLER]: success")
        else:
            print("[TRACK CONTROLLER]: failure")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
