from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

def create_button(label) -> QVBoxLayout:
    button_layout = QVBoxLayout()
    button = QPushButton(label)
    button_layout.addWidget(button)
    # button_layout.addWidget(label)
    return button_layout


def create_line_edit(label) -> QVBoxLayout:
    line_edit_layout = QVBoxLayout()
    label = QLabel(label)
    label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    lineEdit = QLineEdit()
    line_edit_layout.addWidget(lineEdit)
    line_edit_layout.addWidget(label)
    return line_edit_layout