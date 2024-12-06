from PySide6.QtWidgets import *
from PySide6.QtCore import Qt


def create_window(label) -> QWidget:
    w = QWidget()
    w.setWindowTitle(str(label))
    return w


def create_combo_box(label, items, on_click) -> QVBoxLayout:
    mode = QVBoxLayout()
    mode_label = QLabel(label)
    mode_label.setAlignment(Qt.AlignRight)
    mode_dropdown = QComboBox()
    for i in range(len(items)):
        mode_dropdown.addItem(str(items[i]))

    mode_dropdown.currentIndexChanged.connect(lambda: on_click(mode_dropdown.currentText()))

    mode.addWidget(mode_dropdown)
    mode.addWidget(mode_label)

    return mode


def create_button(label, on_click=None) -> QPushButton:
    button = QPushButton(label)
    if on_click is not None:
        button.clicked.connect(lambda: on_click())
    return button


# UI Helper function
# @params
#   label: line caption
#   on_enter: function to occur when the line edit value changed
#   default_text: pass in the current train's speed, set to a default
# @return
#   returns the layout for the button and caption
def create_line_edit(label, on_enter=None, default_text: str = None) -> QVBoxLayout:
    line_edit_layout = QVBoxLayout()
    label = QLabel(label)
    label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    lineEdit = QLineEdit()
    if on_enter is not None:
        lineEdit.textEdited.connect(lambda: on_enter(lineEdit.text()))
    lineEdit.setText(str(default_text))
    line_edit_layout.addWidget(lineEdit)
    line_edit_layout.addWidget(label)
    return line_edit_layout


def create_line_no_edit(label, default_text: str = None) -> QVBoxLayout:
    line_no_edit_layout = QVBoxLayout()
    label = QLabel(label)
    label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    line_no_edit = QLineEdit()
    line_no_edit.setText(str(default_text))
    line_no_edit.setReadOnly(True)
    line_no_edit_layout.addWidget(line_no_edit)
    line_no_edit_layout.addWidget(label)

    return line_no_edit_layout


def create_text_no_edit(label, default_text: str = None) -> QVBoxLayout:
    line_no_edit_layout = QVBoxLayout()
    label = QLabel(label)
    label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    line_no_edit = QTextEdit()
    line_no_edit.setText(str(default_text))
    line_no_edit.setReadOnly(True)
    line_no_edit_layout.addWidget(line_no_edit)
    line_no_edit_layout.addWidget(label)

    return line_no_edit_layout
