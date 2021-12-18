from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from .key_consts import *

class RoutingActions(ControlSurfaceComponent):
    __module__ = __name__
    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)
        self._c_instance = c_instance
        self.track = None
        self.input_routing_index = 0
        self.input_sub_routing_index = 0
        self.output_routing_index = 0
        self.output_sub_routing_index = 0
        self.monitor_index = 0
        self.routing_index = 0
        self.routing_list = ["input routing", "input sub routing", "monitoring", "output routing", "output sub routing"]
        self.routing = None
        self.actions = {
                        ALT_UP: self.alt_up,
                        ALT_DOWN: self.alt_down,
                        ALT_LEFT: self.alt_left,
                        ALT_RIGHT: self.alt_right
                        }

    def get_action(self, midi_bytes):
        if midi_bytes in self.actions.keys():
            return self.actions[midi_bytes]()



    def make_routing_lists(self):
        self.track = self.song().view.selected_track
        if self.track in self.song().return_tracks:
            self.routing_index = 3
        elif self.track == self.song().master_track:
            self.routing_index = 3
        else:
            self.routing_index = 0
            self.setup_routing_lists()
        self.routing = self.track.available_input_routing_types[self.input_routing_index].display_name
        return 'Routing, {0} {1}'.format(self.routing_list[self.routing_index], self.routing)

    def setup_routing_lists(self):
        self.track = self.song().view.selected_track
        self.input_routing_index = 0
        self.input_sub_routing_index = 0
        self.output_routing_index = 0
        self.output_sub_routing_index = 0
        for input in self.track.available_input_routing_types:
            if input == self.track.input_routing_type:
                break
            else:
                self.input_routing_index += 1
        for input_sub in self.track.available_input_routing_channels:
            if input_sub == self.track.input_routing_channel:
                break
            else:
                self.input_sub_routing_index += 1
        for output in self.track.available_output_routing_types:
            if output == self.track.output_routing_type:
                break
            else:
                self.output_routing_index += 1
        for output_sub in self.track.available_output_routing_channels:
            if output_sub == self.track.output_routing_channel:
                break
            else:
                self.output_routing_index += 1

    def alt_up(self):
        self.setup_routing_lists()
        if self.routing_index > 0:
            self.routing_index -= 1


            if self.routing_index == 0:
                self.routing = self.track.available_input_routing_types[self.input_routing_index].display_name
            elif self.routing_index == 1:
                if self.track.available_input_routing_channels[self.input_sub_routing_index].display_name != "":
                    self.routing = self.track.available_input_routing_channels[
                        self.input_sub_routing_index].display_name
                else:
                    return "No input routing channels available"

            elif self.routing_index == 2:
                if self.track.available_input_routing_types[self.input_routing_index].display_name != "No Input":
                    if self.track.current_monitoring_state == 0:
                        self.routing = "In"
                    elif self.track.current_monitoring_state == 1:
                        self.routing = "Auto"
                    elif self.track.current_monitoring_state == 2:
                        self.routing = "Off"
                else:
                    return 'No input selected, monitoring options disabled'

            elif self.routing_index == 3:
                if self.track in self.song().return_tracks:
                    return 'Return track selected, no monitoring or input options available'
                elif self.track == self.song().master_rack:
                    return 'Master track selected, no monitoring or input options available'
                else:
                    self.routing = self.track.available_output_routing_types[self.output_routing_index].display_name
        return '{0} {1}'.format(self.routing_list[self.routing_index], str(self.routing))



    def alt_down(self):
        self.setup_routing_lists()
        if self.routing_index < 4:
            self.routing_index += 1
            if self.routing_index == 1:
                if self.track.available_input_routing_channels[self.input_sub_routing_index].display_name != '':
                    self.routing = self.track.available_input_routing_channels[
                        self.input_sub_routing_index].display_name
                else:
                    return 'No input routing channels available'

            elif self.routing_index == 2:
                if self.track.available_input_routing_types[self.input_routing_index].display_name != 'No Input':
                    if self.track.current_monitoring_state == 0:
                        self.routing = 'In'
                    elif self.track.current_monitoring_state == 1:
                        self.routing = 'Auto'
                    elif self.track.current_monitoring_state == 2:
                        self.routing = 'Off'
                else:
                    return 'No input selected, monitoring options disabled'

            elif self.routing_index == 3:
                self.routing = self.track.available_output_routing_types[self.output_routing_index].display_name
            elif self.routing_index == 4:
                if self.track.available_output_routing_channels[self.output_sub_routing_index].display_name != '':
                    self.routing = self.track.available_output_routing_channels[
                        self.output_sub_routing_index].display_name
                else:
                    self.routing_index -= 1
                    return 'No output routing channels available'
            return '{0} {1}'.format(self.routing_list[self.routing_index], str(self.routing))
            


    def alt_left(self):
        if self.routing_index == 0:
            if self.input_routing_index == 0:
                self.input_routing_index = len(self.track.available_input_routing_types) - 1
            else:
                self.input_routing_index -= 1
            self.track.input_routing_type = self.track.available_input_routing_types[self.input_routing_index]
            return self.track.available_input_routing_types[self.input_routing_index].display_name

        elif self.routing_index == 1:
            if self.input_sub_routing_index == 0:
                self.input_sub_routing_index = len(self.track.available_input_routing_channels) - 1
            else:
                self.input_sub_routing_index -= 1

            self.track.input_routing_channel = self.track.available_input_routing_channels[self.input_sub_routing_index]
            return self.track.available_input_routing_channels[self.input_sub_routing_index].display_name

        elif self.routing_index == 2:
            if self.track.current_monitoring_state == 0:
                self.track.current_monitoring_state = 2
            else:
                self.track.current_monitoring_state -= 1
            if self.track.current_monitoring_state == 0:
                return "In"
            elif self.track.current_monitoring_state == 1:
                return "Auto"
            elif self.track.current_monitoring_state == 2:
                return "Off"

        elif self.routing_index == 3:
            if self.output_routing_index == 0:
                self.output_routing_index = len(self.track.available_output_routing_types) - 1
            else:
                self.output_routing_index -= 1
            self.track.output_routing_type = self.track.available_output_routing_types[self.output_routing_index]
            return self.track.available_output_routing_types[self.output_routing_index].display_name

        elif self.routing_index == 4:
            if self.output_sub_routing_index == 0:
                self.output_sub_routing_index = len(self.track.available_output_routing_channels) - 1
            else:
                self.output_sub_routing_index -= 1
            self.track.output_routing_channel = self.track.available_output_routing_channels[
                self.output_sub_routing_index]
            return self.track.available_output_routing_channels[self.output_sub_routing_index].display_name

    def alt_right(self):
        if self.routing_index == 0:
            if self.input_routing_index == len(self.track.available_input_routing_types) - 1:
                self.input_routing_index = 0
            else:
                self.input_routing_index += 1
            self.track.input_routing_type = self.track.available_input_routing_types[self.input_routing_index]
            return self.track.available_input_routing_types[self.input_routing_index].display_name
        elif self.routing_index == 1:
            if self.input_sub_routing_index == len(self.track.available_input_routing_channels) - 1:
                self.input_sub_routing_index = 0
            else:
                self.input_sub_routing_index += 1
            self.track.input_routing_channel = self.track.available_input_routing_channels[self.input_sub_routing_index]
            return self.track.available_input_routing_channels[self.input_sub_routing_index].display_name
        elif self.routing_index == 2:
            if self.track.current_monitoring_state == 2:
                self.track.current_monitoring_state = 0
            else:
                self.track.current_monitoring_state += 1
            if self.track.current_monitoring_state == 0:
                return 'In'
            elif self.track.current_monitoring_state == 1:
                return 'Auto'
            elif self.track.current_monitoring_state == 2:
                return 'Off'

        elif self.routing_index == 3:
            if self.output_routing_index == len(self.track.available_output_routing_types) - 1:
                self.output_routing_index = 0
            else:
                self.output_routing_index += 1
            self.track.output_routing_type = self.track.available_output_routing_types[self.output_routing_index]
            return self.track.available_output_routing_types[self.output_routing_index].display_name

        elif self.routing_index == 4:
            if self.output_sub_routing_index == len(self.track.available_output_routing_channels) - 1:
                self.output_sub_routing_index = 0
            else:
                self.output_sub_routing_index += 1

            self.track.output_routing_channel = self.track.available_output_routing_channels[
                self.output_sub_routing_index]
            return self.track.available_output_routing_channels[self.output_sub_routing_index].display_name
