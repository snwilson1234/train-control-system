from god import *
import unittest
import subprocess
import atexit

class TestTrackController(unittest.TestCase):

    def setUp(cls) -> None:
        cls.green_line_system = TrackControllerSystem("GREEN_LINE")
        cls.green_line_system.create_waysides()

    
    def test_receive_block_status(self):
        self.assertEqual(self.green_line_system.controller_list[0].var_list[4][26:], '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]')

        self.green_line_system.controller_list[0].set_block([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        self.assertEqual(self.green_line_system.controller_list[0].var_list[4][26:], '[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]')


    def test_track_controller_updates_unsafe_speed(self):
        self.assertEqual(self.green_line_system.controller_list[0].var_list[1][18],'0')
        self.green_line_system.controller_list[0].set_block_speed_auth(5,30,13)#limit is 20m/s

        self.green_line_system.run_waysides_one_step()
        self.assertEqual(self.green_line_system.controller_list[0].fun_out[10].elements[1].value,0)


def run_cleanup():
    subprocess.run(["python","clean_up.py"])

if __name__ == "__main__":
    atexit.register(run_cleanup)
    unittest.main()