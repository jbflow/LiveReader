import gzip

def turn_on_prelisten():
    als_path = '/Applications/Ableton Live 11 Suite.app/Contents/App-Resources/Builtin/Templates/DefaultLiveSet.als'
    with gzip.GzipFile(als_path, mode='rb') as gz:
        lines = gz.readlines()
        for idx, line in enumerate(lines):
            if b'MidiPrelisten' in line:
                line = line.replace(b'false', b'true')
                lines[idx] = line
    with gzip.GzipFile(als_path, mode='w+b') as gz:
        gz.writelines(lines)