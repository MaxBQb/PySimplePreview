from src.PySimplePreview.domain.interactor.previews_manager import PreviewsManager


class PreviewsStorage:
    _instance = None

    def __init__(self):
        self.previews = PreviewsManager()

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
