import time
from abc import ABCMeta, abstractmethod
from queue import Queue

import PySimpleGUI as sg

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.model.config import Config
from PySimplePreview.domain.model.position import Position
from PySimplePreview.domain.model.preview import LayoutProvider
from PySimplePreview.view.controller.utils import WindowHolder
from PySimplePreview.view.layouts import get_nocontent_layout
from PySimplePreview.view.models import PositionViewDTO


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
