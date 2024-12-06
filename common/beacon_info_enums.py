from enum import Enum


class StationList(Enum):
    SHADYSIDE = 'Shadyside'
    HERRONAVE = 'Herron Ave'
    SWISSVILLE = 'Swissville'
    PENNSTATION = 'Penn Station'
    STEELPLAZA = 'Steel Plaza'
    FIRSTAVE = 'First Ave'
    STATIONSQUARE = 'Station Square'
    SOUTHHILLSJUNCTION = 'South Hills Junction'
    PIONEER = 'Pioneer'
    EDGEBROOK = 'Edgebrook'
    PNCPARK = 'PNC Park'     # question asked in piazza, answer tbd
    WHITED = 'Whited'
    SOUTHBANK = 'South Bank'
    CENTRAL = 'Central'
    INGLEWOOD = 'Inglewood'
    OVERBROOK = 'Overbrook'
    GLENBURY = 'Glenbury'
    DORMONT = 'Dormont'
    MTLEBANON = 'Mt Lebanon'
    POPLAR = 'Poplar'
    CASTLESHANNON = 'Castle Shannon'
    B = 'B'
    C = 'C'


    @classmethod
    def asList(cls):
        return [cls.SHADYSIDE, cls.HERRONAVE, cls.SWISSVILLE, cls.PENNSTATION, cls.STEELPLAZA,
                cls.FIRSTAVE, cls.STATIONSQUARE, cls.SOUTHHILLSJUNCTION, cls.PIONEER,
                cls.EDGEBROOK, cls.TBD, cls.WHITED, cls.SOUTHBANK, cls.CENTRAL, cls.INGLEWOOD,
                cls.OVERBROOK, cls.GLENBURY, cls.GLENBURY, cls.DORMONT, cls.MTLEBANON, cls.POPLAR, cls.CASTLESHANNON, cls.B, cls.C]

    @classmethod
    def asValues(cls):
        return [cls.SHADYSIDE.value, cls.HERRONAVE.value, cls.SWISSVILLE.value, cls.PENNSTATION.value, cls.STEELPLAZA.value,
                cls.FIRSTAVE.value, cls.STATIONSQUARE.value, cls.SOUTHHILLSJUNCTION.value, cls.PIONEER.value,
                cls.EDGEBROOK.value, cls.PNCPARK.value, cls.WHITED.value, cls.SOUTHBANK.value, cls.CENTRAL.value, cls.INGLEWOOD.value,
                cls.OVERBROOK.value, cls.GLENBURY.value, cls.GLENBURY.value, cls.DORMONT.value, cls.MTLEBANON.value,
                cls.POPLAR.value, cls.CASTLESHANNON.value, cls.B.value, cls.C.value]


class StationSide(Enum):
    OPEN_DOORS_LEFT = 'L'
    OPEN_DOORS_RIGHT = 'R'
    OPEN_ALL_DOORS = 'LR'

    @classmethod
    def asList(cls):
        return [cls.OPEN_DOORS_LEFT, cls.OPEN_DOORS_RIGHT, cls.OPEN_ALL_DOORS]

    @classmethod
    def asValues(cls):
        return [cls.OPEN_DOORS_LEFT.value, cls.OPEN_DOORS_RIGHT.value, cls.OPEN_ALL_DOORS.value]

class TunnelIncoming(Enum):
    NO_TOGGLE_LIGHTS = 0
    TOGGLE_LIGHTS = 1