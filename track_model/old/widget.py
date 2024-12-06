# This Python file uses the following encoding: utf-8
import sys
import sqlite3
import csv

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Slot

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.ui.importButton.clicked.connect(say_hello)

@Slot()
def say_hello():
    print("[TRACK MODEL]: Button clicked, Hello!")

# def init_db() -> sqlite3.Connection:
#     con = sqlite3.connect("track.db")
#     cur = con.cursor()
#     cur.execute("CREATE TABLE track(Line, Section, Number, Length, Grade, Speed, Infrastructure);")
#     return con

# def import_track():
#     con = sqlite3.connect("track.db")
#     cur = con.cursor()
#     cur.execute("CREATE TABLE IF NOT EXISTS track(Line, Section, Number, Length, Grade, Speed, Infrastructure);")
#     with open('track_db.csv','r') as fin: # `with` statement available in 2.5+
#         # csv.DictReader uses first line in file for column headings by default
#         dr = csv.DictReader(fin) # comma is default delimiter
#         to_db = [(i['Line'], i['Section'], i['Number'], i['Length'], i['Grade'], i['Speed'], i['Infrastructure']) for i in dr]
#     cur.executemany("INSERT INTO track (Line, Section, Number, Length, Grade, Speed, Infrastructure) VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
#     con.commit()
#     con.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    #import_track()
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
