from dataclasses import dataclass
from typing import Iterable, Any

import PySimpleGUI as sg

from src.PySimplePreview.domain.interactor.previews_manager import PreviewsManager
from src.PySimplePreview.domain.model.config import Config


class ListItem:
    def __init__(self, value, name: str = None):
        self.value = value
        self.name = name if name is not None else str(value)

    def __str__(self):
        return self.name

    @classmethod
    def wrap_map(cls, values: Iterable[tuple[Any, str]]):
        return [cls(value, name) for value, name in values]


@dataclass
class ConfigViewDTO:
    preview_key: ListItem = None
    theme: str = None


def map_config_to_view(config: Config):
    return ConfigViewDTO(
        preview_key=ListItem(config.last_preview_key, PreviewsManager.name_of(config.last_preview_key))
        if config.last_preview_key else None,
        theme=config.theme or sg.CURRENT_LOOK_AND_FEEL,
    )
