import Live
from _Framework.ControlSurface import ControlSurface
from .TransportActions import TransportActions
from .SessionActions import SessionActions
from .BrowserActions import BrowserActions
from .DeviceActions import DeviceActions
from .ClipActions import ClipActions
from .key_consts import *
from .PushMonitoring import PushMonitoring
from ableton.v2.base import nop
import json


class LiveReader(ControlSurface):

    def __init__(self, c_instance):
        super(LiveReader, self).__init__(c_instance)
        self._suggested_input_port = str(u'Live Reader IN (feedback)')
        self._suggested_output_port = str(u'Live Reader OUT (commands)')
        with self.component_guard():
            self._transport = TransportActions()
            self._session = SessionActions(c_instance)
            self._browser = BrowserActions(c_instance)
            self._device = DeviceActions(c_instance)
            self._clip = ClipActions(c_instance)
            

        self.global_buttons = {
            ONE_KEY: self.set_session_mode,
            TWO_KEY: self.set_mixer_mode,
            THREE_KEY: self.set_routing_mode,
            FOUR_KEY: self.set_device_mode,
            FIVE_KEY: self.set_parameter_mode,
            SIX_KEY: self.set_browser_mode,
            SEVEN_KEY: self.set_clip_mode,
            ALT_THREE: self._transport.click_button,
            ALT_FOUR: self._transport.overdub_button,
            ALT_FIVE: self._transport.record_button,
            ALT_ONE: self._transport.tempo_down,
            ALT_TWO: self._transport.tempo_up,
            ALT_SHIFT_ONE: self._transport.tempo_down_big,
            ALT_SHIFT_TWO: self._transport.tempo_up_big,
            ALT_CMD_T: self.add_return_track
            }

        self.modes = {'Session': self._session.get_action,
                      'Browser': self._browser.get_action,
                      'Device': self._device.get_action,
                      'Clip': self._clip.get_action
                      }

        self.view = self.application().view
        self.current_mode = 'Session'
        self.send_midi('Script initialised')
        self.push = PushMonitoring(log_message = self.log_message, send_midi=self.send_midi, register_component=nop, song=nop)
        self.push.get_push_instance()
        


    def disconnect(self):
        ControlSurface.disconnect(self)



    def receive_midi(self, midi_bytes):
        self.log_message(midi_bytes)
        if midi_bytes == (240, 0, 33, 29, 1, 1, 10, 0, 247):
            self.push.get_push_instance()
            return 
        if midi_bytes[0] == 240:
            midi_bytes = midi_bytes[1:-1]
            try:
                self.send_midi(self.global_buttons[midi_bytes]())
            except KeyError:
                self.send_midi(self.modes[self.current_mode](midi_bytes))

    def send_midi(self, text):
        if text:
            sys_text = tuple([240] + [ord(c) for c in text] + [247])
            self._send_midi(sys_text)
            self.show_message(text)

    def set_session_mode(self):
        self.view.show_view('Session')
        self.view.focus_view('Session')
        self.current_mode = 'Session'
        return 'Session mode'

    def set_device_mode(self):
        self.view.show_view('Detail/DeviceChain')
        self.view.focus_view('Detail/DeviceChain')
        self.current_mode = 'Device'
        self.view.scroll_view(Live.Application.Application.View.NavDirection.right, 'Detail/DeviceChain', False)
        self.view.scroll_view(Live.Application.Application.View.NavDirection.left, 'Detail/DeviceChain', False)
        return 'Device mode'

    def set_parameter_mode(self):
        self.set_device_mode()
        self.view.show_view('Detail/DeviceChain')
        self.view.focus_view('Detail/DeviceChain')
        self.view.scroll_view(Live.Application.Application.View.NavDirection.right, 'Detail/DeviceChain', False)
        self.view.scroll_view(Live.Application.Application.View.NavDirection.left, 'Detail/DeviceChain', False)
        return self._device.set_sub_mode('Parameter')

    def set_browser_mode(self):
        self.set_device_mode()
        self.view.show_view('Detail/DeviceChain')
        self.view.focus_view('Detail/DeviceChain')
        self.view.scroll_view(Live.Application.Application.View.NavDirection.right, 'Detail/DeviceChain', False)
        self.view.scroll_view(Live.Application.Application.View.NavDirection.left, 'Detail/DeviceChain', False)
        self._device.set_sub_mode('Browser')
        return 'Browser mode'

    def set_routing_mode(self):
        self.set_session_mode()
        self._session.set_sub_mode('Routing')
        return 'Routing Mode'

    def set_mixer_mode(self):
        self.set_session_mode()
        self._session.set_sub_mode('Mixer')
        return 'Mixer mode'

    def set_clip_mode(self):

        if self._clip.get_highlighted_clip():
            self.application().view.show_view('Detail')
            self.application().view.focus_view('Detail/Clip')
            self.current_mode = 'Clip'
            return 'Clip editing mode'
        else:
            return 'No clip selected'

    def add_audio_track(self):
        pass
        # track = self.song().view.selected_track
        # tracks = list(self.song().tracks)
        # index = tracks.index(track) + 1
        # self.update_components()
        # return 'audio track added position {0}'.format(index)

    def add_midi_track(self):
        pass
        # track = self.song().view.selected_track
        # tracks = list(self.song().tracks)
        # index = tracks.index(track) + 1
        # self.update_components()
        # return 'midi track added position {0}'.format(index)

    def add_return_track(self):
        self.song().view.selected_track = self._session.track
        return 'return track added'

    def update_components(self):
        self._session.track = self.song().view.selected_track
        self._session.track_name = self._session.track.name
        self._session.scene = self.song().view.selected_scene
        self._session.selected_tracks = []
        self._session.header_selected = False
