"""A series of actions MIDI Remote Script takes on startup, for monitoring log file, registering key_press callbacks"""

import os
import time
from datetime import datetime
from pathlib import Path
import psutil
import shutil

from StoreKeys import keys_pressed
from prelisten import turn_on_prelisten

import speak_text



# First we need to get all the paths needed to manage to log file
home = str(Path.home())
dir = '{0}/Library/Preferences/Ableton/'.format(home)
livereader = '{0}/Library/Preferences/livereader/logs'.format(home)
if not os.path.exists(livereader):
    os.makedirs(livereader)
paths = sorted(Path(dir).iterdir(), key=os.path.getmtime)

# TODO: Find a better method of getting the most recent version of Live so manual update is not needed
path = r'{0}/Log.txt'.format(''.join([str(p) for p in paths if '10.1.17' in str(p)]))
start_up_successful = False

# Used for displaying and navigating pop ups on start up, the first 3 words are used for the pop up to load the correct
# List for the buttons needed, this seems to be enough. The two most common dialogs are included.
load_messages = {
    'Live unexpectedly quit': ['Yes', 'No'],
    'Audio is disabled.': ['OK']
}
navigation_keys = {'Key.left': -1,
            'Key.right': 1
            }
selected_button = 0
buttons = None


def live_is_running():
    for p in psutil.process_iter():
        try:
            if p.name() == 'Live':
                return True
        except psutil.ZombieProcess:
            continue


def _log_exists():
    global path
    return True if os.path.isfile(path) else False


def _read_log_file():
    """This function reads the log file, it also contains a keypress forwarding callback function and registers it with
    an instance of the StoreKeys Class if it detects a message box during load, and therefore the key presses need to be monitored. Once
    load is complete, it updates the variable start_up_successful"""

    global path, start_up_successful, buttons
    f = open(path, 'r')
    while True:
        line = f.readline()
        if 'Message Box:' in line:
            log_running = False
            message = line.split('Message Box: ', 1)[1]
            shortened = ' '.join(message.split()[:3])
            speak_text.speak_text('{0} {1} selected'.format(message, load_messages[shortened][0]))
            buttons = load_messages[shortened]

            def forward_presses(new_keys):
                """Create the nested callback, it only expects a single key press, and uses it to navigate the dialog box
                using the variables defined for this at the start of the script. Or select the button currently selected"""
                nonlocal log_running
                if new_keys:
                    key = str(new_keys[0])
                    if key in navigation_keys.keys():
                        _navigate_dialog(navigation_keys[key])
                    elif key in ['Key.enter', 'Key.space']:
                        speak_text.speak_text('{0} pressed'.format(buttons[selected_button]))

                        log_running = True # This unpauses the script when either of the above keys are pressed


            keys_pressed.register_callback(forward_presses) # We register the callback here
            while not log_running:
                time.sleep(0.1) # pause the script here when a dialog comes up
            keys_pressed.unregister_callback(forward_presses) # In this case, unregister the callback.


        if "Performance: Startup hook 'EnableMidiRemoteScriptManager':" in line: # When this substring is found in the Log file the script has initialized, so startup is succesfull
            start_up_successful = True
            return
        time.sleep(0.01)


def _navigate_dialog(key):
    """This function navigates the dialog, it updates the selected_button, and allows it to loop around, it also speaks
    the selected button"""
    global buttons, selected_button, load_messages
    selected_button += key
    selected_button = len(buttons) - 1 if selected_button == -1 else selected_button
    selected_button = 0 if selected_button == len(buttons) else selected_button

    speak_text.speak_text(buttons[selected_button])

def _move_log_file():
    """This moves the log file, and time/date stamps it. This enables us to search a new log file at each load - it should also help with testing."""
    date = datetime.now()
    shutil.move(path, '{0}/Ableton-Live-Log-{1}.txt'.format(livereader, date))


def wait_for_close():
    while True:
        global start_up_successful
        if not live_is_running() and _log_exists():  # True after close
            start_up_successful = False
            _move_log_file()
            turn_on_prelisten()
            break
        time.sleep(1)
    wait_for_start()

def wait_for_start():
    if not live_is_running() and _log_exists():
        _move_log_file()
    global start_up_successful
    while True:
        if live_is_running() and _log_exists() and not start_up_successful: # True on startup
            _read_log_file()
        elif start_up_successful: # True once start up has finished
            break
        time.sleep(0.1)
    wait_for_close()


