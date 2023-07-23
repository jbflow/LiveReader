from .consts import NOTES


def modify_func(func, extra_func):
    def decorator(*a, **k):
        func(*a, **k)
        extra_func()

    return decorator


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


def convert_to_note(pitch):
    octave = int(pitch / 12) - 2
    note = pitch % 12
    return '{0}{1}'.format(NOTES[note], octave)
