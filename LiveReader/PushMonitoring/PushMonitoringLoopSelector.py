from pushbase.loop_selector_component import LoopSelectorComponent
from .PushMonitoringComponent import PushMonitoringComponent


class PushMonitoringLoopSelector(PushMonitoringComponent):

    def __init__(self, *a, **k):
        super(PushMonitoringLoopSelector, self).__init__(LoopSelectorComponent, *a, **k)


    def get_push_component(self, PushComponent):
        return [component for component in self.push._components if isinstance(component, PushComponent)]
