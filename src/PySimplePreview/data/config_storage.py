import logging
from copy import deepcopy
from typing import Callable

import jsons

from PySimplePreview.domain.model.config import Config
from PySimplePreview.domain.model.event import InvokableEvent


class ConfigStorage:
    def __init__(self, filename: str = 'config.json'):
        self._config = None
        self.filename = filename
        self._on_update = InvokableEvent[Callable[[Config], None]]()
        self.on_update = self._on_update.base
        self._positions = None

    @property
    def positions(self):
        if self.config.remember_positions:
            return self.config.positions
        if not self._positions:
            self._positions = deepcopy(self.config.positions)
        return self._positions

    def dump_positions(self):
        if self._positions:
            self.config.positions = self._positions

    @property
    def config(self) -> Config:
        if self._config is None:
            self.load()
        return self._config

    def load(self):
        try:
            self._config = Config()
            with open(self.filename, 'r', encoding='utf-8-sig') as file:
                self._config = jsons.loads(file.read(), Config)
        except (OSError, jsons.DeserializationError) as e:
            logging.exception(
                "Load config failed, "
                "file will be overwritten with latest loaded version...",
                exc_info=e
            )
            self.save(False)

    def save(self, dispatch_changes=True):
        with open(self.filename, 'w', encoding='utf-8-sig') as file:
            file.write(jsons.dumps(self._config or Config(), strip_nulls=True, jdkwargs=dict(indent=2)))
        if dispatch_changes:
            self._on_update.invoke(self._config)
