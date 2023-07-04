import punq

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.model.config import Config


def register_data(container: punq.Container):
    container.register(PreviewsStorage, scope=punq.Scope.singleton)
    container.register(ConfigStorage, scope=punq.Scope.singleton)
    container.register(Config, factory=lambda: container.resolve(ConfigStorage).config)
