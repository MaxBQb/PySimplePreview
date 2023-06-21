from src.PySimplePreview.domain.model.config import Config


class ConfigStorage:
    _instance = None

    def __init__(self):
        self.config = Config()

    def save(self):
        pass

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

