"""This script was written by Josh Ball of Flowstate Creative Solutions, Copyright 2020, on an improved BSD License"""

from AppKit import NSWorkspace

def is_live():  # method to get the active window name as in the title bar
    active_window_name = (NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    return True if active_window_name == 'Live' else False

def get_active():
    return NSWorkspace.sharedWorkspace().activeApplication()