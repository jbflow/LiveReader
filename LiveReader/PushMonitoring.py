from ableton.v2.control_surface import Component
from ableton.v2.base import depends, nop
from Push2.push2 import Push2
from Push2.browser_component import BrowserComponent
from Push2.notification_component import NotificationComponent
from Push2.scales_component import ScalesComponent
from .consts import ROOT_NOTES

class RegisterMode():
    def __init__(self, push, name, instance, register_slot, control, listener_callbacks, log, send_midi):
        self.push = push
        self.name = name
        self.instance = instance
        self.listener_callbacks = listener_callbacks
        self.log = log
        self.send_midi = send_midi
        self.register_slot = register_slot
        self.register_slot(control, self.mode_button_pressed, u'value')
        self.registered_properties = []


    def mode_button_pressed(self, value):
        if value == 127:
            self.send_midi(f"{self.name.split('_')[0]} pressed")
            for component in self.push._components:
                if isinstance(component, self.instance):
                    if component.name in ["Browser", "Scales"]:
                        self.send_midi(f"{component.name} open" if component._is_enabled else f"{component.name} closed")
                    for listener in self.listener_callbacks:
                        if listener['property'] not in self.registered_properties:
                            # self.log('registering listener slot')
                            self.register_slot(component, lambda callback=listener["callback"], comp=component: callback(comp), listener["property"])
                            self.registered_properties.append(listener['property'])


class PushMonitoring(Component):
    
    @depends(log_message=None, send_midi=None)
    def __init__(self, log_message, send_midi, *a, **k):
        super(PushMonitoring, self).__init__(*a, **k)
        self.log = log_message
        self.send_midi = send_midi
        self.push = None

        self.mode_buttons = {"Browse_Mode_Button": {"instance": BrowserComponent, "listener_callbacks": [{"callback": self.browser_focused_item_changed, 'property': 'focused_item'}]},
                             "Session_Mode_Button": {"instance": type(None), "listener_callbacks": []},
                             "Device_Mode_Button": {"instance": type(None), "listener_callbacks": []},
                             "Clip_Mode_Button": {"instance": type(None), "listener_callbacks": []},
                             "Note_Mode_Button": {"instance": type(None), "listener_callbacks": []},
                             "Layout": {"instance": NotificationComponent, "listener_callbacks": [{"callback": self.layout_sequencer_changed, "property": "message"}]},
                             "Scale_Presets_Button": {"instance": ScalesComponent, "listener_callbacks": [{"callback": self.scales_scale_changed, "property": "selected_scale_index"}, 
                                                                                                          {"callback": self.scales_root_note_changed, "property": "selected_root_note_index"},
                                                                                                          {"callback": self.scales_layout_index_changed, "property": "selected_layout_index"}]}
                             }

    def get_push_instance(self):
        for i, control_surface in enumerate(self.application.control_surfaces):
            if control_surface and isinstance(control_surface, Push2):
                self.push = control_surface
                break
        else: # No Break
            # self.log("No push detected")
            return
        if self.push._initialized:
            self.send_midi("Push detected and initialized, Registering components")
            self.register_slots()


    def register_slots(self):
            for control in self.push.controls:
                # if hasattr(control, "name") and control.name != "":
                #     self.log(control.name)
                if control.name in self.mode_buttons:
                    RegisterMode(self.push, control.name, self.mode_buttons[control.name]['instance'], self.register_slot, control, self.mode_buttons[control.name]['listener_callbacks'], self.log, self.send_midi)
            self.send_midi("Push ready")
            

    def show_notification(self, component):
        if component._show_notification:
            self.log(component._message)
            self.send_midi(component._message)

    def browser_focused_item_changed(self, component):
        index = component._focused_list_index
        _list = component._lists[index]
        selected_index = _list._selected_index
        focused_item = _list._items[selected_index]
        self.log(f"{focused_item.name} on encoder {index + 3}")
        self.send_midi(f"Browser item {focused_item.name} on encoder {index + 3}")
    def layout_sequencer_changed(self, component):
        self.show_notification(component)


    def scales_scale_changed(self, component):
        index = component._selected_scale_index
        scale = component._scale_name_list[index]
        # self.log(scale)
        self.send_midi(f"Scale set to {scale}")

    def scales_root_note_changed(self, component):
        index = component._selected_root_note_index
        root_note = ROOT_NOTES[index]
        # self.log(root_note)
        self.send_midi(f"Scales root note set to {root_note}")


    def scales_layout_index_changed(self, component):
        index = component._selected_layout_index
        layout = component._layouts[index].name
        # self.log(layout)
        self.send_midi(f"Scales layout set to {layout}")

    

