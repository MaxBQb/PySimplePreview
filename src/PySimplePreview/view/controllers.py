import time
from queue import Queue
from typing import Callable

import PySimpleGUI as sg

from src.PySimplePreview.data.config_storage import ConfigStorage
from src.PySimplePreview.data.previews_storage import PreviewsStorage
from src.PySimplePreview.domain.model.preview import LayoutProvider
from src.PySimplePreview.view.layouts import get_settings_layout, get_preview_layout_frame, get_nocontent_layout
from src.PySimplePreview.view.models import map_config_to_view, ListItem, shorten_preview_names


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


class PreviewWindowController:
    def __init__(self):
        self._configs_storage = ConfigStorage.get()
        self._previews_storage = PreviewsStorage.get()
        self._window_holder = WindowHolder()
        self.queue = Queue()

    @property
    def _config(self):
        return self._configs_storage.config

    @property
    def _previews(self):
        return self._previews_storage.previews

    def make_layout(self, layout: Callable[[], list[list]]):
        config = map_config_to_view(self._config)
        if self._previews.previews and config.preview_key:
            names = shorten_preview_names(self._previews.previews)
            name = names[self._previews.previews.index(self._config.last_preview_key)]
            config.preview_key.name = name
        return [
            *get_settings_layout(
                config,
                ListItem.wrap_map(zip(self._previews.previews, names))
            ),
            [get_preview_layout_frame(layout, config.preview_key.value)],
        ]

    @property
    def layout(self) -> LayoutProvider | None:
        if not self._config.last_preview_key or\
                self._config.last_preview_key not in self._previews.previews:
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
            alpha_channel=0.0,
        )
        window.bind('<Configure>', "Configure")
        self._window_holder.swap(window)

    def step(self):
        if not self.queue.empty():
            self._set_layout(self.queue.get_nowait())
        try:
            result = self._window_holder.step()
            if result:
                event, values = result
                self._handle_event(event, values)
            else:
                time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)

    def _handle_event(self, event, values):
        if event is None:
            self._window_holder.close()
        elif event == "theme":
            self._config.theme = values[event]
            self._configs_storage.save()
            self.refresh_layout()
        elif event == "preview":
            self._config.last_preview_key = values[event].value
            self._configs_storage.save()
            self.refresh_layout()
        elif event == "Configure":
            self._config.location = self._window_holder.window.current_location(True)
            self._config.size = self._window_holder.window.size
            self._configs_storage.save()

    def refresh_layout(self):
        self.layout = self.layout or get_nocontent_layout
