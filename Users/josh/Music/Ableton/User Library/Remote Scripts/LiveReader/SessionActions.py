from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

from .RoutingActions import RoutingActions
from .MixerActions import MixerActions
from .key_consts import *


class SessionActions(ControlSurfaceComponent):
    __module__ = __name__

    def __init__(self, c_instance):
        ControlSurfaceComponent.__init__(self, c_instance)

        self._routing = RoutingActions(c_instance)
        self._mixer = MixerActions(c_instance)
        self._c_instance = c_instance
        self.track = self.song().view.selected_track
        self.track_name = self.track.name
        self.selected_tracks = []
        self.select_left = None
        self.scene = self.song().view.selected_scene
        self.clip_slot = self.song().view.highlighted_clip_slot
        self.has_clip = []
        self.header_selected = False
        self.renaming = None
        self.new_name = ''


        self.sub_mode = 'Mixer'
        self.sub_modes = {'Routing': self._routing.get_action,
                          'Mixer': self._mixer.get_action}

        self.actions = {UP_ARROW: self.up_arrow,
                        DOWN_ARROW: self.down_arrow,
                        LEFT_ARROW: self.left_arrow,
                        RIGHT_ARROW: self.right_arrow,
                        ALT_UP: self.alt_up,
                        ALT_DOWN: self.alt_down,
                        ALT_LEFT: self.alt_left,
                        ALT_RIGHT: self.alt_right,
                        CMD_R: self.rename,
                        ENTER: self.enter,
                        CMD_SHIFT_R: self.add_midi_clip,
                        DEL: self.delete,
                        BACKSPACE: self.delete,
                        COMMA: self.mute_selected,
                        PERIOD: self.solo_selected,
                        FORWARDSLASH: self.arm_selected
                        # (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0): self.selecting,
                        # (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0): self.selecting_right,
                        # (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0): self.selecting_left
                        }

    def disconnect(self):
        self._mixer = None
        self._routing = None
        super(SessionActions, self).disconnect()


    def log(self, msg):
        self._c_instance.log_message(str(msg))

    def get_action(self, midi_bytes):
        if midi_bytes not in self.actions.keys() and midi_bytes[21:] != (0, 0):

            return self.char_pressed(midi_bytes)
        else:
            return self.actions[midi_bytes]()

    def char_pressed(self, midi_bytes):
        ASCII = chr((midi_bytes[21] * 128) + midi_bytes[22])
        if self.renaming:
            if ASCII.isalpha():
                self.new_name += ASCII
                return ASCII

    def set_sub_mode(self, sub_mode):
        self.sub_mode = sub_mode
        if self.sub_mode == 'Routing':
            return self._routing.make_routing_lists()

        if self.sub_mode == 'Mixer':
            return self._mixer.make_mixer_list()

    def up_arrow(self):
        scenes = self.song().scenes
        if self.renaming:
            return self.renamed()

        if self.track == self.song().master_track:
            if self.scene == self.song().scenes[0]:
                self.header_selected = True
                return 'track header selected'
            else:
                self.scene = self.song().view.selected_scene
                return 'scene {0} name {1}'.format(list(scenes).index(self.scene) + 1, self.scene.name)

        if self.scene == self.song().scenes[0] and not self.header_selected:
            self.header_selected = True
            return 'track header selected'
        elif self.header_selected:
            return 'track header already selected'
        else:

            self.clip_slot = self.song().view.highlighted_clip_slot
            self.scene = self.song().view.selected_scene
            if self.clip_slot.has_clip:
                if self.clip_slot not in self.has_clip:
                    self.has_clip.append(self.clip_slot)
                if self.clip_slot.clip.name == '':
                    return 'unnamed clip in scene {0} named {1}'.format(list(scenes).index(self.scene) + 1,
                                                                        self.scene.name)
                else:
                    return 'clip {0} in scene {1} named {2}'.format(self.clip_slot.clip.name,
                                                                    list(scenes).index(self.scene) + 1, self.scene.name)
            elif self.clip_slot in self.has_clip:
                self.has_clip.remove(self.clip_slot)
            return 'empty clip slot in scene {0} named {1}'.format(list(scenes).index(self.scene) + 1, self.scene.name)

    def down_arrow(self):
        scenes = self.song().scenes
        if self.renaming:
            return self.renamed()

        if self.track == self.song().master_track:
            if self.header_selected == True:
                self.header_selected = False
            self.scene = self.song().view.selected_scene
            return 'scene {0} name {1}'.format(list(scenes).index(self.scene) + 1, self.scene.name)

        if self.header_selected == True:
            self.header_selected = False
        self.clip_slot = self.song().view.highlighted_clip_slot
        self.scene = self.song().view.selected_scene
        if self.clip_slot.has_clip:
            if self.clip_slot not in self.has_clip:
                self.has_clip.append(self.clip_slot)
            if self.clip_slot.clip.name == '':
                return 'unnamed clip in scene {0} named {1}'.format(list(scenes).index(self.scene) + 1, self.scene.name)
            else:
                return 'clip {0} in scene {1} named {2}'.format(self.clip_slot.clip.name,
                                                                list(scenes).index(self.scene) + 1, self.scene.name)
        elif self.clip_slot in self.has_clip:
            self.has_clip.remove(self.clip_slot)
        return 'empty clip slot in scene {0} named {1}'.format(list(scenes).index(self.scene) + 1, self.scene.name)

    def left_arrow(self):
        self.track = self.song().view.selected_track
        self.track_name = self.track.name
        self._routing.make_routing_lists()
        self._mixer.make_mixer_list()
        return self.track.name

    def right_arrow(self):
        self.track = self.song().view.selected_track
        self.track_name = self.track.name
        self._routing.make_routing_lists()
        self._mixer.make_mixer_list()
        return self.track.name

    def rename(self):
        scenes = self.song().scenes
        if self.track == self.song().master_track:
            if self.header_selected:
                return 'cant rename master track'
            else:
                self.renaming = 'renamed scene {0} to '.format(list(scenes).index(self.scene) + 1)
                return 'renaming scene {0}'.format(list(scenes).index(self.scene) + 1)

        if self.header_selected:
            self.renaming = 'renamed {0} to '.format(self.track.name)
            return 'renaming {0}'.format(self.track.name)

        elif self.clip_slot.has_clip:
            self.renaming = 'renamed clip on {0} scene {1} to '.format(self.track.name,
                                                                       list(scenes).index(self.scene) + 1)
            return 'renaming clip on {0} scene {1}'.format(self.track.name, list(scenes).index(self.scene) + 1)
        else:
            return 'nothing to rename'

    def renamed(self):

        renamed = self.renaming
        new_name = self.new_name
        self.renaming = None
        self.new_name = ''
        return renamed + new_name

    def enter(self):
        if self.renaming:
            return self.renamed()

    def add_midi_clip(self):
        scenes = self.song().scenes
        if self.track.has_midi_input:
            if self.header_selected:
                return "can't add midi clip when selected on track header"
            if self.clip_slot in self.has_clip:
                return 'clip slot already has midi clip'

            else:
                self.has_clip.append(self.clip_slot)
                return 'midi clip added {0} scene {1} named {2}'.format(self.track.name,
                                                                        list(scenes).index(self.scene) + 1,
                                                                        self.scene.name)
        else:
            return 'must select a midi track to add a midi clip'

    def add_scene(self):
        if not self.header_selected:
            self.clip_slot = self.song().view.highlighted_clip_slot
            self.scene = self.song().view.selected_scene
            scenes = self.song().scenes
            return 'empty scene added at position {0}'.format(list(scenes).index(self.scene) + 1)
        else:
            return 'cant insert scene when track header selected'

    def delete(self):
        scenes = self.song().scenes

        if self.track == self.song().master_track:
            if self.header_selected:
                return 'cant delete master track'
            else:
                return 'deleted scene {0}'.format(list(scenes).index(self.scene))

        if self.header_selected:
            track_name = self.track_name
            self.track = self.song().view.selected_track
            self.track_name = self.track.name
            return 'deleted {0}'.format(track_name)

        elif self.clip_slot in self.has_clip:
            self.has_clip.remove(self.clip_slot)
            return 'deleted clip on {0} scene {1} named {2}'.format(self.track.name, list(scenes).index(self.scene) + 1,
                                                                    self.scene.name)
        else:
            return 'nothing to delete'

    # def selecting(self):
    #     self.selected_tracks = [self.track_name]
    #     return 'selecting {0}'.format(' '.join(map(str, self.selected_tracks)))
    #
    # def selecting_right(self):
    #     if self.header_selected and not self.track == self.song().master_track:
    #         self.track = self.song().view.selected_track
    #         self.track_name = self.track.name
    #         if self.select_left and len(self.selected_tracks) != 1:
    #             del self.selected_tracks[0]
    #         else:
    #             self.select_left = False
    #             self.selected_tracks.append(self.track_name)
    #         return 'selected {0}'.format(' '.join(map(str, self.selected_tracks)))
    #
    # def selecting_left(self):
    #     if self.header_selected and not self.track == self.song().master_track:
    #         self.track = self.song().view.selected_track
    #         self.track_name = self.track.name
    #         if len(self.selected_tracks) == 1:
    #             self.select_left = True
    #             self.selected_tracks.insert(0, self.track_name)
    #         elif self.select_left:
    #             self.selected_tracks.insert(0, self.track_name)
    #         else:
    #             self.selected_tracks = self.selected_tracks[:-1]
    #         return 'selected {0}'.format(' '.join(map(str, self.selected_tracks)))

    def alt_up(self):
        return self.sub_modes[self.sub_mode](ALT_UP)
    def alt_down(self):
        return self.sub_modes[self.sub_mode](ALT_DOWN)
    def alt_left(self):
        return self.sub_modes[self.sub_mode](ALT_LEFT)
    def alt_right(self):
        return self.sub_modes[self.sub_mode](ALT_RIGHT)


    def mute_selected(self):
        mute = {0: 'mute off',
                1: 'mute on'}
        self.track.mute = 0 if self.track.mute else 1
        return '{0} {1}'.format(self.track.name, mute[self.track.mute])

    def solo_selected(self):
        solo = {0: 'solo off',
                1: 'solo on'}
        self.track.solo = 0 if self.track.solo else 1
        return '{0} {1}'.format(self.track.name, solo[self.track.solo])

    def arm_selected(self):
        arm = {0: 'arm off',
               1: 'arm on'}
        self.track.arm = 0 if self.track.arm else 1
        return '{0} {1}'.format(self.track.name, arm[self.track.arm])
