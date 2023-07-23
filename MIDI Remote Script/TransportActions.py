from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


class TransportActions(ControlSurfaceComponent):
    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)
        self._c_instance = c_instance
        self.song().add_is_playing_listener(self.start_or_stop)

    def disconnect(self):
        self.song().remove_is_playing_listener(self.start_or_stop)

    def send_midi(self, text):
        sys_text = tuple([240] + [ord(c) for c in text] + [247])
        self._c_instance.send_midi(sys_text)
        self._c_instance.show_message(text)

    def start_or_stop(self):
        if self.song().is_playing:
            self.send_midi('play')
        else:
            self.send_midi('stop')


    def record_button(self):
        if self.song().record_mode == 0:
            self.song().record_mode = 1
            return 'record enabled'
        else:
            self.song().record_mode = 0
            return 'record disabled'

    def overdub_button(self):
        if self.song().arrangement_overdub == 0:
            self.song().arrangement_overdub = 1
            return 'overdub enabled'
        else:
            self.song().arrangement_overdub = 0
            return 'overdub disabled'
    def loop_button(self):
        if self.song().loop == 0:
            self.song().loop = 1
            return 'loop enabled'
        else:
            self.song().loop = 0
            return 'loop disabled'
    def click_button(self):
        if self.song().metronome == 0:
            self.song().metronome = 1
            return 'click enabled'
        else:
            self.song().metronome = 0
            return 'click disabled'

    def tempo_down(self):
        self.song().tempo = self.song().tempo - 1
        return 'tempo {0}'.format(self.song().tempo)

    def tempo_up(self):
        self.song().tempo = self.song().tempo + 1
        return 'tempo {0}'.format(self.song().tempo)

    def tempo_down_big(self):
        self.song().tempo = self.song().tempo - 10
        return 'tempo {0}'.format(self.song().tempo)

    def tempo_up_big(self):
        self.song().tempo = self.song().tempo + 10
        return 'tempo {0}'.format(self.song().tempo)
