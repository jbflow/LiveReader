# LiveReader

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-360/)

### Confirmed Compatibility:

- MacOS Intel (Big Sur)
- Ableton Live 11

Livereader is an accessibility tool for Ableton Live. It aims to make Live and Push accessible to those with visual impairments. It does
this via a custom desktop app, a MIDI remote script and a series of keyboard shortcuts. See [here](keyboard_shortcuts.txt) for a list of keyboard shortcuts.

### Confirmed Compatibility:

- MacOS Intel (Big Sur)
- Ableton Live 11

** Note to users/testers:

In it's current state it should be possible to download, set up and access Livereader without the assistance of a sighted user; however, this is still an Alpha release
that is under development. Functionality cannot be guaranteed and errors probably WILL happen. It is strongly advised that a blind or visually-impaired user has someone available that is able to help with this.
Feel free to drop me a message or open an issue if you are actively testing and if I am able assist you I will do so (I can't make any promises here as my time is limited)

## To get set up

- Download [LiveReader.zip](LiveReader.zip) in the [dist](dist) folder
- Unzip the app and copy to your applications folder
- Give the App Accessibility and Input Monitoring permissions in System Preferences > Security & Privacy > Privacy
- Launch the App
- Launch Live

Everything should be automatically configured

This includes:
- Creating IAC Drivers for MIDI communication
- Copying MIDI Remote Script
- Setting Script and MIDI Ports in preferences automatically

If a push is detected by the script push functionality should work out of the box (This has not been tested on all systems)

## Developers

I will aim to put a full breakdown on how you can contribute here at some stage, but any developers that are interested in getting involved please reach out.

The bare minimum to get you set up for development is

```
virtualenv -p=3.8 .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

To continuously read the Live logs in your python console
```
from dev_tools import read_log
read_log("11.3.4") # Takes the live version as an argument
```

Any changes to the MIDI remote script will need to be moved into MIDI remote script folder and live to be restarted for changes to take affect:

```
from dev_tools import copy_script
copy_script()
```

### Build

The project is built using PyInstaller, I created a shell script that builds the project with all the necessary data files from [a spec file](main.spec) and then zips it into the [dist](dist) folder.

``` 
sh build.sh
```

### To Do

- MacOS ARM Support
- Set up automated testing
- Create a release pipeline
- Automatic MIDI Remote Script update checking in app from main branch
- Expand and refine Push functionality
- Update Keyboard monitoring and SysEx messages to use Bitmasking instead of (1/0) integer arrays
- Expand MIDI remote scripts for keyboard shortcuts
- Preferences are not accessible
- Dialog boxes are not accessible
- Windows support (Requires some virtual MIDI work, I am working on a binding for the virtualMIDI driver by Tobias Erichsen that will make this possible programmatically in Python)

### Blog

I have published a blog on this work here, which contains a demonstration video.

https://flowstate-creative-solutions.tumblr.com/
