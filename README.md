# LiveReader


Livereader is an accessibility tool for Ableton Live. It aims to make Live and Push accessible to those with visual impairments. It does
this via a custom desktop app, a MIDI remote script and a series of keyboard shortcuts. See [here](docs/shortcuts.md) for a list of a keyboard shortcuts.

Currently Live reader is MacOS only.

* Note to users/tests
In it's current state it should be possible to download, set up and access Livereader without the assistance of a sighted user, however, this is still an Alpha release, 
that is under development, therefor functionality cannot be guaranteed and errors likely WILL happen. Therefor it is strongly advised that a blind or visually-impaired user has someone available that is able to help with this.
Feel free to drop me a message if you are actively testing and if I am able to I will assist you.

## Set up

- Download the release in the dist folder
- Launch the App
- Launch Live

Everything should be automatically configured

## Developers

I will aim to put a full breakdown on how you can contribute here soon, but any developers that are interested in getting involved please reach out.

The bare minimum to get you set up for development is

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

To read the Live logs you can run
```
python DevTools.py
```

Any changes to the MIDI remote script will need to be moved into the correct folder (I am going to write a script for this)

### To Do

- Expand and refine Push functionality
- Update Keyboard monitoring and SysEx messages to use Bitmasking instead of (1/0) integer arrays
- Update MIDI remote scripts for keyboard shortcuts
- Preferences are not accessible
- Dialog boxes are not accessible
- Windows support (I am actively working on this, it requires some virtual MIDI work which I will be releasing very soon)

### Blog

I have published a blog on this work here, which contains a demonstration video.

https://flowstate-creative-solutions.tumblr.com/
