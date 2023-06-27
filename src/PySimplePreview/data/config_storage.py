from typing import Callable

import jsons

from src.PySimplePreview.domain.model.config import Config


class ConfigStorage:
    _instance = None

    def __init__(self, filename: str = 'config.json'):
        self._config = None
        self.filename = filename
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
            for action in self._updates_listeners:
                action(self._config)

    def on_update(self, action: Callable[[Config], None]):
        self._updates_listeners.add(action)

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

