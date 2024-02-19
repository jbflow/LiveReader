from ableton.v2.control_surface import Component
from ableton.v2.base import depends, nop, listens
from Push2.push2 import Push2

from ableton.v2.control_surface.mode import ModesComponent
from Push2.notification_component import NotificationComponent

import re
from .PushMonitoringBrowser import PushMonitoringBrowser
from .PushMonitoringClip import PushMonitoringClip
from .PushMonitoringDevice import PushMonitoringDevice
from .PushMonitoringMix import PushMonitoringMix
from .PushMonitoringScales import PushMonitoringScales



def get_push_component(push, ClassComponent):
    return [component for component in push._components if isinstance(component, ClassComponent)][0]


class PushMonitoring(Component):
    @depends(log_message=None, send_midi=None)
    def __init__(self, log_message, send_midi, *a, **k):
        super(PushMonitoring, self).__init__(*a, **k)
        self.log_message = log_message
        self.send_midi = send_midi
        self.modes_component = None
        self.selected_mode = None
        self.shift_button = None
        self.pads = []
        self.touches = []
        self.bottom_buttons = []
    def send_midi(self, midi):
        return self.send_midi(midi)

    def log(self, message):

        self.log_message(message)

    def get_push_instance(self):
        for i, control_surface in enumerate(self.application.control_surfaces):
            if control_surface and isinstance(control_surface, Push2):
                self.push = control_surface
                break
        else:  # No Break
            self.log("No push detected")
            return
        if self.push._initialized:
            self.modes_component = self.push._main_modes
            self._on_main_mode_changed.subject = self.modes_component
            self.register_controls()
            self.initialize_monitoring()
            self.send_midi("Push loaded")

    def initialize_monitoring(self):
        self.clip = PushMonitoringClip(push=self.push, main_modes=self.modes_component, log_message=self.log, send_midi=self.send_midi,
                                                   song=self.song, shift_button=self.shift_button, select_button=self.select_button, pads=self.pads)
        self.device = PushMonitoringDevice(push=self.push, main_modes=self.modes_component, log_message=self.log, send_midi=self.send_midi,
                                                       song=self.song)
        self.browse = PushMonitoringBrowser(push=self.push, main_modes=self.modes_component, log_message=self.log, send_midi=self.send_midi)

        self.mix = PushMonitoringMix(push=self.push, main_modes=self.modes_component, log_message=self.log, send_midi=self.send_midi, song=self.song)
        notification_component = get_push_component(self.push, NotificationComponent)
        self.register_slot(notification_component, lambda: self.show_notification(notification_component), "message")

        self.scales = PushMonitoringScales(push=self.push, log_message=self.log, send_midi=self.send_midi)
        self.register_slot(self.push._dialog_modes, lambda mode: self.send_midi(f"{'scales open' if mode == 'scales' else ''}"), 'selected_mode')


    def get_main_modes(self):
        modes_component = [component for component in self.push._components if
                           isinstance(component, ModesComponent) and component._mode_list == ['mix', 'clip', 'device',
                                                                                              'browse', 'add_device',
                                                                                              'add_track', 'user']][0]
        return modes_component


    def register_controls(self):
        for control in self.push.controls:
            self.log(control.name)
            if "Track_Control_Touch_" in control.name:
                self.register_slot(control,
                                   lambda value, control=control._msg_identifier: self._on_control_midi_value_changed(
                                       value,
                                       control,
                                       "touches"),
                                   u'value')
            elif "Track_State_Button" in control.name and control.name != "Track_State_Buttons":
                self.register_slot(control,
                                   lambda value,
                                          control=control._msg_identifier - 102: self._on_control_midi_value_changed(
                                       value,
                                       control,
                                       "top_buttons"),
                                   u'value')
            elif "Track_Select_Button" in control.name and control.name != "Track_Select_Buttons":
                self.register_slot(control,
                                   lambda value,
                                          control=control._msg_identifier - 20: self._on_control_midi_value_changed(
                                       value,
                                       control,
                                       "bottom_buttons"),
                                   u'value')
            elif control.name in ["Shift_Button", "Select_Button"]:
                setattr(self, control.name.lower(), control)


    def show_notification(self, component):
        if component._show_notification and self.push._dialog_modes.selected_mode != "scales":
            self.send_midi(component._message)

    def _on_control_midi_value_changed(self, value, control, control_list):
        try:
            if value == 127:
                getattr(self, self.selected_mode).on_values_changed(value, control, control_list)
        except Exception as e:
            self.log_message(e)


    @listens("selected_mode")
    def _on_main_mode_changed(self, selected_mode):
        self.log_message(selected_mode)
        if selected_mode:
            self.selected_mode = selected_mode
            getattr(self, selected_mode).enter()

    def disconnect(self):
        self.send_midi("disconnecting")
        self._on_main_mode_changed.subject = None
        self._on_control_midi_value_changed.subjects = None
        self.selected_mode = None
        self.modes_component = None
        self.clip = None
        self.browse = None
        self.device = None
        self.mix = None
        self.song = None
        super(PushMonitoring, self).disconnect()

