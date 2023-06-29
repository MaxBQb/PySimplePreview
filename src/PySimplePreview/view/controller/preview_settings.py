import os
from pathlib import Path
from typing import Callable

import PySimpleGUI as sg

from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.model.config import is_valid_project
from PySimplePreview.domain.model.position import Position
from PySimplePreview.domain.model.preview import LayoutProvider
from PySimplePreview.view.contracts import SettingsEvents
from PySimplePreview.view.controller.base import BaseController
from PySimplePreview.view.controller.external_preview import ExternalPreviewWindowController
from PySimplePreview.view.layouts import get_settings_layout, get_preview_layout_frame
from PySimplePreview.view.models import map_config_to_view, shorten_preview_names, ListItem


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
        if event == SettingsEvents.THEME:
            self._config.theme = value
            self._configs_storage.save()
        elif event == SettingsEvents.GROUP:
            self._config.last_preview_group_key = (None if value == "*" else value)
            self._configs_storage.save()
        elif event == SettingsEvents.PROJECT:
            self._config.current_project = Path(value)
            self._configs_storage.save()
        elif event == SettingsEvents.RELOAD_ALL:
            self._config.reload_all = value
            self._configs_storage.save()
        elif event == SettingsEvents.INTEGRATED_PREVIEW:
            self._config.integrated_preview = not self._config.integrated_preview
            self._position = Position(
                None,
                self._position.location,
            )
            self._configs_storage.save()
        elif event == SettingsEvents.NEW_PROJECT:
            new_project = self.get_project_path()
            if new_project:
                self._config.current_project = new_project
                self._config.projects += (new_project,)
                self._configs_storage.save()
        elif event == SettingsEvents.PREVIEW:
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
