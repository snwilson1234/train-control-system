
import unittest
import sys
from PySide6.QtWidgets import *
from track_model import TrackModel, ColorEnum

class TestTrackModel(unittest.TestCase):

    tm = TrackModel()
    track = tm.import_track('track_green.csv', ColorEnum.GREEN)

    def test_toggle_switch(self):
        if self.track:
            switch = self.tm.get_switch(ColorEnum.GREEN, 77)
            self.tm.toggle_switch(ColorEnum.GREEN, 77)
            new_switch = self.tm.get_switch(ColorEnum.GREEN, 77)
            self.assertNotEqual(switch, new_switch)

            self.tm.toggle_switch(ColorEnum.GREEN, 77)
            curr_switch = self.tm.get_switch(ColorEnum.GREEN, 77)
            self.assertEqual(switch, curr_switch)
        

if __name__ == '__main__':
    unittest.main()

