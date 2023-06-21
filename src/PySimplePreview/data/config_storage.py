import jsons

from src.PySimplePreview.domain.model.config import Config


class ConfigStorage:
    _instance = None

    def __init__(self, filename: str = 'config.json'):
        self._config = None
        self.filename = filename

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
        except (OSError, jsons.DeserializationError):
            self.save()

    def save(self):
        with open(self.filename, 'w', encoding='utf-8-sig') as file:
            file.write(jsons.dumps(self._config or Config(), jdkwargs=dict(indent=2)))

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

