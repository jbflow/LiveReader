import Live
from Push2.device_component_provider import DeviceComponentProvider
from ableton.v2.base import listens, listens_group
from past.builtins import unicode

from .PushMonitoringComponent import PushMonitoringComponent
from .PushMonitoringWavetableDevice import WavetableDevice


class Devices:
    InstrumentVector = WavetableDevice()


class PushMonitoringDevice(PushMonitoringComponent):
    def __init__(self, song, *a, **k):
        super(PushMonitoringDevice, self).__init__(DeviceComponentProvider, *a, **k)
        self.toggled_state = False
        self.touching_param = None
        self.song = song
        self.device_provider = self.component
        self._on_selected_track_changed.subject = self.song.view
        self.device_component = self.device_provider._device_component_modes[self.device_provider.selected_mode]
        self._on_device_parameters_changed.subject = self.device_provider
        self._on_device_changed.subject = self.device_provider
        self._on_selected_mode_changed.subject = self.device_provider
        self._on_options_changed.subject = self.device_component
        self.selected_device = self.device_provider.selected_mode
        self.special_device = getattr(Devices, self.selected_device, None)



    def enter(self):
        self.open_close_device.subject = self.push._device_navigation._modes
        if self.song.view.selected_track.view.selected_device:
            self.push._device_bank_registry.set_device_bank(self.song.view.selected_track.view.selected_device, 0)
        self.push._device_navigation._modes.selected_mode = "default"
        self.bottom_start_slice = 0
        self.bottom_end_slice = 7
        self.toggled_state = False
        msg = "device mode"
        msg += ", press top button 1 to expand the device" if self.song.view.selected_track.view.selected_device else ", no device currently selected"
        self.send_midi(msg)
        self.update_controls()

    def update_controls(self):
        if self.main_modes.selected_mode != "device":
            return
        self.add_new_params()
        self.log_message("updating controls")
        try:
            self.touches = []
            for p in self.device_provider.device_component._bank.parameters:
                appendable = p[1] if p[1] else p[0].name if p[0] else ""
                self.touches.append(appendable)
            self.top_buttons = [""]
            for o in self.device_provider.device_component._bank.options:
                if type(o) == str:
                    self.top_buttons.append(lambda: o)
                elif o:
                    self.top_buttons.append(lambda: o._name)
                else:
                    self.top_buttons.append(lambda: "")
            self.banks = []
            for option in self.component.device_component._bank._definition:
                if option:
                    self.banks.append(lambda option=option: option if self.toggled_state else "")
            self.bottom_buttons = []
            if len(self.banks) >= 8:
                if self.bottom_start_slice == 0:
                    self.bottom_buttons = self.banks[self.bottom_start_slice:self.bottom_end_slice] + [lambda: self.inc_slices()]
                else:
                    self.bottom_buttons = [lambda: self.dec_slices()] + self.banks[self.bottom_start_slice + 1:self.bottom_end_slice + 1] + [lambda: self.inc_slices()]
            self.special_device = getattr(Devices, self.selected_device, None)
            if self.special_device is not None:
                self.top_buttons, self.touches, self.bottom_buttons = self.special_device.update_controls(self.touches,
                                                                                                          self.top_buttons,
                                                                                                          self.bottom_buttons,
                                                                                                          self.device_component,
                                                                                                          self.toggled_state,
                                                                                                          log_message=self.log_message)
        except Exception as e:
            self.log_message(e)

    @listens("selected_mode")
    def open_close_device(self, mode):
        if mode:
            self.toggled_state = True if mode == "bank_selection" else False
            self.update_controls()
            self.send_midi(f"{self.selected_device} opened" if self.toggled_state else f"{self.selected_device} closed")

    def inc_slices(self):
        self.bottom_start_slice += 1
        if self.bottom_start_slice >= 2:
            self.bottom_end_slice += 1
        self.update_controls()
        self.send_midi("device banked right")
    def dec_slices(self):
        self.bottom_start_slice -= 1
        if self.bottom_start_slice >= 1:
            self.bottom_end_slice -= 1
        self.update_controls()
        self.send_midi("device banked left")


    def on_values_changed(self, value, control, control_list):
        if control_list == "touches":
            self.touching_param = control if value == 127 else None
            super(PushMonitoringDevice, self).on_values_changed(value, control, control_list)
        self.send_midi(getattr(self, control_list)[control]())




    @listens("parameters")
    def _on_device_parameters_changed(self):
        self.log_message("params changed")
        self.update_controls()

    @listens("device")
    def _on_device_changed(self):
        self.log_message("device changed")
        self._on_parameter_value_changed.replace_subjects([])
        self._on_options_value_changed.replace_subjects([])
        self.update_controls()

    @listens("options")
    def _on_options_changed(self, *args):
        self.log_message("options changed")
        self.update_controls()

    @listens("selected_mode")
    def _on_selected_mode_changed(self, mode):
        self.log_message("sel mode changed")
        self._on_parameter_value_changed.replace_subjects([])
        self._on_options_value_changed.replace_subjects([])
        self.selected_device = self.device_provider.selected_mode
        self.update_controls()

    @listens("selected_track")
    def _on_selected_track_changed(self):
        self.log_message("sel track changed")
        self.toggled_state = False
        self._on_parameter_value_changed.replace_subjects([])
        self._on_options_value_changed.replace_subjects([])
        self.update_controls()

    @listens_group("value")
    def _on_options_value_changed(self, parameter):
        self.log_message("options val changed")
        self.send_midi(f"{parameter.name} {self.parameter_to_string(parameter)}")

    @listens_group("value")
    def _on_parameter_value_changed(self, parameter):
        try:
            is_automation =  parameter.automation_state != Live.DeviceParameter.AutomationState.none
            parameters = [p.parameter for p in self.device_provider.parameters if self.device_provider]
            self.log_message(parameter.automation_state)
            if self.touching_param is not None and self.touching_param == parameters.index(parameter) and not is_automation:
                self.send_midi(f"{self.parameter_to_string(parameter)}")
                if is_automation and not self.song.is_playing:
                    self.send_midi(f"{self.parameter_to_string(parameter)} adding automation")

        except:
            pass

    def parameter_to_string(self, parameter):
        if parameter == None:
            return u''
        return unicode(parameter)

    def add_new_params(self):
        self.device_component = self.device_provider._device_component_modes[self.device_provider.selected_mode]
        parameters = [p.parameter for p in self.device_component.parameters]
        options = [o._parameter for o in self.device_component.options if o and hasattr(o, "_parameter")]
        options += [o._property_host for o in self.device_component.options if o and hasattr(o, "_property_host")]
        for p in parameters:
            if not self._on_parameter_value_changed.has_subject(p):
                self._on_parameter_value_changed.add_subject(p)

        for o in options:
            if not self._on_options_value_changed.has_subject(o):
                self._on_options_value_changed.add_subject(o)


    def disconnect(self):
        self.device_provider = None
        self._on_selected_track_changed.subject = None
        self.device_component = None
        self._on_device_parameters_changed.subject = None
        self._on_device_changed.subject = None
        self._on_selected_mode_changed.subject = None
        self._on_options_changed.subject = None
        self.selected_device = None
        self.special_device = None
        super(PushMonitoringDevice, self).disconnect()