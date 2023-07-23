import Live
import math
import time
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from .key_consts import *
from .consts import *


def convert_to_note(pitch):
    octave = int(pitch / 12) - 2
    note = pitch % 12
    return '{0}{1}'.format(NOTES[note], octave)


def note_changed(original_notes, new_notes):
    difference = tuple(set(original_notes) ^ set(new_notes))
    if len(difference) >= 2:
        original = difference[0] if difference[0] in original_notes else difference[1]
        new = difference[1] if difference[1] in new_notes else difference[0]
        attr = [i for i, (o, n) in enumerate(zip(original, new)) if o != n][0]
        return 'note {0} changed to {1}'.format(ATTR[attr], new[attr])


class ClipActions(ControlSurfaceComponent):
    __module__ = __name__

    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)

        self._c_instance = c_instance
        self.clip = None
        self.position = 0.0
        self.q_index = 7
        self.length = 0.0
        self.start = 0.0
        self.end = 0.0
        self.loop = 0
        self.notes = None
        self.bars = None
        self.beats = None
        self.sixteenths = None
        self.pitch_fb = True
        self.pos_fb = False
        self.length_fb = False
        self.vel_fb = False
        self.end_at_pos = []
        self.start_at_pos = []
        self.snap_back = None
        self.snap_fore = None
        self.last_note = None
        self.selected_note_index = None
        self.select_end = None
        self.select_start = None
        self.selected_notes = None

        self.actions = {
            UP_ARROW: self.up_arrow,
            DOWN_ARROW: self.down_arrow,
            LEFT_ARROW: self.left_arrow,
            RIGHT_ARROW: self.right_arrow,
            ALT_UP: self.alt_up,
            ALT_DOWN: self.alt_down,
            ALT_LEFT: self.alt_left,
            ALT_RIGHT: self.alt_right,
            SHIFT: self.selecting,
            SHIFT_LEFT: self.selecting_left,
            SHIFT_RIGHT: self.selecting_right,
            SQR_BRACKET_OPEN: self.quant_down,
            SQR_BRACKET_CLOSED: self.quant_up,
            SEMI_COLON: self.loop_on_off,
            APOSTROPHE: self.decrease_length,
            BACKSLASH: self.increase_length,
            COMMA: self.pitch_fb_on,
            PERIOD: self.vel_fb_on,
            ALT_COMMA: self.pos_fb_on,
            ALT_PERIOD: self.len_fb_on,
            FORWARDSLASH: self.report_pos,
            ALT_FORWARDSLASH: self.report_prox_notes,
            ALT_SEMI_COLON: self.duplicate_loop,
            ALT_APOSTROPHE: self.deselect_notes,
            ALT_BACKSLASH: self.select_region,
            CMD_A: self.select_all_notes
        }

    def log(self, msg):
        self._c_instance.log_message(str(msg))

    def send_midi(self, text):
        sys_text = tuple([240] + [ord(c) for c in text] + [247])
        self._c_instance.send_midi(sys_text)
        self._c_instance.show_message(text)

    def get_action(self, midi_bytes):
        if midi_bytes in self.actions.keys():
            return self.actions[midi_bytes]()
        else:
            if midi_bytes[19] == 1:
                self.left_arrow()
            elif midi_bytes[20] == 1:
                self.right_arrow()

    def get_highlighted_clip(self):
        if self.song().view.detail_clip:
            self.clip = self.song().view.detail_clip
            self.start = self.clip.start_marker
            self.end = self.clip.end_marker
            self.length = self.clip.length
            self.q_index = 2
            self.clip.view.grid_quantization = QUANT_VALUES[self.q_index]
            self.position = self.make_pos_zero()
            self.notes = self.clip.get_notes(float(self.start), 0, float(self.clip.length), 128)
            if not self.clip.notes_has_listener(self.update_notes):
                self.clip.add_notes_listener(self.update_notes)1

            return True
        else:
            return False

    def make_pos_zero(self):

        self.clip.set_notes(((0, 0.0, 0.1, 0, 0),))
        self.clip.remove_notes(0.0, 0, 0.1, 1)
        self.clip.deselect_all_notes()
        return 0.0

    def convert_beat_time(self, beat_time):

        beats_per_bar = 4
        musical_beats_per_beat = 1
        if beat_time >= 0:
            bars = 1 + int(beat_time / beats_per_bar)
        else:
            bars = int(beat_time / beats_per_bar) if beat_time % beats_per_bar == 0 else int(
                beat_time / beats_per_bar) - 1
        beats = 1 + int(beat_time % beats_per_bar * musical_beats_per_beat)
        sixteenths = 1 + int(beat_time % (1.0 / musical_beats_per_beat) * 4.0)
        if bars != self.bars:
            self.bars = bars
            yield 'bar {0}'.format(bars)
        if beats != self.beats:
            self.beats = beats
            yield 'beat {0}'.format(beats)
        if sixteenths != self.sixteenths:
            self.sixteenths = sixteenths
            yield 'sixteenth {0}'.format(sixteenths)
        return

    def update_notes(self):
        time.sleep(0.1)
        if self.length != self.clip.length:
            self.length = self.clip.length
            return
        message = ''
        new_notes = self.clip.get_notes(float(self.start), 0, float(self.length), 128)
        if len(new_notes) > len(self.notes):
            action = ' added'
        elif len(new_notes) < len(self.notes):
            action = ' removed'
        elif len(new_notes) == len(self.notes):
            message += note_changed(self.notes, new_notes)
            self.send_midi(message)
            self.notes = new_notes
            return
        note = tuple(set(new_notes) ^ set(self.notes))

        if note != ():
            pitch = note[0][0]
            pos = note[0][1]
            length = note[0][2]
            vel = note[0][3]
            note_name = convert_to_note(pitch)
            if self.pitch_fb:
                message += 'note {0}'.format(note_name)
            if self.pos_fb:
                message += ', position {0}'.format(pos)
            if self.length_fb:
                message += ', length {0}'.format(length)
            if self.vel_fb:
                message += ', velocity {0}'.format(vel)
            message += action
        self.send_midi(message)
        self.notes = new_notes

    def update_surrounding_notes(self):
        self.last_note = None
        self.end_at_pos = []
        self.start_at_pos = []
        nearest_start = None
        nearest_end = float('inf')
        end_of_notes = []
        start_of_notes = []

        for note in self.notes:
            if note[1] + note[2] == self.position:
                self.end_at_pos.append(note)
                if note[1] > nearest_start:
                    nearest_start = note[1]
                self.snap_back = self.position - nearest_start

            elif note[1] == self.position:
                self.start_at_pos.append(note)
                if note[1] + note[2] < nearest_end:
                    nearest_end = note[1] + note[2]
                self.snap_fore = nearest_end - self.position
            elif note[1] + note[2] < self.position:
                end_of_notes.append(note[1] + note[2])
            elif note[1] > self.position:
                start_of_notes.append(note[1])
            elif note[1] < self.position < note[1] + note[2]:
                self.snap_fore = note[1] + note[2] - self.position
                self.snap_back = self.position - note[1]
            if not self.end_at_pos and end_of_notes:
                closest_note_back = min(end_of_notes, key=lambda x: abs(x - self.position))
                self.snap_back = self.position - closest_note_back
            if not self.start_at_pos and start_of_notes:
                closest_note_forward = min(start_of_notes, key=lambda x: abs(x - self.position))
                self.snap_fore = closest_note_forward - self.position

            if note[1] + note[2] > self.last_note:
                self.last_note = note[1] + note[2]

    def up_arrow(self):
        final_time = []
        selected_notes = self.clip.get_selected_notes()
        if self.position == self.last_note and selected_notes == ():
            return 'position at end of last note'
        self.position += self.snap_fore
        self.update_surrounding_notes()
        if selected_notes == ():
            for t in self.convert_beat_time(self.position):
                final_time.append(t)
            return ' '.join(final_time)

    def down_arrow(self):
        final_time = []
        selected_notes = self.clip.get_selected_notes()
        if self.position == self.start and selected_notes == ():
            return 'position at start of first note'
        self.position -= self.snap_back
        self.update_surrounding_notes()
        if selected_notes == ():
            for t in self.convert_beat_time(self.position):
                final_time.append(t)
            return ' '.join(final_time)

    def left_arrow(self):
        final_time = []
        quant = QUANT_BEATS[self.q_index]
        if self.position > 0.0:
            self.position -= quant
            self.position = quant * math.ceil(self.position / quant)
            self.update_surrounding_notes()
            if self.clip.get_selected_notes() == ():
                for t in self.convert_beat_time(self.position):
                    final_time.append(t)
                return ' '.join(final_time)

    def right_arrow(self):
        final_time = []
        quant = QUANT_BEATS[self.q_index]
        if self.position < self.clip.end_marker:
            self.position += QUANT_BEATS[self.q_index]
            self.position = quant * math.floor(self.position / quant)

            self.update_surrounding_notes()
            if self.clip.get_selected_notes() == ():
                for t in self.convert_beat_time(self.position):
                    final_time.append(t)
                return ' '.join(final_time)

    def quant_down(self):
        if self.clip:
            self.q_index -= 1
            self.clip.view.grid_quantization = QUANT_VALUES[self.q_index]
            return 'quantization {0}'.format(QUANT_NAMES[self.q_index])

    def quant_up(self):
        if self.clip:
            self.q_index += 1
            self.clip.view.grid_quantization = QUANT_VALUES[self.q_index]
            return 'quantization {0}'.format(QUANT_NAMES[self.q_index])

    def loop_on_off(self):
        if self.clip:
            loop = {0: 'off',
                    1: 'on'}
            self.clip.looping = 1 if self.clip.looping == 0 else 0
            return 'looping {0}'.format(loop[self.clip.looping])

    def decrease_length(self):
        if self.clip:
            self.clip.end_marker -= QUANT_BEATS[self.q_index]
            self.clip.loop_end -= QUANT_BEATS[self.q_index]
            self.length = self.clip.length
            return 'clip length {0} beats'.format(self.clip.end_marker)

    def increase_length(self):
        if self.clip:
            self.clip.end_marker += QUANT_BEATS[self.q_index]
            self.clip.loop_end += QUANT_BEATS[self.q_index]
            self.length = self.clip.length
            return 'clip length {0} beats'.format(self.clip.end_marker)

    def pitch_fb_on(self):
        self.pitch_fb = False if self.pitch_fb else True
        state = 'On' if self.pitch_fb is True else 'Off'
        return 'pitch feedback {0}'.format(state)

    def vel_fb_on(self):
        self.vel_fb = False if self.vel_fb else True
        state = 'On' if self.vel_fb is True else 'Off'
        return 'velocity feedback {0}'.format(state)

    def pos_fb_on(self):
        self.pos_fb = False if self.pos_fb else True
        state = 'On' if self.pos_fb is True else 'Off'
        return 'position feedback {0}'.format(state)

    def len_fb_on(self):
        self.length_fb = False if self.length_fb else True
        state = 'On' if self.length_fb is True else 'Off'
        return 'length feedback {0}'.format(state)

    def report_prox_notes(self):
        pass

    def report_pos(self):
        return 'insert marker at {0}'.format(self.position)

    def duplicate_loop(self):
        self.clip.duplicate_loop()
        self.length = self.clip.length
        self.start = self.clip.start_marker
        self.end = self.clip.end_marker
        return 'loop duplicated, new length {0} bars'.format(self.length / 4)

    def deselect_notes(self):
        self.clip.deselect_all_notes()
        self.position = self.make_pos_zero()

        return 'notes deselected and position reset to zero'

    def alt_up(self):
        return self.get_selected_note()

    def alt_down(self):
        return self.get_selected_note()

    def alt_left(self):
        return self.get_selected_note()

    def alt_right(self):
        return self.get_selected_note()

    def get_selected_note(self):
        note = self.clip.get_selected_notes()
        if not note:
            notes = self.clip.get_notes(float(self.start), 0, float(self.length), 128)
            note = (notes[0])
            self.clip.set_notes((note,))
            return self.get_note_info(note)
        if note:
            return self.get_note_info(note[0])

    def get_note_info(self, note):
        message = ''
        pitch = note[0]
        pos = note[1]
        length = note[3]
        note_name = convert_to_note(pitch)
        if self.pitch_fb:
            message += 'note {0}'.format(note_name)
        if self.pos_fb:
            message += ', position {0}'.format(pos)
        if self.length_fb:
            message += ', length {0}'.format(length)
        if self.vel_fb:
            message += ', velocity {0}'.format(vel)
        return message

    def select_all_notes(self):
        return 'all notes selected'

    def select_region(self):
        pass

    #     self.selected_notes = self.clip.get_notes(self.select_start, 0, self.select_end, 128)
    #     count = len(self.selected_notes)
    #     self.clip.set_notes(self.selected_notes)
    #     return '{0} notes in highlighted region selected'.format(count)
    #
    def selecting(self):
        pass

    #     if self.clip.get_selected_notes() == ():
    #         if self.select_end == self.position:
    #             return 'extending highlighted region {0} to {1}'.format(self.select_start, self.select.end)
    #         self.select_start = self.position
    #         return 'highlighting from {0}'.format(self.position)
    #
    def selecting_right(self):
        pass

    #     self.right_arrow()
    #     self.select_end = self.position
    #     return 'highlighted {0} to {1}'.format(self.select_start, self.select_end)
    #
    def selecting_left(self):
        pass
    #     self.left_arrow()
    #     if self.position == self.select_start:
    #         self.select_start = None
    #         self.select_end = None
    #         return 'unselected'
    #     self.select_end = self.position
    #     return 'highlighted {0} to {1}'.format(self.select_start, self.select_end)
