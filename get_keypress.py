"""This script is used to get the currently pressed keys, it loads the keys_pressed object - this should always be an instance of StoreKeys Class. 
it then updates its keys property with a list of currently pressed keys, in this way whenever a key is pressed, the registered observers are notified. 
Copyright (c) 2020, Josh Ball of Flowstate Creative Solutions."""

from pynput import keyboard
from StoreKeys import keys_pressed

pressed = []


def on_press(key):
    if key not in pressed:
        pressed.append(key)
        keys_pressed.keys = pressed


def on_release(key):
    if key in pressed:
        pressed.remove(key)
        keys_pressed.keys = pressed


listener = keyboard.Listener(on_press=on_press, on_release=on_release)


def stop():
    global listener
    listener.stop()


def start():
    global listener
    listener.start()
