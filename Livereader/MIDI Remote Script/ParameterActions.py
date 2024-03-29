import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from .key_consts import *


class ParameterActions(ControlSurfaceComponent):
    __module__ = __name__

    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)
        self._c_instance = c_instance
        self.device = None
        self.param_index = 0
        self.selected_param = None
        self.parame_list = []
        self.actions = {
            ALT_UP: self.alt_up,
            ALT_DOWN: self.alt_down,
            ALT_LEFT: self.alt_left,
            ALT_RIGHT: self.alt_right
            }

    def get_action(self, midi_bytes):
        if not midi_bytes[21:] == (0, 0):
            return self.char_pressed(midi_bytes)
        else:
            return self.actions[midi_bytes]()


    def make_parameter_list(self, device):
        self.device = device
        if self.device:
            self.param_index = 0
            self.param_list = self.device.parameters
            self.selected_param = self.param_list[self.param_index]
            return 'parameter mode'
        else:
            return 'No device, cant enter parameter mode'

    def char_pressed(self, midi_bytes):
        ASCII = chr((midi_bytes[21] * 128) + midi_bytes[22])
        if ASCII.isalpha() and midi_bytes[2] == 1:

            for counter, item in enumerate(self.param_list):
                if item.name[0].lower() == ASCII.lower():
                    self.param_index = counter
                    self.selected_param = self.param_list[self.param_index]
                    name = self.selected_param.name
                    value = self.selected_param.str_for_value(self.selected_param.value)
                    return '{0} {1}'.format(name, value)

    def alt_up(self):
        if not self.selected_param.is_enabled:
            return 'Parameter not enabled'
        else:
            if self.selected_param.is_quantized == True:
                max = self.selected_param.max
                if self.selected_param.value < max:
                    self.selected_param.value += 1
                elif self.selected_param.value == max:
                    self.selected_param.value -= max
            else:
                if self.selected_param.max != 1:
                    step = 1
                else:
                    step = (self.selected_param.max - self.selected_param.min) / 127

                self.selected_param.value += step

        value = self.selected_param.str_for_value(self.selected_param.value)
        return value

    def alt_down(self):
        if not self.selected_param.is_enabled:
            return 'parameter not enabled'
        else:
            if self.selected_param.is_quantized == True:
                min = self.selected_param.min
                max = self.selected_param.max
                if self.selected_param.value > min:
                    self.selected_param.value -= 1
                elif self.selected_param.value == min:
                    self.selected_param.value += max
            else:
                if self.selected_param.max != 1:
                    step = 1
                else:
                    step = (self.selected_param.max - self.selected_param.min) / 127

                self.selected_param.value -= step

        value = self.selected_param.str_for_value(self.selected_param.value)
        return value

    def alt_left(self):
        self.param_index -= 1
        i = self.param_index
        self.selected_param = self.param_list[i]
        name = self.selected_param.name
        value = self.selected_param.str_for_value(self.selected_param.value)
        return '{0} {1}'.format(name, value)

    def alt_right(self):
        self.param_index += 1
        i = self.param_index
        self.selected_param = self.param_list[i]
        name = self.selected_param.name
        value = self.selected_param.str_for_value(self.selected_param.value)
        return '{0} {1}'.format(name, value)

