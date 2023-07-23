from .PushMonitoringComponent import PushMonitoringComponent
from Push2.mixer_control_component import MixerControlComponent
from ableton.v2.base import listens, listens_group
from ..utils import modify_func


class PushMonitoringMix(PushMonitoringComponent):
    def __init__(self, song, *a, **k):
        super(PushMonitoringMix, self).__init__(MixerControlComponent, *a, **k)
        self.song = song
        self.component._update_mixer_sections = modify_func(self.component._update_mixer_sections,
                                                            self.update_mixer_sections)
        self._on_selected_track_changed.subject = self.song.view
        self._on_items_changed.subject = self.push._session_ring
        self._on_selected_item_changed.subject = self.push._session_ring
        self._on_mix_mode_changed.subject = self.push._mix_modes


    def update_controls(self):
        self._on_track_volume_changed.subject = self.song.view.selected_track.mixer_device.volume
        self._on_track_panning_changed.subject = self.song.view.selected_track.mixer_device.panning
        self.update_mixer_sections()

    def update_mixer_sections(self):
        if self.push._mix_modes.selected_mode == "global":
            self.top_buttons = [lambda name=section._name: name for section in self.component._mixer_sections]

            while (len(self.top_buttons) < 8):
                self.top_buttons.append(lambda: None)
            self.top_buttons[7] = "cycle sends" if self.component.number_sends >= 6 else ""
        elif self.push._mix_modes.selected_mode == "track":
            self.top_buttons = [lambda: "Mix", lambda: "Input/Output", lambda: None, lambda: None, lambda: None, lambda: None, lambda: None, lambda: None]
            self.touches = [lambda: str(self.song.view.selected_track.mixer_device.volume.str_for_value(self.song.view.selected_track.output_meter_level)) if self.song.is_playing else "Volume", lambda: "Pan"]


    def on_values_changed(self, value, control, control_list):
        if value == 127:
            self.send_midi(getattr(self, control_list)[control]())

    @listens("selected_mode")
    def _on_mix_mode_changed(self, mode):
        if mode:
            self.send_midi(f"{mode} mixer mode")

    @listens("items")
    def _on_items_changed(self):
        self.update_controls()

    @listens("selected_item")
    def _on_selected_item_changed(self):
        self.update_controls()

    @listens("selected_track")
    def _on_selected_track_changed(self):
        self.update_controls()
        self.send_midi(f"{self.song.view.selected_track.name} track selected")

    @listens("value")
    def _on_track_volume_changed(self):
        parameter = self.song.view.selected_track.mixer_device.volume
        self.send_midi(f"{parameter.name} {parameter.str_for_value(parameter.value)}")

    @listens("value")
    def _on_track_panning_changed(self):
        parameter = self.song.view.selected_track.mixer_device.panning
        self.send_midi(f"{parameter.name} {parameter.str_for_value(parameter.value)}")


    def disconnect(self):
        self._on_selected_track_changed.subject = None
        self._on_items_changed.subject = None
        self._on_selected_item_changed.subject = None
        self._on_mix_mode_changed.subject = None
        self.song = None
        super(PushMonitoringMix, self).disconnect()


