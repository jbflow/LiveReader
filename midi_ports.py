"""Creation of Virtual MIDI ports on MacOS using rtmidi package"""

import rtmidi
import speak_text
import active_window
from StoreKeys import keys_pressed
import keys_to_midi
from speak_text import Speak

midi_out = rtmidi.MidiOut()
midi_in = rtmidi.MidiIn()
midi_in.ignore_types(sysex=False)

push_in = rtmidi.MidiIn()
push_in.ignore_types(sysex=False)

speech = Speak()

def _parse_midi(*midi):
    for m in midi:
        if m and m[0][0] == 240:
            sysex = m[0]
            text = ''.join([chr(o) for o in sysex[1:-1]])
            if text:
                print(text)
                speech.kill_process()
                speech.speak_text(text)


def _forward_presses(pressed_keys):
    if active_window.is_live():
        message = keys_to_midi.extract_sysex(pressed_keys)
        if message:
            print(message)
            midi_out.send_message(message)

def init_push(*args):
    if args[0][0] == [240, 0, 33, 29, 1, 1, 10, 0, 247]:
        midi_out.send_message(args[0][0])


def clean_up():
    if midi_in.is_port_open():
        midi_in.close_port()
    if midi_out.is_port_open():
        midi_out.close_port()
    keys_pressed.unregister_callback(_forward_presses)


def open():
    midi_in.open_virtual_port('MIDI Remote Script')
    midi_out.open_virtual_port('MIDI Remote Script')
    keys_pressed.register_callback(_forward_presses)
    midi_in.set_callback(_parse_midi)
    try:
        push_index = push_in.get_ports().index("Ableton Push 2 Live Port")
        push_in.open_port(push_index)
        push_in.set_callback(init_push)
    except IndexError:
        pass

if __name__ == '__main__':
    open()
    clean_up()
