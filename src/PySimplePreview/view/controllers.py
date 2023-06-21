import time
from queue import Queue
from typing import Callable

import PySimpleGUI as sg

from src.PySimplePreview.data.config_storage import ConfigStorage
from src.PySimplePreview.data.previews_storage import PreviewsStorage
from src.PySimplePreview.domain.model.preview import LayoutProvider
from src.PySimplePreview.view.layouts import get_settings_layout, get_preview_layout_frame, get_nocontent_layout
from src.PySimplePreview.view.models import map_config_to_view, ListItem


class PreviewWindowController:
    def __init__(self):
        self._configs_storage = ConfigStorage.get()
        self._previews_storage = PreviewsStorage.get()
        self._window: sg.Window = None
        self.queue = Queue()

    @property
    def _config(self):
        return self._configs_storage.config

    @property
    def _previews(self):
        return self._previews_storage.previews

    def _swap_window(self, value):
        if self._window:
            self._window.close()
            self._window = None
        self._window = value

    def make_layout(self, layout: Callable[[], list[list]]):
        return [
            *get_settings_layout(
                map_config_to_view(self._config),
                ListItem.wrap_map(zip(self._previews.previews,
                                      self._previews.names))
            ),
            [get_preview_layout_frame(layout)],
        ]

    @property
    def layout(self) -> LayoutProvider | None:
        if not self._config.last_preview_key:
            self._config.last_preview_key = self._previews.first_preview_key
            self._configs_storage.save()
        new_layout = self._previews.get(self._config.last_preview_key)
        return new_layout.layout if new_layout else None

    @layout.setter
    def layout(self, value: LayoutProvider):
        self.queue.put_nowait(value)

    def _set_layout(self, layout: LayoutProvider):
        if self._config.theme:
            sg.theme(self._config.theme)
        window = sg.Window(
            "Python Simple Preview",
            self.make_layout(layout),
            keep_on_top=True,
            location=self._config.location,
            size=self._config.size,
            resizable=True,
            finalize=True,
        )
        self._swap_window(window)
        self._window.bind('<Configure>', "Configure")

    def step(self):
        if not self.queue.empty():
            self._set_layout(self.queue.get_nowait())
        if self._window:
            try:
                event, values = self._window.read(1)
                self._handle_event(event, values)
            except Exception as e:
                print(e)
        else:
            time.sleep(1)

    def _handle_event(self, event, values):
        if event is None:
            self._window = None
        elif event == "theme":
            self._config.theme = values[event]
            self._configs_storage.save()
            self.refresh_layout()
        elif event == "preview":
            self._config.last_preview_key = values[event].value
            self._configs_storage.save()
            self.refresh_layout()
        elif event == "Configure":
            self._config.location = self._window.current_location(True)
            self._config.size = self._window.size
            self._configs_storage.save()

    def refresh_layout(self):
        self.layout = self.layout or get_nocontent_layout
