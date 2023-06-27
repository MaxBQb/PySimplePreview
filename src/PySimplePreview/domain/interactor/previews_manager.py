import inspect
import warnings
from pathlib import Path

from PySimplePreview.domain.model.preview import LayoutProvider, Preview


class PreviewsManager:
    NAME_SEP = ':'

    def __init__(self):
        self._previews: dict[str, Preview] = dict()

    def get(self, key: str):
        return self._previews.get(key)

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

    @property
    def previews(self):
        return list(self._previews.keys())

    @property
    def names(self):
        return [self.name_of(key) for key in self._previews]

    @property
    def first_preview_key(self):
        return next(iter(self._previews.keys()), None)

    @property
    def first_preview(self):
        return self._previews.get(self.first_preview_key)

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
