from Push2.browser_component import BrowserComponent, FolderBrowserItem
from ableton.v2.base import listens

from .PushMonitoringComponent import PushMonitoringComponent


class PushMonitoringBrowser(PushMonitoringComponent):
    def __init__(self, *a, **k):
        self._args = a
        self._kwargs = k

    def enter(self):
        super(PushMonitoringBrowser, self).__init__(BrowserComponent, *self._args, **self._kwargs)
        super(PushMonitoringBrowser, self).enter()

        self._on_focused_item_changed.subject = self.component


        self._on_prehear_enabled_changed.subject = self.component

    def update_controls(self):
        pass

    @listens("focused_item")
    def _on_focused_item_changed(self):
        index = self.component._focused_list_index
        _list = self.component._lists[index]
        selected_index = _list._selected_index
        focused_item = _list._items[selected_index]
        msg = focused_item.name
        if focused_item.is_loadable:
            msg += ", press bottom button 8 to load."
        if isinstance(focused_item, FolderBrowserItem):
            msg += " press right arrow to explore."
        self.send_midi(msg)

    @listens("prehear_enabled")
    def _on_prehear_enabled_changed(self):
        self.send_midi("preview on" if self.component.prehear_button.is_toggled else "preview off")

