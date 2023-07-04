import punq

from PySimplePreview.view.controller.external_preview import ExternalPreviewWindowController


class ExternalPreviewWindowControllerFactory:
    def __init__(self, di: punq.Container):
        self.di = di
        self._external_windows = dict[str, ExternalPreviewWindowController]()
        self._previous_key = None

    def create(self, name: str):
        if name in self._external_windows or not name:
            return
        if self._previous_key and self._previous_key != name:
            self.remove(self._previous_key)
        self._previous_key = name
        controller = self.di.resolve(ExternalPreviewWindowController, preview_key=name)
        self._external_windows[name] = controller
        controller.refresh_layout()

    def remove(self, name: str = None):
        name = name or self._previous_key
        controller = self._external_windows.get(name)
        if not controller:
            return
        controller._handle_event(None, None)
        del self._external_windows[name]

    @property
    def values(self):
        return self._external_windows.values()
