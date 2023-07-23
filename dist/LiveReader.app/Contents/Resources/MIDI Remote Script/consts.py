import Live

QUANT_BEATS = [1 / 960,
               0.0125,
               0.25,
               0.5,
               1.0,
               2.0,
               4.0,
               8.0,
               16.0,
               32.0]

QUANT_VALUES = [Live.Clip.GridQuantization.no_grid,
                Live.Clip.GridQuantization.g_thirtysecond,
                Live.Clip.GridQuantization.g_sixteenth,
                Live.Clip.GridQuantization.g_eighth,
                Live.Clip.GridQuantization.g_quarter,
                Live.Clip.GridQuantization.g_half,
                Live.Clip.GridQuantization.g_bar,
                Live.Clip.GridQuantization.g_2_bars,
                Live.Clip.GridQuantization.g_4_bars,
                Live.Clip.GridQuantization.g_8_bars]

QUANT_NAMES = ['None',
               'thirtysecond',
               'sixteenth',
               'eighth',
               'quarter',
               'half',
               'bar',
               '2 bar',
               '4 bar',
               '8 bar']

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

ATTR = {0: 'pitch',
        1: 'position',
        2: 'length',
        3: 'mute',
        4: 'probability',
        5: 'release_velocity',
        6: 'velocity',
        7: 'velocity_range'}

ROOT_NOTES = ["C", "G", "D", "A", "E", "B", "F", "B flat", "E flat", "A flat", "D flat", "G flat"]

MODE_MESSAGES = {
    "browse": "Browser mode, use arrows to navigate, toggle preview with top button 2",
    "clip": "Clip editing mode",
    "add_track": "Browser in adding track mode",
    "add_device": "Browser in adding device mode",

}










