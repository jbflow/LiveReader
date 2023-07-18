"""This script is for copying the remote scripts folder to the correct place, it will only
work if the Ableton User Library is contained in the default location of the Music folder. It checks the version of the
remote script and upates it as necessary."""


import os
from distutils.dir_util import copy_tree
from pathlib import Path


def copy():
    # Get the home directory and the path to the remote script locations
    home = Path.home()
    dir = r'{0}/Music/Ableton/User Library/Remote Scripts'.format(home)
    script = '{0}/LiveReader'.format(dir)
    # Create if it doesn't exist
    if not os.path.exists(script):
        os.makedirs(dir)
        copy_tree('LiveReader', script)







