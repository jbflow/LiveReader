"""A function for converting keyboard presses into a MIDI SysEx message."""

import time
import math
from pynput import keyboard
from consts import *

ignore = False
ignore_counter = 0
keyb = keyboard.Controller()


def extract_sysex(keys):
    MESSAGE = [0xF0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xF7]
    global ignore, ignore_counter
    if ignore and ignore_counter < 2:
        ignore_counter += 1
        return
    elif ignore:
        ignore = False
        ignore_counter = 0
        return
    else:
        for key in keys:
            try:
                if str(key) in special_converter.keys():
                    ASCII = (ord(special_converter[str(key)]))

                elif key.char in special_converter.keys():
                    ASCII = (ord(special_converter[key.char]))
                else:
                    if key.char == '7':
                        ignore = True
                        time.sleep(0.1)
                        with keyb.pressed(keyboard.Key.shift):
                            keyb.press(keyboard.Key.tab)
                            keyb.release(keyboard.Key.tab)
                            time.sleep(0.05)
                            keyb.press(keyboard.Key.tab)
                            keyb.release(keyboard.Key.tab)
                    ASCII = (ord(key.char))
                MESSAGE[22] = math.floor(ASCII / 128)
                MESSAGE[23] = ASCII % 128
                return MESSAGE

            except AttributeError:
                try:
                    MESSAGE[MODIFIERS[str(key)]] = 1
                    if str(key) in FINALS:
                        return MESSAGE
                except KeyError:
                    print('KeyCode {0} not used at the present time'.format(key))
