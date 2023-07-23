from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from .BrowserActions import BrowserActions
from .ParameterActions import ParameterActions
from .key_consts import *


class DeviceActions(ControlSurfaceComponent):
    __module__ = __name__

    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)
        self.end_of_chain = None
        self.end_of_devices = None
        self._c_instance = c_instance
        self._browser = BrowserActions(c_instance)
        self._parameter = ParameterActions(c_instance)
        self.device = self.song().view.selected_track.view.selected_device
        self.chains = None
        self.drum_pads = None
        self.chain_index = 0
        self.pad_index = 0
        self.sub_mode = 'Parameter'
        self.sub_modes = {'Parameter': self._parameter.get_action,
                          'Browser': self._browser.get_action}
        self.actions = {
            LEFT_ARROW: self.left_arrow,
            RIGHT_ARROW: self.right_arrow,
            CMD_R: self.rename,
            ENTER: self.enter,
            BACKSPACE: self.delete,
            DEL: self.delete,
            SHIFT: self.selecting,
            SHIFT_RIGHT: self.selecting_right,
            SHIFT_LEFT: self.selecting_left,
            SQR_BRACKET_CLOSED: self.next_chain,
            SQR_BRACKET_OPEN: self.prev_chain
        }

    def get_action(self, midi_bytes):
        if midi_bytes not in self.actions.keys():
            feedback = self.sub_modes[self.sub_mode](midi_bytes)
            if 'loaded' in feedback:
                self.update_selected_device()
            return feedback
        else:
            return self.actions[midi_bytes]()

    def set_sub_mode(self, sub_mode):
        self.sub_mode = sub_mode
        if self.sub_mode == 'Parameter':
            return self._parameter.make_parameter_list(self.device)

    def left_arrow(self):
        device_list = list(self.song().view.selected_track.devices)
        if self.end_of_devices:
            self.end_of_devices = False
            last_device = device_list(len(device_list -1))
            if last_device.can_have_chains and last_device.view.selected_chain.devices and last_device.view.is_showing_chain_devices:
                self.end_of_chain = True
                return 'end of chain'
        if self.end_of_chain:
            self.end_of_chain = False
        return self.update_selected_device()


        return self.update_selected_device()

    def right_arrow(self):
        # get the list of devices
        device_list = list(self.song().view.selected_track.devices)
        # if the previously selected device is in the list (ie not in a rack)
        if self.device in device_list:
            # and its the last in the list and isn't a rack
            if device_list.index(self.device) == len(device_list) - 1 and not self.device.can_have_chains:
                # then we've reached the end of our device chain
                self.end_of_devices = True
                return 'end of devices'
            # otherwise we haven't, so update the selected device
            else:
                return self.update_selected_device()
        # if its not in the list (so it is in a rack)
        else:
            # get the list of devices in the rack
            chain_devices = list(self.device.canonical_parent.devices)
            # if its the last one, and we're not already at the end of the chain
            if chain_devices.index(self.device) == len(chain_devices) - 1 and not self.end_of_chain:
                # then we're at the end of the chain
                self.end_of_chain = True
                return 'end of chain'
            # if we're at the end of the chain
            elif self.end_of_chain:
                # then set that
                self.end_of_chain = False
                # get the parent
                rack_device = self.device.canonical_parent.canonical_parent
                # and if the parent is the last in the main device chain
                if device_list.index(rack_device) == len(device_list) - 1:
                    # we've reached our end of devices
                    return 'end of devices'
                # if not then we haven't so update
                else:
                    return self.update_selected_device()
            # if its not the last device in the chain, and we're not at the end of the chain, then update
            else:
                return self.update_selected_device()








    def update_selected_device(self):
        self.device = self.song().view.selected_track.view.selected_device
        self._parameter.make_parameter_list(self.device)
        if self.device and self.device.can_have_drum_pads and self.device.drum_pads:
            self.drum_pads = self.device.drum_pads
            self.pad_index = list(self.drum_pads).index(self.device.view.selected_drum_pad)
        elif self.device and self.device.can_have_chains and self.device.chains:
            self.chains = self.device.chains
            self.chain_index = list(self.chains).index(self.device.view.selected_chain)
        if self.device:
            return self.device.name


    def next_chain(self):
        if self.device.can_have_drum_pads:
            self.pad_index += 1
            self.device.view.selected_drum_pad = self.drum_pads[self.pad_index]
            return 'drum pad {0}'.format(self.device.view.selected_drum_pad.name)
        elif self.device.can_have_chains:
            self.chain_index += 1
            self.device.view.selected_chain = self.chains[self.chain_index]
            return 'chain {0}'.format(self.device.view.selected_chain.name)


    def prev_chain(self):
        if self.device.can_have_drum_pads:
            self.pad_index -= 1
            self.device.view.selected_drum_pad = self.drum_pads[self.pad_index]
        elif self.device.can_have_chains:
            self.chain_index -= 1
            self.device.view.selected_chain = self.chains[self.chain_index]

    def rename(self):
        pass

    def renamed(self):
        pass

    def enter(self):
        pass

    def delete(self):
        pass

    def selecting(self):
        pass

    def selecting_right(self):
        pass

    def selecting_left(self):
        pass
