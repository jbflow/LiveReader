from ableton.v2.control_surface import Component
from ableton.v2.base import depends, listens
from .consts import NOTES, ATTR
import math


class ClipActions(Component):
    @depends(log_message=None, send_midi=None)
    def __init__(self, log_message, send_midi, *a, **k):
        super(ClipActions, self).__init__(*a, **k)
        self.log = log_message
        self.send_midi = send_midi
        self.loop_length = None
        self.notes = []
        self._on_detail_clip_changed.subject = self.song.view

    @listens("detail_clip")
    def _on_detail_clip_changed(self):
        self.loop_length = self.song.view.detail_clip.loop_end - self.song.view.detail_clip.loop_start
        self._on_loop_start_changed.subject = self.song.view.detail_clip
        self._on_loop_end_changed.subject = self.song.view.detail_clip
        if self.song.view.detail_clip.is_audio_clip:
            self._on_warp_mode_changed.subject = self.song.view.detail_clip
            self._on_pitch_coarse_changed.subject = self.song.view.detail_clip
            self._on_gain_changed.subject = self.song.view.detail_clip
        else:
            self._on_notes_changed.subject = self.song.view.detail_clip

    @listens("loop_start")
    def _on_loop_start_changed(self):
        bars, beats, sixteenths = self.convert_beat_time(self.song.view.detail_clip.loop_start)
        self.send_midi(f"Loop position bar {bars} beat {beats} sixteenths {sixteenths}")

    @listens("loop_end")
    def _on_loop_end_changed(self):
        loop_length = self.convert_beat_time(
            self.song.view.detail_clip.loop_end - self.song.view.detail_clip.loop_start)
        if loop_length != self.loop_length:
            self.send_midi(
                f"loop length {loop_length[0] - 1} bars {loop_length[1] - 1} beats {loop_length[2] - 1} sixteenths")
            self.loop_length = loop_length

    @listens("warp_mode")
    def _on_warp_mode_changed(self):
        available_warp_modes = self.song.view.detail_clip.available_warp_modes
        self.log(available_warp_modes)
        self.send_midi(f"Warp {available_warp_modes[self.song.view.detail_clip.warp_mode]}")

    @listens("pitch_coarse")
    def _on_pitch_coarse_changed(self):
        self.send_midi(f"Pitch coarse {self.song.view.detail_clip.pitch_coarse}")

    @listens("gain")
    def _on_gain_changed(self):
        self.send_midi(f"Gain {self.song.view.detail_clip.gain_display_string}")

    @listens("notes")
    def _on_notes_changed(self):
        message = ''
        new_notes = self.song.view.detail_clip.get_notes_extended(
            from_time=float(self.song.view.detail_clip.start_marker), from_pitch=0,
            time_span=float(self.song.view.detail_clip.length), pitch_span=128)
        self.log(new_notes)
        if len(new_notes) > len(self.notes):
            note = [note for note in new_notes if note not in self.notes][0]
            message = f'{self.convert_to_note(note.pitch)} added at {self.convert_beat_time(note.start_time)}'
        elif len(new_notes) < len(self.notes):
            note = [note for note in self.notes if note not in new_notes][0]
            message = f'{self.convert_to_note(note.pitch)} removed from {self.convert_beat_time(note.start_time)}'
        elif len(new_notes) == len(self.notes):
            message = self.note_changed(self.notes, new_notes)
        self.send_midi(message)
        self.notes = new_notes

    @staticmethod
    def convert_beat_time(beat_time):
        beats_per_bar = 4
        musical_beats_per_beat = 1
        if beat_time >= 0:
            bars = 1 + int(beat_time / beats_per_bar)
        else:
            bars = int(beat_time / beats_per_bar) if beat_time % beats_per_bar == 0 else int(
                beat_time / beats_per_bar) - 1
        beats = 1 + int(beat_time % beats_per_bar * musical_beats_per_beat)
        sixteenths = 1 + int(beat_time % (1.0 / musical_beats_per_beat) * 4.0)
        return (bars, beats, sixteenths)

    def note_changed(self, original_notes, new_notes):
        new = [note for note in new_notes if note not in original_notes]
        original = [note for note in original_notes if note not in new_notes]
        if len(new) == 1 and len(original) == 1:
            new = self.convert_note_to_dict(new[0])
            original = self.convert_note_to_dict(original[0])
            attr = [i for i, (o, n) in enumerate(zip(original.values(), new.values())) if o != n][0]
            if attr == 2:
                return self.convert_note_lengths_to_steps(new[ATTR[attr]], original[ATTR[attr]])
            elif attr == 4:
                return 'probability changed to {:.0%}'.format(new[ATTR[attr]])
            return '{0} changed to {1}'.format(ATTR[attr].replace("_", " "), int(new[ATTR[attr]]))


    def convert_note_to_dict(self, note):
        return dict(pitch=note.pitch, position=note.start_time, length=note.duration, mute=note.mute,
                    probability=note.probability, release_velocity=note.release_velocity, velocity=note.velocity,
                    velocity_range=note.velocity_deviation)

    def convert_note_lengths_to_steps(self, new, old):
        diff = abs(new - old)
        steps = math.floor(new * 4) / 4
        old_steps = math.floor(old * 4) / 4
        fine = round(((new - steps) / 0.25) * 100)
        if diff % 0.25 == 0.0:
            return f"length changed to {int(steps * 4)} steps"
        elif steps != old_steps:
            return f"length changed to {int(steps * 4)} steps and {fine} fine"
        else:
            return f"fine changed to {fine}"

    @staticmethod
    def convert_to_note(pitch):
        octave = int(pitch / 12) - 2
        note = pitch % 12
        return '{0}{1}'.format(NOTES[note], octave)
