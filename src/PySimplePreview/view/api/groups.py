import inspect
from pathlib import Path

from PySimplePreview.domain.interactor.previews_manager import get_qualified_name
from PySimplePreview.view.api.preview import LAYOUT_HOLDER


def _group_previews(group_name: str = None):
    def wrapper(f):
        f.preview_group_name = group_name or get_qualified_name(f, Path(inspect.getfile(f)))
        return f
    return wrapper


def group_previews(group_name: str = None):
    if group_name is None or isinstance(group_name, str):
        return _group_previews(group_name)
    return _group_previews()(group_name)
