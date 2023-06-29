import os.path
import time
from abc import ABCMeta, abstractmethod
from pathlib import Path
from queue import Queue
from typing import Callable

import PySimpleGUI as sg

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.model.config import is_valid_project, Config
from PySimplePreview.domain.model.position import Position
from PySimplePreview.domain.model.preview import LayoutProvider
from PySimplePreview.view.layouts import get_settings_layout, get_preview_layout_frame, get_nocontent_layout
from PySimplePreview.view.models import map_config_to_view, ListItem, shorten_preview_names, PositionViewDTO


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


class BaseController(metaclass=ABCMeta):
    def __init__(self):
        self._configs_storage = ConfigStorage.get()
        self._window_holder = WindowHolder()
        self.queue = Queue()
        self._configs_storage.on_update(self._on_config_update)

    def _on_config_update(self, config: Config):
        self.refresh_layout()

    @abstractmethod
    def _set_layout(self, layout):
        pass

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
            print("Error in controller", f"({self.name}):", e)
            time.sleep(1)

    @property
    def _position(self):
        return PositionViewDTO.from_domain(self._config.positions.get(self.name, Position()))

    @_position.setter
    def _position(self, value: Position):
        self._config.positions[self.name] = value
        self._configs_storage.save(False)

    @property
    def name(self):
        return self.__class__.__name__

    def _handle_event(self, event, values):
        if event == "Configure":
            self._position = Position(
                self._window_holder.window.size,
                self._window_holder.window.current_location(True),
            )
        elif event is None:
            self._window_holder.close()

    def refresh_layout(self):
        self.layout = self.layout or get_nocontent_layout

    @abstractmethod
    def _get_layout(self):
        pass

    @property
    def layout(self) -> LayoutProvider | None:
        return self._get_layout()

    @layout.setter
    def layout(self, value: LayoutProvider):
        self.queue.put_nowait(value)

    def _set_window(self, window: sg.Window):
        window.bind('<Configure>', "Configure")
        self._window_holder.swap(window)

    @property
    def _config(self):
        return self._configs_storage.config


class ExternalPreviewWindowController(BaseController):
    def __init__(self, preview_key):
        super().__init__()
        self.__key = preview_key
        self._previews_storage = PreviewsStorage.get()

    @property
    def key(self):
        return self.__key

    def _get_layout(self):
        new_layout = self._previews.get(self.key)
        return new_layout.layout if new_layout else None

    @property
    def _previews(self):
        return self._previews_storage.previews

    def make_layout(self, layout: Callable[[], list[list]]):
        return [
            [get_preview_layout_frame(layout, self.key or "")],
        ]

    def _set_layout(self, layout: LayoutProvider):
        window = sg.Window(
            f"External Python Simple Preview for {self.key}",
            self.make_layout(layout),
            keep_on_top=True,
            location=self._position.location,
            size=self._position.size,
            resizable=True,
            finalize=True,
            alpha_channel=0.0,
        )
        super()._set_window(window)


class PreviewSettingsWindowController(BaseController):
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._previews_storage = PreviewsStorage.get()
        self._external_windows: dict[str, ExternalPreviewWindowController] = dict()
        self._previous_key = None

    def open_external(self, name: str):
        if name in self._external_windows or not name:
            return
        controller = ExternalPreviewWindowController(name)
        self._external_windows[name] = controller
        controller.refresh_layout()

    def close_external(self, name: str):
        controller = self._external_windows.get(name)
        if not controller:
            return
        controller._handle_event(None, None)
        del self._external_windows[name]

    def _get_layout(self):
        changed = False
        if not self._previews.get_group(self._config.last_preview_group_key):
            self._config.last_preview_group_key = None
            changed = True
        if self._config.last_preview_key not in self._previews.get_group(self._config.last_preview_group_key):
            self._config.last_preview_key = self._previews.first_preview_key(self._config.last_preview_group_key)
            changed = True
        if changed:
            self._configs_storage.save(False)
        new_layout = self._previews.get(self._config.last_preview_key)
        return new_layout.layout if new_layout else None

    @property
    def _previews(self):
        return self._previews_storage.previews

    def make_layout(self, layout: Callable[[], list[list]]):
        config = map_config_to_view(self._config)
        names = tuple()
        previews = self._previews.get_group(self._config.last_preview_group_key)
        if previews and config.preview_key and \
                self._config.last_preview_key in previews:
            names = shorten_preview_names(previews)
            name = names[previews.index(self._config.last_preview_key)]
            config.preview_key.name = name
        settings_layout = get_settings_layout(
            config,
            ListItem.wrap_map(zip(previews, names)),
            ("*",) + self._previews.groups
        )
        if self._config.integrated_preview:
            settings_layout += [[
                get_preview_layout_frame(layout, self._config.last_preview_key or "")
            ]]
        return settings_layout

    def _set_layout(self, layout: LayoutProvider):
        if self._config.theme:
            sg.theme(self._config.theme)
        window = sg.Window(
            "Python Simple Preview",
            self.make_layout(layout),
            keep_on_top=True,
            location=self._position.location,
            size=self._position.size,
            resizable=True,
            finalize=True,
            alpha_channel=0.0,
        )
        super()._set_window(window)
        self.open_external_preview()

    def open_external_preview(self):
        key = self._config.last_preview_key
        external = not self._config.integrated_preview
        if self._previous_key != key or not external:
            self.close_external(self._previous_key)
        if external:
            self.open_external(key)
        self._previous_key = key

    def step(self):
        super().step()
        for controller in self._external_windows.values():
            controller.step()

    def _handle_event(self, event, values):
        value = values.get(event) if values else None
        if event == "theme":
            self._config.theme = value
            self._configs_storage.save()
        elif event == "group":
            self._config.last_preview_group_key = (None if value == "*" else value)
            self._configs_storage.save()
        elif event == "project":
            self._config.current_project = Path(value)
            self._configs_storage.save()
        elif event == "reload_all":
            self._config.reload_all = value
            self._configs_storage.save()
        elif event == "integrated_preview":
            self._config.integrated_preview = not self._config.integrated_preview
            self._position = Position(
                None,
                self._position.location,
            )
            self._configs_storage.save()
        elif event == "new_project":
            new_project = self.get_project_path()
            if new_project:
                self._config.current_project = new_project
                self._config.projects += (new_project,)
                self._configs_storage.save()
        elif event == "preview":
            self._config.last_preview_key = value.value
            self._configs_storage.save()
        else:
            super()._handle_event(event, values)

    def get_project_path(self):
        old_project_dir = self._config.current_project or "."
        old_project_dir = os.path.dirname(str(old_project_dir))
        project_module = sg.popup_get_file(
            "Select root module (__init__), single .py module, or directory (select file, then edit path as text)",
            "Add new module/package", keep_on_top=True, initial_folder=old_project_dir,
            file_types=(("Python executable", "*.py"),)
        )
        if not project_module:
            return
        project_module = Path(project_module)
        if is_valid_project(project_module):
            return project_module

    def refresh_layout(self):
        super().refresh_layout()
        for controller in self._external_windows.values():
            controller.refresh_layout()
