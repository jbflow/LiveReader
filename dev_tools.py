""" Just some tools to aid development, just import DevTools into the python console then you can run these functions
whenever you need to do either action, makes updating the script and bug tracking much easier"""

from distutils.dir_util import copy_tree
from pathlib import Path

def read_log():
    path = '/Users/josh/Library/Preferences/Ableton/Live 11.0.12/log.txt'
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if 'RemoteScript' in line:
                print(line)

def copy_script():
    # Get the home directory and the path to the remote script locations
    home = Path.home()
    dir = f'{home}/Music/Ableton/User Library/Remote Scripts'
    script = f'{dir}/MIDI Remote Script'
    # overwrite the script
    copy_tree('MIDI Remote Script', script)

