
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any, Sequence

import PySimpleGUI as sg

from PySimplePreview.domain.interactor.previews_manager import PreviewsManager
from PySimplePreview.domain.model.config import Config, is_package_project


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
    last_preview_group_key: str = "*"
    current_project: str = None
    is_package: bool = None
    reload_all: bool = False
    projects: tuple[str, ...] = tuple()
    theme: str = None


def map_config_to_view(config: Config):
    return ConfigViewDTO(
        preview_key=ListItem(config.last_preview_key, PreviewsManager.name_of(config.last_preview_key))
        if config.last_preview_key else None,
        projects=tuple(str(x) for x in config.projects),
        current_project=str(config.current_project) if config.current_project else None,
        theme=config.theme or sg.CURRENT_LOOK_AND_FEEL,
        reload_all=config.reload_all,
        last_preview_group_key=config.last_preview_group_key or "*",
        is_package=is_package_project(Path(config.current_project)) if config.current_project else None
    )


def shorten_preview_names(keys: Iterable[str]):
    """
    | Map **keys** to their shortest possible aliases:
    | **package.module.function_name:preview_name -> preview_name**
    | **package.module.function_name -> function_name**

    | Name collision is resolved by fallback to longer version:
    | **package.module.function_name -> module.function_name**
    | **package.other_module.function_name -> other_module.function_name**

    :param keys: Preview keys, likely in format ('package.module.function_name',
        'package.module.function_name:preview_name', ...)
    :return: Tuple of the shortest possible aliases
    """
    source = [_shorten_preview_name(key) for key in keys]
    result = [next(generator) for generator in source]
    indexes = set()
    while indexes := _find_not_uniq(result, indexes):
        for i in indexes:
            result[i] = next(source[i])
    return tuple(result)


def _find_not_uniq(array: Sequence, indexes: set = None):
    indexes = indexes or set()
    first_entries = {}
    sequence = ((i, array[i]) for i in indexes) if indexes else enumerate(array)
    indexes = set()
    for i, element in sequence:
        if element in first_entries:
            indexes.add(first_entries[element])
            indexes.add(i)
        else:
            first_entries[element] = i
    return indexes


def _shorten_preview_name(key: str):
    name_only = PreviewsManager.name_of(key)
    if name_only != key:
        yield name_only
    tokens = key.split('.')
    result = ""
    for token in reversed(tokens):
        result = f"{token}.{result}" if result else token
        yield result
