"""Copyright (c) 2020, Josh Ball of Flowstate Creative Solutions."""

import time
import math
from pynput import keyboard
from consts import *

ignore = False
ignore_counter = 0
keyb = keyboard.Controller()
mods = "000000000000000000000"


def extract_sysex(keys):
    print(keys)
    global ignore, ignore_counter, mods
    
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
                    _ascii = (ord(special_converter[str(key)]))

                elif key.char and key.char in special_converter.keys():
                    _ascii = (ord(special_converter[key.char]))
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
                    _ascii = (ord(key.char))
                ascii_byte_one = math.floor(_ascii / 128)
                ascii_byte_two = _ascii % 128
                return compile(ascii_byte_one, ascii_byte_two, mods)

            except AttributeError:
                try:
                    mods = replace_str_index(mods, MODIFIERS[str(key)], '1')
                    if str(key) in FINALS:
                        return compile(0,0, mods)
                except KeyError:
                    print('KeyCode {0} not used at the present time'.format(key))

def compile(a_one, a_two, mods):
    print(mods)
    mod_one = int('0' + mods[:7], 2)
    mod_two = int('0' + mods[7:14], 2)
    mod_three = int('0' + mods[14:], 2)
    return [0xF0,0,0,0,0,0, mod_one, mod_two, mod_three, a_one, a_two, 0xF7]

def replace_str_index(text,index=0,replacement=''):
    return '%s%s%s'%(text[:index],replacement,text[index+1:])
    