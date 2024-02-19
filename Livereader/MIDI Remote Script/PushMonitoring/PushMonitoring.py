from ableton.v2.control_surface import Component
from ableton.v2.base import depends, nop, listens
from Push2.push2 import Push2
from Push2.browser_component import BrowserComponent
from Push2.device_component_provider import DeviceComponentProvider
from Push2.clip_control import ClipControlComponent
from Push2.notification_component import NotificationComponent
from Push2.scales_component import ScalesComponent
from ableton.v2.control_surface.mode import ModesComponent

from Livereader.consts import ROOT_NOTES


def get_push_component(push, ClassComponent):
    return [component for component in push._components if isinstance(component, ClassComponent)][0]


class RegisterMode():
    def __init__(self, push, name, instance, register_slot, control, slots_to_register, log, send_midi):
        self.push = push
        self.name = name
        self.instance = instance
        self.slots_to_register = slots_to_register
        self.log = log
        self.send_midi = send_midi
        self.register_slot = register_slot
        self.registered_slots = []
        self.register_slot(control, self.register_slots, "value")

    def register_slots(self, value):
        if value == 127:
            self.send_midi(f"{self.name.split('_')[0]} pressed")
            component = get_push_component(self.push, self.instance)
            if component.name in ["Browser", "Scales"]:
                self.send_midi(f"{component.name} open" if component._is_enabled else f"{component.name} closed")
            for slot in self.slots_to_register:
                if slot and slot.get("property") and slot not in self.registered_slots:
                    subject = slot.get("subject", component)
                    self.register_slot(subject, lambda callback=slot["callback"], comp=component: callback(comp),
                                       slot["property"])
                    self.registered_slots.append(slot)
                slot["callback"](component)


class PushMonitoring(Component):
    @depends(log_message=None, send_midi=None)
    def __init__(self, log_message, send_midi, *a, **k):
        super(PushMonitoring, self).__init__(*a, **k)
        self.log = log_message
        self.send_midi = send_midi
        self.touches = []
        self.top_buttons = []
        self.bottom_buttons = []
        self.push = None
        self.registered_slots = []

        self.mode_buttons = {
            "Browse_Mode_Button": {"instance": BrowserComponent, "slots_to_register": [
                {"callback": self.browser_focused_item_changed, 'property': 'focused_item'},
                {"callback": self.clear_controls}]},


            "Session_Mode_Button": {"instance": type(None), "slots_to_register": []},
            "Device_Mode_Button": {"instance": DeviceComponentProvider, "slots_to_register": [
                {"callback": self._update_parameter_banks, "property": "parameters"},
                {"callback": self._update_parameter_banks, "property": "device"},
                {"callback": self.clear_controls}
            ]},
            "Clip_Mode_Button": {"instance": ClipControlComponent, "slots_to_register": [
                {"callback": self.update_controls_for_clips, "property": "has_clip",
                 "subject": self.song.view.highlighted_clip_slot},
                {"callback": self.update_controls_for_clips, "property": "selected_track",
                 "subject": self.song.view},
                {"callback": self.update_controls_for_clips, "property": "selected_scene",
                 "subject": self.song.view},
                {"callback": self.update_controls_for_clips, "property": "detail_clip",
                 "subject": self.song.view}]},

            "Note_Mode_Button": {"instance": type(None), "slots_to_register": []},
            "Scale_Presets_Button": {"instance": ScalesComponent, "slots_to_register": [
                {"callback": self.scales_scale_changed, "property": "selected_scale_index"},
                {"callback": self.scales_root_note_changed, "property": "selected_root_note_index"},
                {"callback": self.scales_layout_index_changed, "property": "selected_layout_index"},
                {"callback": self.clear_controls}]},

        }

    def get_push_instance(self):
        for i, control_surface in enumerate(self.application.control_surfaces):
            if control_surface and isinstance(control_surface, Push2):
                self.push = control_surface
                break
        else:  # No Break
            # self.log("No push detected")
            return
        if self.push._initialized:
            self.register_controls()
            self.register_components()

    def register_controls(self):
        for control in self.push.controls:
            if control.name != "":
                self.log(control.name)
            if control.name in self.mode_buttons:
                RegisterMode(self.push, control.name, self.mode_buttons[control.name]['instance'], self.register_slot,
                             control, self.mode_buttons[control.name]['slots_to_register'], self.log, self.send_midi)
            elif "Track_Control_Touch_" in control.name:
                self.register_slot(control,
                                   lambda value, control=control._msg_identifier: self.midi_value_changed(value,
                                                                                                          control,
                                                                                                          self.touches),
                                   u'value')
            elif "Track_State_Button" in control.name and control.name != "Track_State_Buttons":
                self.register_slot(control,
                                   lambda value, control=control._msg_identifier - 102: self.midi_value_changed(value,
                                                                                                                control,
                                                                                                                self.top_buttons),
                                   u'value')
            elif "Track_Select_Button" in control.name and control.name != "Track_Select_Buttons":
                self.register_slot(control,
                                   lambda value, control=control._msg_identifier - 20: self.midi_value_changed(value,
                                                                                                               control,
                                                                                                               self.bottom_buttons),
                                   u'value')

            elif "_Clip_" in control.name:
                self.register_slot(control, lambda value, control=control: self.clip_button_pressed(value, control),
                                   u'value')
                if control.name != "":
                    self.log(control.name)

                self.send_midi("Push ready")

    def register_components(self):
        notification_component = get_push_component(self.push, NotificationComponent)
        modes_component = [component for component in self.push._components if
                          isinstance(component, ModesComponent) and component._mode_list == ['mix', 'clip', 'device',
                                                                                             'browse', 'add_device',
                                                                                             'add_track', 'user']][0]

        self.register_slot(notification_component, lambda: self.show_notification(notification_component), "message")
        self.register_slot(modes_component, lambda *args: self.main_mode_changed(modes_component, args), "selected_mode")

    def show_notification(self, component):
        if component._show_notification:
            self.log(component._message)
            self.send_midi(component._message)

    def main_mode_changed(self, component, args):
        self.log("SELECTED_MODE_CHANGED")
        self.log(args)
        self.log(component.selected_mode)

    def browser_focused_item_changed(self, component):
        index = component._focused_list_index
        _list = component._lists[index]
        selected_index = _list._selected_index
        focused_item = _list._items[selected_index]
        self.log(f"{focused_item.name} on encoder {index + 3}")
        self.send_midi(f"Browser item {focused_item.name} on encoder {index + 3}")

    def scales_scale_changed(self, component):
        index = component._selected_scale_index
        scale = component._scale_name_list[index]
        self.send_midi(f"Scale set to {scale}")

    def scales_root_note_changed(self, component):
        index = component._selected_root_note_index
        root_note = ROOT_NOTES[index]
        self.send_midi(f"Scales root note set to {root_note}")

    def scales_layout_index_changed(self, component):
        index = component._selected_layout_index
        layout = component._layouts[index].name
        self.send_midi(f"Scales layout set to {layout}")

    def update_controls_for_clips(self, component):
        if component and component._clip:
            slot = (component._clip, lambda: self.update_controls_for_clips(component), "looping")
            if slot not in self.registered_slots:
                self.register_slot(*slot)
            if component._clip.looping:
                self.touches = ["Zoom", "Loop Position", "Loop Length", "Start Offset", None]
                self.top_buttons = [None, "Loop Off", "Crop", None, None, None, None, None]
            else:
                self.touches = ["Zoom", "Start", "End", None, None]
                self.top_buttons = [None, "Loop On", "Crop", None, None, None, None, None]
            if component._clip.is_audio_clip:
                self.touches += ["Warp", "Transpose", "Gain"]
                self.top_buttons[2] = None
            else:
                self.touches += [None, None, None]

    def _update_parameter_banks(self, component):
        try:
            self.touches = []
            for p in component.device_component._bank.parameters:
                self.touches.append(p[0].name if p[0] else "")
            self.top_buttons = [""]
            for o in component.device_component._bank.options:
                if type(o) == str:
                    self.top_buttons.append(o)
                elif o:
                    self.log(o.__dict__)
                    self.top_buttons.append(o._name)
            self.bottom_buttons = []
            self.bottom_buttons = [o for o in component.device_component._bank._definition if o]
        except Exception as e:
            self.log(e)

    def clip_button_pressed(self, value, control):
        if value > 0:
            self.touches = ["Nudge", "Length", "Fine", "Velocity", "Velocity range", "Probability", None, None]
        else:
            self.update_controls_for_clips(get_push_component(self.push, ClipControlComponent))

    def clear_controls(self, component):
        self.touches = []
        self.top_buttons = []
        self.bottom_buttons = []

    def midi_value_changed(self, value, control, control_list):
        self.log(control_list)
        try:
            if value == 127:
                self.send_midi(control_list[control])
        except IndexError:
            pass
