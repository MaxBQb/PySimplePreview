from PySimplePreview.domain.interactor.previews_manager import PreviewsManager


class PreviewsStorage:
    def __init__(self, previews: PreviewsManager):
        self.previews = previews
        self.__class__._instance = self
