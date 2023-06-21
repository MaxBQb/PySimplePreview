import inspect
from pathlib import Path
from typing import Callable

from src.PySimplePreview.domain.interactor.previews_manager import PreviewsManager, get_longest_module_name


class PreviewsStorage:
    _instance = None

    def __init__(self):
        self.previews = PreviewsManager()

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


def preview(preview_name: str = None, *args, **kwargs):
    f = None
    if preview_name is not None and not isinstance(preview_name, str):
        f = preview_name
        preview_name = None

    def get_layout(f: Callable[[...], list[list]]):
        module_path = Path(inspect.getfile(f))
        module_parents = get_longest_module_name(Path(module_path))
        qualname = f"{'.'.join(module_parents)}.{f.__qualname__}"

        PreviewsStorage.get().previews.add_preview(
            name=f"{qualname}:{preview_name}" if preview_name else qualname,
            layout_provider=lambda: f(*args, **kwargs),
            module_path=module_path
        )
        return f

    if f:
        return get_layout(f)
    return get_layout


