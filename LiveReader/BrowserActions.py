import Live

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from .key_consts import *


class BrowserActions(ControlSurfaceComponent):
    __module__ = __name__

    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)
        self._c_instance = c_instance

        self.browser = self.application().browser
        self.parents = [self.browser.sounds, self.browser.drums, self.browser.instruments, self.browser.audio_effects,
                        self.browser.midi_effects, self.browser.max_for_live, self.browser.plugins, self.browser.clips,
                        self.browser.samples, self.browser.packs, self.browser.user_library]
        x = 0
        while x < len(self.browser.user_folders):
            self.parents.append(self.browser.user_folders[x])
            x += 1

        self.parent = None
        self.counter = []
        self.index = 0
        self.focused = self.parents[self.index]
        self.current_list = self.parents
        self.insert_mode = 'end'

        self.actions = {
            ALT_UP: self.previous,
            ALT_DOWN: self.next,
            ALT_LEFT: self.go_back,
            ALT_RIGHT: self.open,
            SHIFT_R: self.load
            }

    def get_action(self, midi_bytes):
        if not midi_bytes[21:] == (0, 0):

            return self.char_pressed(midi_bytes)
        else:
            return self.actions[midi_bytes]()

    def char_pressed(self, midi_bytes):

        ASCII = chr((midi_bytes[21] * 128) + midi_bytes[22])
        if ASCII.isalpha() and midi_bytes[2] == 1:
            for counter, item in enumerate(self.current_list):
                if item.name[0].lower() == ASCII.lower():
                    self.index = counter
                    self.focused = self.current_list[self.index]
                    return self.focused.name

        elif ASCII == ';':
            for track in self.song().tracks:
                track.view.device_insert_mode = Live.Track.DeviceInsertMode.selected_left
            return 'insert left'
        elif ASCII == "'":
            for track in self.song().tracks:
                track.view.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
            return 'insert right'
        elif ASCII == "\\":
            for track in self.song().tracks:
                track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
            return 'insert end'

    def next(self):
        self.application().browser.stop_preview()
        if self.index < len(self.current_list) - 1:
            self.index = self.index + 1
            self.focused = self.current_list[self.index]
            if self.focused.is_loadable:
                self.application().browser.preview_item(self.focused)
            return self.focused.name


        else:
            self.index = 0
            self.focused = self.current_list[self.index]
            if self.focused.is_loadable:
                self.application().browser.preview_item(self.focused)
            return self.focused.name

    def previous(self):
        self.application().browser.stop_preview()
        if self.index >= 1:
            self.index = self.index - 1
            self.focused = self.current_list[self.index]
            if self.focused.is_loadable:
                self.application().browser.preview_item(self.focused)
            return self.focused.name

        else:
            self.index = len(self.current_list) - 1
            self.focused = self.current_list[self.index]
            if self.focused.is_loadable:
                self.application().browser.preview_item(self.focused)
            return self.focused.name

    def open(self):
        self.application().browser.stop_preview()

        if not self.focused.children:
            return self.focused.name

        elif self.focused in self.parents:
            self.parent = self.index
            self.current_list = self.focused.children
            self.focused = self.focused.children[0]
            self.index = 0
            if self.focused.is_loadable:
                self.application().browser.preview_item(self.focused)

            return self.focused.name

        elif self.focused.is_folder or self.focused.is_device or self.parent in (6, 9):

            if len(self.focused.children) is not 0:
                self.counter.append(self.index)
                self.current_list = self.focused.children
                self.focused = self.focused.children[0]
                self.index = 0
                if self.focused.is_loadable:
                    self.application().browser.preview_item(self.focused)

                return self.focused.name

            else:

                return self.focused.name

    def go_back(self):
        self.application().browser.stop_preview()
        if self.counter == []:
            self.focused = self.parents[self.parent]
            self.current_list = self.parents
            self.index = self.parent
            self.parent = ''
            return self.focused.name
        else:
            length = len(self.counter) - 1
            self.index = self.counter[length]
            self.counter.pop(length)
            self.focused = self.parents[self.parent]
            for x in self.counter:
                self.focused = self.focused.children[x]
            self.current_list = self.focused.children
            self.focused = self.focused.children[self.index]
            return self.focused.name

    def load(self):

        if self.focused.is_loadable:
            self.application().browser.stop_preview()
            self.application().browser.load_item(self.focused)

            self.track = self.song().view.selected_track
            devices = list(self.track.devices)
            device = devices.index(self.track.view.selected_device)
            return "loaded {0} at index {1}".format(self.focused.name, device + 1)

        else:
            return self.open()
