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
        self._updates_listeners = set()

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
            print("Error occurred while loading config:", e)
            print("Override with latest correct version...")
            self.save(False)

    def save(self, dispatch_changes=True):
        with open(self.filename, 'w', encoding='utf-8-sig') as file:
            file.write(jsons.dumps(self._config or Config(), strip_nulls=True, jdkwargs=dict(indent=2)))
        if dispatch_changes:
            self._on_update.invoke(self._config)
