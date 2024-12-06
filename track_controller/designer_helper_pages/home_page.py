from PyQt6 import QtCore, QtGui, QtWidgets


class HomePage(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("HomePage")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(230, 110, 361, 301))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.system_title = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(24)
        self.system_title.setFont(font)
        self.system_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.system_title.setObjectName("system_title")
        self.verticalLayout.addWidget(self.system_title)
        self.blue_line_buttton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.blue_line_buttton.setObjectName("blue_line_buttton")
        self.verticalLayout.addWidget(self.blue_line_buttton)
        self.red_line_button = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.red_line_button.setObjectName("red_line_button")
        self.verticalLayout.addWidget(self.red_line_button)
        self.green_line_button = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.green_line_button.setObjectName("green_line_button")
        self.verticalLayout.addWidget(self.green_line_button)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 810, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("HomePage", "HomePage"))
        self.system_title.setText(_translate("HomePage", "Track Controller System"))
        self.blue_line_buttton.setText(_translate("HomePage", "Blue Line"))
        self.red_line_button.setText(_translate("HomePage", "Red Line"))
        self.green_line_button.setText(_translate("HomePage", "Green Line"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = HomePage()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
