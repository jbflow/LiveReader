from ableton.v2.base import EventObject
from ..consts import MODE_MESSAGES


class PushMonitoringComponent(EventObject):
    def __init__(self, PushComponent, log_message=None, main_modes=None, send_midi=None, push=None, shift_button=None,
                 select_button=None):
        super(PushMonitoringComponent, self).__init__()
        self.log_message = log_message
        self.send_midi = send_midi
        self.push = push
        self.main_modes = main_modes
        self.shift_button = shift_button
        self.select_button = select_button
        self.touches = []
        self.top_buttons = []
        self.bottom_buttons = []
        self.PushComponent = PushComponent
        self.component = self.get_push_component(self.PushComponent)

    def enter(self):
        if self.main_modes.selected_mode in MODE_MESSAGES.keys():
            self.send_midi(MODE_MESSAGES[self.main_modes.selected_mode])
        self.update_controls()

    def get_push_component(self, PushComponent):
        return [component for component in self.push._components if isinstance(component, PushComponent)][0]

    def update_controls(self):
        raise NotImplementedError


    def on_values_changed(self, value, control, control_list):
        if value == 127 and self.main_modes.selected_mode not in ["browse"]:
            self.send_midi(getattr(self, control_list)[control])

    def disconnect(self):
        self.main_modes = None
        self.send_midi = None
        self.log_message = None
        self.push = None
        self.PushComponent = None
        self.component = None
        self.touches = []
        self.top_buttons = []
        self.bottom_buttons = []
        super(PushMonitoringComponent, self).disconnect()
