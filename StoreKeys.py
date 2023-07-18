"""This class is used to store the currently pressed keys, and update any observers when this changes, callbacks can
be registered and unregistered with the provided methods."""


class StoreKeys:
    def __init__(self, initial_keys=[]):
        self._keys = initial_keys
        self._callbacks = []

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, new_keys):
        self._keys = new_keys
        self._update_observers(new_keys)

    def _update_observers(self, new_keys):
        for call in self._callbacks:
            call(new_keys)

    def register_callback(self, callback):
        self._callbacks.append(callback)

    def unregister_callback(self, callback):
        self._callbacks.remove(callback)


keys_pressed = StoreKeys()
