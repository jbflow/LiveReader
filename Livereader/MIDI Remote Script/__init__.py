import Live
from .LiveReader import LiveReader
from ableton.v2.control_surface.capabilities import SUGGESTED_PORT_NAMES_KEY

def get_capabilities():
    return {SUGGESTED_PORT_NAMES_KEY: [u'LiveReader']}


def create_instance(c_instance):
    return LiveReader(c_instance)
