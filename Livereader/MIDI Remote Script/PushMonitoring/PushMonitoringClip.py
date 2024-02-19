from functools import partial

from Push2.clip_control import ClipControlComponent
from ableton.v2.base import listens, listens_group, task
from ableton.v2.control_surface import defaults

from .PushMonitoringComponent import PushMonitoringComponent
from .PushMonitoringLoopSelector import PushMonitoringLoopSelector
from ..utils import convert_to_note, convert_beat_time, modify_func


class PushMonitoringClip(PushMonitoringComponent):
    def __init__(self, song, pads, *a, **k):
        super(PushMonitoringClip, self).__init__(ClipControlComponent, *a, **k)
        self.song = song
        self._on_clip_slot_has_clip_changed.subject = self.song.view.highlighted_clip_slot
        self._on_selected_track_changed.subject = self.song.view
        self._on_selected_scene_changed.subject = self.song.view
        self._on_detail_clip_changed.subject = self.song.view
        self.loop_selector = PushMonitoringLoopSelector(push=self.push, log_message=self.log_message,
                                                        send_midi=self.send_midi)

        self._on_select_button_pressed.subject = self.select_button

        for loop_selector in self.loop_selector.component:
            self._on_note_page_index_changed.add_subject(loop_selector._paginator)

        self.main_paginator = None

        for component in self.loop_selector.component:
            if component._parent and component._parent.name == "Melodic_Component":
                self.melodic_paginator = component._paginator
                self.melodic_note_editors = component._parent._note_editors
                self.create_step_tasks(self.melodic_note_editors)

            elif component._parent and component._parent.name == "Drum_Step_Sequencer":
                self.step_seq_paginator = component._paginator
                self.step_note_editor = component._parent._note_editor
                self.create_step_tasks([self.step_note_editor])

            elif component._parent and component._parent.name == "":
                self.melodic_step_seq_paginator = component._paginator
                self.melodic_step_note_editor = component._parent._note_editor
                self.create_step_tasks([self.melodic_step_note_editor])


    def update_controls(self):
        if self.component._clip:
            self._on_clip_looping_changed.subject = self.component._clip
            if self.component._clip.looping:
                self.touches = ["Zoom", "Loop Position", "Loop Length", "Start Offset", None]
                self.top_buttons = [None, "Loop Off", "Crop", None, None, None, None, None]
            else:
                self.touches = ["Zoom", "Start", "End", None, None]
                self.top_buttons = [None, "Loop On", "Crop", None, None, None, None, None]
            if self.component._clip.is_audio_clip:
                self.touches += ["Warp", "Transpose", "Gain"]
                self.top_buttons[2] = None
            else:
                self.touches += [None, None, None]

    def create_step_tasks(self, note_editors):
        step_tasks = []

        def _on_press_step(editor, index):
            if not editor._step_duplicator.is_duplicating:
                step_tasks[index].restart()

        def _on_release_step(index):
            step_tasks[index].kill()
            self.update_controls()

        def pressed_steps(editor):
            if not self.main_modes.selected_mode == "clip":
                self.send_midi("clip mode not opened, open clip mode first to modify notes")
            self.send_midi("modifying note, use encoders to adjust values")
            self.touches = ["Nudge", "Length", "Fine", "Velocity", "Velocity Range", "Probability", None, None, None]

        for i, editor in enumerate(note_editors):
            editor._on_press_step = modify_func(editor._on_press_step,
                                                lambda editor=editor, i=i: _on_press_step(editor, i))
            editor._on_release_step = modify_func(editor._on_release_step, lambda i=i: _on_release_step(i))
            trigger = partial(pressed_steps, editor)
            step_tasks.append(editor._tasks.add(task.sequence(task.wait(defaults.MOMENTARY_DELAY),
                                                              task.run(trigger))).kill())

    @listens("has_clip")
    def _on_clip_slot_has_clip_changed(self):
        self.update_controls()

    @listens("selected_track")
    def _on_selected_track_changed(self):
        self.update_controls()

    @listens("selected_scene")
    def _on_selected_scene_changed(self):
        self.update_controls()

    @listens("detail_clip")
    def _on_detail_clip_changed(self):
        self.update_controls()

    @listens("looping")
    def _on_clip_looping_changed(self):
        self.generated_notes = self.notes_generator()
        self.update_controls()

    @listens_group("page_index")
    def _on_note_page_index_changed(self, paginator):
        if self.main_modes.selected_mode == "clip":
            self.send_midi(f"page {paginator.page_index + 1} press select button for details of notes on this page")
            self.generated_notes = self.notes_generator()
            self.main_paginator = paginator


    def notes_generator(self):
        clip_slot = self.song.view.highlighted_clip_slot
        page_start, page_end = ((
                                        self.main_paginator.page_index + 1) * self.main_paginator.page_length) - self.main_paginator.page_length, (
                                       self.main_paginator.page_index + 1) * self.main_paginator.page_length
        notes = clip_slot.clip.get_notes_extended(from_time=page_start, from_pitch=0, time_span=page_end,
                                                  pitch_span=128)
        for note in notes:
            yield note

    @listens("value")
    def _on_select_button_pressed(self, value):
        if value != 127:
            return
        clip_slot = self.song.view.highlighted_clip_slot
        if self.main_modes.selected_mode == "clip":
            if not clip_slot.has_clip:
                self.send_midi("no clip selected, input notes using sequencer to create a clip")
            elif clip_slot.clip.is_audio_clip:
                self.send_midi("audio clip selected")
            else:
                try:
                    note = next(self.generated_notes)
                    self.send_midi(f"note {convert_to_note(note.pitch)}, pad {int((note.start_time * 4) + 1)} across,  {self.component.midi_clip_controller._most_recent_editable_pitches.index(note.pitch) + 1} up")
                except StopIteration:
                    pass
                    # self.generated_notes = self.notes_generator()
                    # if len(self.generated_notes) != 0:
                    #     self._on_select_button_pressed(value)





    def disconnect(self):
        self.log_message("CLIP DISCONNECT")
        self.song = None
        self._on_clip_slot_has_clip_changed.subject = None
        self._on_selected_track_changed.subject = None
        self._on_selected_scene_changed.subject = None
        self._on_detail_clip_changed.subject = None
        self.loop_selector = None
        self._on_select_button_pressed.subject = None
        self._on_note_page_index_changed.subjects = None
        self.main_paginator = None
        super(PushMonitoringClip, self).disconnect()
