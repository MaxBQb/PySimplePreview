import os
from pathlib import Path
from typing import Callable

import PySimpleGUI as sg

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.interactor.abc.files_observer import ProjectObserver
from PySimplePreview.domain.model.config import is_valid_project
from PySimplePreview.domain.model.event import Listener
from PySimplePreview.domain.model.position import Position
from PySimplePreview.domain.model.preview import LAYOUT_PROVIDER
from PySimplePreview.view.contracts import SettingsEvents
from PySimplePreview.view.controller.base import BaseController
from PySimplePreview.view.controller.external_preview_factory import ExternalPreviewWindowControllerFactory
from PySimplePreview.view.layouts import get_settings_layout, get_preview_layout_frame
from PySimplePreview.view.models import map_config_to_view, shorten_preview_names, ListItem


class PreviewSettingsWindowController(BaseController):
    def __init__(
        self,
        config: ConfigStorage,
        previews_storage: PreviewsStorage,
        project_observer: ProjectObserver,
        external_previews_factory: ExternalPreviewWindowControllerFactory,
    ):
        super().__init__(config)
        self._previews_storage = previews_storage
        self._external_previews_factory = external_previews_factory
        config.on_update += self._on_config_update
        project_observer.on_project_update += Listener(
            lambda _, __: self.refresh_layout(),
            Listener.Priority.Lowest,
        )
        self._position_controller.other_key += "Minimized"

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

        if not self._check_preview_integrated(self._config.last_preview_key):
            config.integrated_preview_disabled = True
            config.integrated_preview = False

        settings_layout = get_settings_layout(
            config,
            ListItem.wrap_map(zip(previews, names)),
            ("*",) + self._previews.groups
        )
        if self._is_preview_integrated:
            settings_layout += [[
                get_preview_layout_frame(layout, self._config.last_preview_key or "")
            ]]
        return settings_layout

    def _set_layout(self, layout: LAYOUT_PROVIDER):
        if self._config.theme:
            sg.theme(self._config.theme)
        self._position_controller.use_other = not self._is_preview_integrated
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
        if self._is_preview_integrated:
            self._external_previews_factory.remove()
        else:
            self._external_previews_factory.create(key)

    @property
    def _is_preview_integrated(self):
        integrated = self._config.integrated_preview
        if not integrated:
            return False
        return self._check_preview_integrated(self._config.last_preview_key)

    def _check_preview_integrated(self, key: str | None):
        if not key:
            return True
        preview = self._previews.get(key)
        if not preview or preview.internal:
            return True
        return False

    def step(self):
        super().step()
        for controller in self._external_previews_factory.values:
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

    def _refresh_size(self):
        self._position = Position(
            None,
            self._position.location,
        )

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
        for controller in self._external_previews_factory.values:
            controller.refresh_layout()
