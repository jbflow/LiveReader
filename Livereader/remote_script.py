"""This script is for copying the remote scripts folder to the correct place, it will only
work if the Ableton User Library is contained in the default location of the Music folder."""

import os, sys
from distutils.dir_util import copy_tree
from pathlib import Path

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()


def copy():
    # Get the home directory and the path to the remote script locations
    home = Path.home()
    dir = f'{home}/Music/Ableton/User Library/Remote Scripts'
    script = f'{dir}/LiveReader'
    # Create if it doesn't exist
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not os.path.exists(script):
        copy_tree(f'{wd}/MIDI Remote Script', script)
