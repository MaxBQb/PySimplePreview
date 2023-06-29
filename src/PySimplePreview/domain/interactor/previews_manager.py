import inspect
import warnings
from pathlib import Path
from typing import Callable

from PySimplePreview.domain.model.preview import LayoutProvider, Preview


class PreviewsManager:
    NAME_SEP = ':'

    def __init__(self):
        self._previews: dict[str, Preview] = dict()
        self._groups: dict[str, set[str]] = dict()

    def get(self, key: str):
        return self._previews.get(key)

    def get_group(self, key: str):
        if key is None:
            return self.previews or tuple()
        return tuple(self._groups.get(key, set()))

    def clear(self):
        self._previews.clear()
        self._groups.clear()

    def remove_module(self, path: Path):
        keys = [key for key, preview in self._previews.items()
                if preview.path.samefile(path)]
        for key in keys:
            del self._previews[key]

    def add_preview(
        self,
        name: str,
        module_path: Path,
        layout_provider: LayoutProvider,
        group_name: str = None,
    ):
        if (not module_path.exists() or
                not module_path.is_file() or
                module_path.suffix != ".py"):
            raise ValueError("No python module found")
        preview = Preview(module_path, layout_provider)
        if name in self._previews:
            old_preview = self._previews[name]
            if old_preview.creation_time == preview.creation_time:
                warnings.warn(f"Preview with key '{name}' already exists! (overwrite applied)")
        self._previews[name] = preview
        if group_name:
            self._groups.setdefault(group_name, set())
            self._groups[group_name].add(name)

    @property
    def previews(self):
        return tuple(self._previews.keys())

    @property
    def names(self):
        return [self.name_of(key) for key in self._previews]

    @property
    def groups(self):
        return tuple(self._groups.keys())

    def first_preview_key(self, group_key=None):
        return next(iter(self.get_group(group_key)), None)

    @property
    def first_preview(self):
        return self._previews.get(self.first_preview_key())

    @staticmethod
    def split_name(key):
        return key.split(PreviewsManager.NAME_SEP, 1)

    @staticmethod
    def name_of(key):
        return PreviewsManager.split_name(key)[-1]

    @staticmethod
    def key_of(key):
        return PreviewsManager.split_name(key)[0]


def get_longest_module_name(path: Path):
    if path.is_file():
        yield from get_longest_module_name(path.parent)
        yield inspect.getmodulename(str(path))
    else:
        if path.joinpath("__init__.py").exists():
            yield from get_longest_module_name(path.parent)
            yield path.name


def get_qualified_name(func: Callable, module_path: Path, name: str = None):
    module_parents = get_longest_module_name(module_path)
    qualname = f"{'.'.join(module_parents)}.{func.__qualname__}"
    return f"{qualname}:{name}" if name else qualname
