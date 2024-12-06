# TODO: change back to specific imports whether than star
from PySide6.QtCore import *

# TODO: change back to specific imports whether than star
# from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtWidgets import *

# TODO: change back to specific imports whether than star
from PySide6.QtGui import *

from train.train_model.ui.custom_widgets import AnimatedToggle,Color

class Fonts():
    # Section Font
    section_font = QFont()
    section_font.setBold(True)
    section_font.setPointSize(26)
    # Station Font
    station_font = QFont()
    station_font.setBold(True)
    station_font.setPointSize(18)
    # SubSection Font
    subsection_font = QFont()
    subsection_font.setBold(True)
    subsection_font.setPointSize(14)
    # Normal Text
    normal_font = QFont()
    normal_font.setBold(False)
    normal_font.setPointSize(10)
    # Unit Text
    unit_font = QFont()
    unit_font.setBold(False)
    unit_font.setPointSize(12)
    # Large Bold Font
    large_bold_font = QFont()
    large_bold_font.setBold(True)
    large_bold_font.setPointSize(18)
    # Top Panel Field Font
    top_panel_font = QFont()
    top_panel_font.setBold(True)
    top_panel_font.setPointSize(14)
    # Top Panel Info Font
    top_panel_NB_font = QFont()
    top_panel_NB_font.setBold(False)
    top_panel_NB_font.setPointSize(14)
    # Test UI Section Header
    tui_section_header = QFont()
    tui_section_header.setBold(False)
    tui_section_header.setPointSize(12)
    # Test UI Block Header
    tui_block_header = QFont()
    tui_block_header.setBold(True)
    tui_block_header.setPointSize(12)

class UI_Help():
    def create_label(text: str, font: QFont='None', color: str='black') -> QLabel:
        label = QLabel(text)
        if font is not None:
            label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        style = "color: " + color
        label.setStyleSheet(style)
        return label
    
    def create_QLCDNumber(val: float, digitcount : int) -> QLCDNumber:
        lcd = QLCDNumber()
        lcd.setFixedWidth(150)
        lcd.setMode(QLCDNumber.Dec)
        lcd.setDigitCount(digitcount)
        lcd.setSegmentStyle(QLCDNumber.Filled)
        lcd.display(val)
        return lcd
    
    def create_number_disp_layout(number_lcd: QLCDNumber, unit_label: QLabel, identifer_str : str ,identifier_font : QFont) -> QGridLayout:
        layout = QGridLayout()
        number_lcd.setMinimumHeight(30)
        number_lcd.setMaximumHeight(80)
        layout.addWidget(number_lcd, 0,1,1,2)
        layout.addWidget(unit_label, 0,3,1,1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(UI_Help.create_label(identifer_str, identifier_font), 1,0,1,4, Qt.AlignmentFlag.AlignTop) 
        return layout
    
    def create_frame() -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(2)
        return frame
    
    def create_input_field(field_name : str, line_edit : QLineEdit, read_only : bool=False) -> QHBoxLayout: 
        layout = QHBoxLayout()
        label = UI_Help.create_label(field_name)
        line_edit.setReadOnly(read_only)
        line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter) #sets text alignment within the field
        layout.addWidget(label)
        layout.addWidget(line_edit)
        
        return layout
    
    def create_text_edit() -> QPlainTextEdit:
        text_edit = QPlainTextEdit()
        text_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        # text_edit.setFixedHeight(80) this screws up the top alignment
        return text_edit
    
    def create_anim_btn_field(field_name : str, anim_btn : AnimatedToggle) -> QGridLayout:
        layout = QGridLayout()
        anim_btn.setFixedWidth(70)
        layout.addWidget(UI_Help.create_label(field_name, None), 0,0,1,1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(anim_btn, 0,1,1,1,Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        return layout
    
    def create_btn_field(field_name :str, btn : QPushButton) -> QGridLayout:
        layout = QGridLayout()
        layout.addWidget(UI_Help.create_label(field_name, None), 0,0,1,1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(btn, 0,0,1,1, Qt.AlignmentFlag.AlignVCenter)
        return layout
    
    def create_field(field_name : str, field_font : QFont, data_label : QLabel, alignment : Qt.AlignmentFlag) -> QHBoxLayout:
            field = QHBoxLayout()
            field.addWidget(UI_Help.create_label(field_name, field_font))
            field.addWidget(data_label)
            field.setAlignment(alignment)
            return field

        
