from .PushMonitoringComponent import PushMonitoringComponent
from Push2.scales_component import ScalesComponent
from ableton.v2.base import listens

from ..consts import ROOT_NOTES



class PushMonitoringScales(PushMonitoringComponent):

    def __init__(self, *a, **k):
        super(PushMonitoringScales, self).__init__(ScalesComponent, *a, **k)
        self.component = self.get_push_component(self.PushComponent)
        self._on_selected_scale_index_changed.subject = self.component
        self._on_selected_root_note_index_changed.subject = self.component
        self._on_selected_layout_index_changed.subject = self.component

    def update_controls(self):
        pass

    def on_values_changed(self, value, control, control_list):
        pass

    @listens("selected_scale_index")
    def _on_selected_scale_index_changed(self):
        index = self.component._selected_scale_index
        scale = self.component._scale_name_list[index]
        self.log_message("WOOOOO")
        self.send_midi(f"Scale set to {scale}")

    @listens("selected_root_note_index")
    def _on_selected_root_note_index_changed(self):
        index = self.component._selected_root_note_index
        root_note = ROOT_NOTES[index]
        self.send_midi(f"Scales root note set to {root_note}")

    @listens("selected_layout_index")
    def _on_selected_layout_index_changed(self):
        index = self.component._selected_layout_index
        layout = self.component._layouts[index].name
        self.send_midi(f"Scales layout set to {layout}")
