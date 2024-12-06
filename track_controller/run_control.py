# from vpython.no_notebook import stop_server
import keyboard
from sys import exit
import os
import signal

# https://github.com/BruceSherwood/vpython-jupyter/issues/36

def monitor_terminate():
    if keyboard.is_pressed('shift+q'):    
        print("[TRACK CONTROLLER]: Exit function triggered. Sending the kill signal.")
        # stop_server() # this didn't work for me, hangs on this function usually
        # print("[TRACK CONTROLLER]: Server stopped.")
        os.kill(os.getpid(), signal.SIGINT)
        exit()

def monitor_pause():
    if keyboard.is_pressed('shift+p'):
        print("[TRACK CONTROLLER]: Pause triggered.")
        while True:
            if keyboard.is_pressed('shift+r'):
                print("[TRACK CONTROLLER]: Resuming")
                return
            if keyboard.is_pressed('shift+q'):
                print("[TRACK CONTROLLER]: Exit function triggered. Sending the kill signal.")
                os.kill(os.getpid(), signal.SIGINT)
                exit()

def monitor_loop():
    monitor_pause()
    monitor_terminate()

def kill():
    os.kill(os.getpid(), signal.SIGINT)
    exit()