import PySimpleGUI as sg


class WindowHolder:
    def __init__(self):
        self._window: sg.Window = None
        self._new_window: sg.Window = None

    @property
    def window(self):
        return self._window

    def swap(self, new_window: sg.Window):
        self._new_window = new_window

    def step(self):
        if self._new_window:
            result = self._read(self._new_window, 0)
            self._new_window.set_alpha(1)
            self.close()
            self._window = self._new_window
            self._new_window = None
            return result
        if not self._window or self.window.was_closed():
            return None
        return self._read(self._window, 1)

    def _read(self, window, timeout):
        return window.read(timeout)

    def close(self):
        if self._window:
            self.window.close()
