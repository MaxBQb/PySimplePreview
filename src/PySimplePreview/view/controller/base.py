import logging
import time
from abc import ABCMeta, abstractmethod
from queue import Queue

import PySimpleGUI as sg

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.model.config import Config
from PySimplePreview.domain.model.position import Position, PositionWithFallback
from PySimplePreview.domain.model.preview import LAYOUT_PROVIDER
from PySimplePreview.view.controller.utils import WindowHolder
from PySimplePreview.view.layouts import get_nocontent_layout
from PySimplePreview.view.models import PositionViewDTO


class BaseController(metaclass=ABCMeta):
    def __init__(self, config: ConfigStorage):
        self._configs_storage = config
        self._window_holder = WindowHolder()
        self._position_controller = PositionWithFallback(
            lambda key: config.positions.get(key, None),
            lambda key, value: config.positions.__setitem__(key, value),
            self.name,
            self.name,
            use_other=False
        )
        self.queue = Queue()

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
            logging.exception(f"Error in controller '{self.name}'", exc_info=e)
            time.sleep(1)

    @property
    def _position(self):
        return PositionViewDTO.from_domain(self._position_controller.position)

    @_position.setter
    def _position(self, value: Position):
        self._position_controller.position = value
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
    def layout(self) -> LAYOUT_PROVIDER | None:
        return self._get_layout()

    @layout.setter
    def layout(self, value: LAYOUT_PROVIDER):
        self.queue.put_nowait(value)

    def _set_window(self, window: sg.Window):
        window.bind('<Configure>', "Configure")
        self._window_holder.swap(window)

    @property
    def _config(self):
        return self._configs_storage.config
