from ableton.v2.control_surface import PitchParameter, InternalParameterBase


class WavetableDevice:
    def update_controls(self, touches, top_buttons, bottom_buttons, device_component, toggled_state, log_message):
        log_message("wavetable")
        for index, parameter in enumerate(device_component.parameters):
            log_message(self.is_parameter_modulatable(parameter.parameter, device_component))
            if self.is_parameter_modulatable(parameter.parameter, device_component):
                touches[index] += ", can be added to mod matrix"
                if not toggled_state:
                    touches[index] += ", expand device first using top button 1"

        return top_buttons, touches, bottom_buttons

    @staticmethod
    def is_parameter_modulatable(param, device_component):
        if param is None:
            return False
        if isinstance(param, PitchParameter):
            return True
        if isinstance(param, InternalParameterBase):
            return False
        return device_component._decorated_device._live_object.is_parameter_modulatable(param)
