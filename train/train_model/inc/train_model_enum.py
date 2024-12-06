from enum import Enum

class Door(Enum):
    CLOSE = 0
    OPEN = 1

class Lights(Enum):
    OFF = 0
    ON = 1

class Unit(Enum):
    IMPERIAL = 0
    METRIC = 1

class Air_Conditioning(Enum):
    OFF = 0
    ON = 1

class Controller_Mode(Enum):
    MANUAL = 0
    AUTO = 1
