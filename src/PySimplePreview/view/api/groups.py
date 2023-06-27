import inspect
from pathlib import Path
from typing import Callable

from PySimplePreview.domain.interactor.previews_manager import get_qualified_name


def group_previews(group_name: str = None):
    """
    | Set default value of **preview_group_name** parameter for all **@preview**'s above it
    | Use this on functions with multiple previews applied
    | No-params form can be called without parentheses

    :param group_name: Custom previews group name, if nothing presented function name used
    :return: Returns wrapper, which will return same function as was consumed
    """
    func = None
    if group_name:
        if not isinstance(group_name, str):
            func = group_name
            group_name = None

    def wrapper(f: Callable[[...], list[list]]) -> Callable[[...], list[list]]:
        f.preview_group_name = group_name or get_qualified_name(f, Path(inspect.getfile(f)))
        return f

    if func:
        return wrapper(func)
    return wrapper
